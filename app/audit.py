from __future__ import annotations

import json
from typing import Any

from app.db import execute


class AuditStore:
    def write(self, event_type: str, session_id: str, details: dict[str, Any]) -> None:
        execute(
            "insert into audit_events(event_type, session_id, details) values (%s, %s, %s::jsonb)",
            (event_type, session_id, json.dumps(details)),
        )
