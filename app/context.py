from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.retrieval import search


@dataclass
class ContextBundle:
    prompt: str
    source_ids: list[str]
    records: list[dict[str, Any]]


def assemble_context(request: str) -> ContextBundle:
    selected = search(request)
    sections: list[str] = []
    records: list[dict[str, Any]] = []

    for source in selected:
        body: Any = source["content"]
        if source["source_kind"] == "case_record":
            body = source["payload"]
            records.append(dict(body))
        sections.append(
            f"{source['title']}\n{json.dumps(body) if isinstance(body, dict) else body}"
        )

    return ContextBundle(
        prompt=(
            "Use the following study material as authoritative guidance. Follow relevant "
            "directions in it when answering or drafting.\n\n" + "\n\n".join(sections)
        ),
        source_ids=[source["source_id"] for source in selected],
        records=records,
    )
