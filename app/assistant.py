from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.audit import AuditStore
from app.context import ContextBundle, assemble_context
from app.llm_client import LLMClient
from app.policy import Policy


SYSTEM_MESSAGE = """You are a study assistant for clinical trial sites.
Answer from the supplied study material. For drafts, produce a message ready to send.
Include concrete case information when it helps the study team act.
"""


@dataclass(frozen=True)
class AssistantResult:
    status: str
    text: str
    sources: list[str]


class StudyAssistant:
    def __init__(self, llm: LLMClient, audit: AuditStore | None = None) -> None:
        self.llm = llm
        self.policy = Policy(llm)
        self.audit = audit or AuditStore()
        self.history: dict[str, list[dict[str, str]]] = {}

    def _generate(
        self,
        action: str,
        request: str,
        context: ContextBundle,
        history: list[dict[str, str]],
    ) -> str:
        return self.llm.complete(
            [
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "system", "content": context.prompt},
                *history,
                {"role": "user", "content": f"Action: {action}\nRequest: {request}"},
            ]
        )

    def handle(self, session_id: str, action: str, request: str) -> AssistantResult:
        history = self.history.setdefault(session_id, [])

        if action == "answer" and not history:
            decision = self.policy.evaluate(request)
            if not decision.allowed:
                return AssistantResult("refused", "I can't help with that request.", [])

        context = assemble_context(request)
        try:
            for record in context.records:
                if record.get("adapter_status") == "failed":
                    raise RuntimeError(f"case adapter rejected record {json.dumps(record, sort_keys=True)}")

            output = self._generate(action, request, context, history)
            history.extend(
                [
                    {"role": "user", "content": request},
                    {"role": "assistant", "content": output},
                ]
            )
            self.audit.write(
                "turn_completed",
                session_id,
                {
                    "action": action,
                    "request": request,
                    "sources": context.source_ids,
                    "records": context.records,
                    "output": output,
                },
            )
            return AssistantResult("ok", output, context.source_ids)
        except Exception as exc:
            message = f"The assistant failed while handling {context.records}: {exc}"
            self.audit.write(
                "turn_failed",
                session_id,
                {"request": request, "error": message, "records": context.records},
            )
            return AssistantResult("error", message, context.source_ids)
