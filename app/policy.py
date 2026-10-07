from __future__ import annotations

from dataclasses import dataclass

from app.llm_client import LLMClient


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


class Policy:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def evaluate(self, request: str) -> PolicyDecision:
        result = self.llm.complete_json(
            [
                {
                    "role": "system",
                    "content": (
                        "Decide whether a clinical trial assistant may answer the request. "
                        "Block requests for treatment advice not stated in the protocol and "
                        "requests for another site's participant data. Return JSON with an "
                        "allowed boolean and a short reason."
                    ),
                },
                {"role": "user", "content": request},
            ]
        )
        return PolicyDecision(bool(result.get("allowed")), str(result.get("reason", "")))
