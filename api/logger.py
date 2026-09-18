"""
CareerOS Structured Logging & Audit Telemetry
=============================================
Provides central rotating logging for debugging, LLM token tracing,
route resolution diagnostics, and JSONL audit persistence.
"""

import os
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

_ROOT_DIR = Path(__file__).resolve().parent.parent
_LOG_DIR = _ROOT_DIR / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_LOG_FILE = _LOG_DIR / "careeros_api.log"
_AUDIT_FILE = _LOG_DIR / "chat_audit.jsonl"

# 1. Main Application Logger
logger = logging.getLogger("careeros")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # Console handler
    c_handler = logging.StreamHandler()
    c_format = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", datefmt="%H:%M:%S")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # Rotating file handler (5MB max, 5 backups)
    f_handler = RotatingFileHandler(_LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    f_format = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s")
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

# 2. Audit Trail Logger for LLM & Chat Interactions
class AuditLogger:
    """Persists structured audit events to JSONL for offline evaluation and forensics."""

    @staticmethod
    def log_interaction(
        request_id: str,
        profile: str,
        user_message: str,
        route_taken: str,
        attachments: Optional[List[str]] = None,
        tool_calls: Optional[List[str]] = None,
        duration_ms: Optional[float] = None,
        llm_model: Optional[str] = None,
        status: str = "SUCCESS",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "profile": profile,
            "user_message": user_message[:500] if user_message else "",
            "attachments": attachments or [],
            "route_taken": route_taken,
            "tool_calls": tool_calls or [],
            "llm_model": llm_model,
            "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
            "status": status,
            "error": error
        }

        try:
            with open(_AUDIT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log record: {e}")

        return record

    @staticmethod
    def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
        """Reads the most recent audit records from disk."""
        if not _AUDIT_FILE.exists():
            return []
        try:
            lines = _AUDIT_FILE.read_text(encoding="utf-8").strip().splitlines()
            records = []
            for line in lines[-limit:]:
                if line.strip():
                    records.append(json.loads(line))
            records.reverse()
            return records
        except Exception as e:
            logger.error(f"Failed to read audit log records: {e}")
            return []
