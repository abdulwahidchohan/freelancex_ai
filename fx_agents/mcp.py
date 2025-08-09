#!/usr/bin/env python3
"""
Master Control Plane (MCP) for FreelanceX.AI
- Centralized kill-switch
- Policy checks (basic)
- Audit logging
"""

import os
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import get_config

logger = logging.getLogger(__name__)


class KillSwitch:
    """Global kill switch, backed by environment/config state."""

    def __init__(self):
        self._env_var = "FREELANCEX_KILL_SWITCH"
        self._cfg = get_config()

    def is_enabled(self) -> bool:
        value = os.getenv(self._env_var, "false").lower() in ("1", "true", "yes", "on")
        return bool(value)

    def enable(self):
        os.environ[self._env_var] = "true"

    def disable(self):
        os.environ[self._env_var] = "false"


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str = ""
    status: int = 200


class PolicyEngine:
    """Very basic policy checks; extendable for rate limits and PII rules."""

    def __init__(self):
        self._cfg = get_config()

    def check_request(self, user_id: str, payload: Dict[str, Any]) -> PolicyDecision:
        # Enforce minimal constraints
        text = (payload.get("input") or "")
        if not text:
            return PolicyDecision(allowed=False, reason="Empty input", status=400)
        if len(text) > 8000:
            return PolicyDecision(allowed=False, reason="Input too large", status=413)
        return PolicyDecision(allowed=True)


class AuditLogger:
    """Append-only audit log. Writes JSONL to logs/audit.log"""

    def __init__(self, log_dir: str = "logs"):
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        self._path = Path(log_dir) / "audit.log"

    def log(self, event_type: str, data: Dict[str, Any]):
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event_type,
            **data,
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


class MCP:
    """Master Control Plane facade"""

    def __init__(self):
        self.kill_switch = KillSwitch()
        self.policy = PolicyEngine()
        self.audit = AuditLogger()

    def authorize(self, user_id: str, payload: Dict[str, Any]) -> PolicyDecision:
        if self.kill_switch.is_enabled():
            return PolicyDecision(allowed=False, reason="System paused by kill switch", status=503)
        return self.policy.check_request(user_id, payload)

    def audit_event(self, event_type: str, data: Dict[str, Any]):
        try:
            self.audit.log(event_type, data)
        except Exception as e:
            logger.warning(f"Audit log failed: {e}")


_mcp: Optional[MCP] = None


def get_mcp() -> MCP:
    global _mcp
    if _mcp is None:
        _mcp = MCP()
    return _mcp



