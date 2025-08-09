#!/usr/bin/env python3
"""
FreelanceX.AI Orchestrator
- Entry point for API calls to run the agentic workflow
- Uses MCP for kill switch/policy/audit
- Delegates routing to triage agent (multi-API aware)
"""

import logging
from typing import Any, Dict, Optional

from .mcp import get_mcp
from .triage_agent import route_request
from .api_provider import get_api_manager

logger = logging.getLogger(__name__)


async def run_orchestration(user_id: str, user_input: str, session: Optional[Any] = None) -> Dict[str, Any]:
    mcp = get_mcp()

    # Policy gate
    decision = mcp.authorize(user_id, {"input": user_input})
    if not decision.allowed:
        mcp.audit_event("policy_denied", {
            "user_id": user_id,
            "reason": decision.reason,
        })
        return {
            "success": False,
            "status": decision.status,
            "response": decision.reason,
        }

    mcp.audit_event("orchestration_start", {
        "user_id": user_id,
    })

    try:
        result = await route_request(user_input)
        # annotate cache hit from APIManager if used
        try:
            am = get_api_manager()
            result["cache_hit"] = am.was_last_cache_hit()
        except Exception:
            pass
        mcp.audit_event("orchestration_end", {
            "user_id": user_id,
            "success": True,
            "agent": result.get("agent_used"),
            "provider": result.get("provider"),
        })
        return result
    except Exception as e:
        logger.exception("Orchestration failed")
        mcp.audit_event("orchestration_error", {
            "user_id": user_id,
            "error": str(e),
        })
        return {
            "success": False,
            "response": f"Error: {e}",
        }


