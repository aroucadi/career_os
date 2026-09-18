"""
CareerOS Cryptographic Double Opt-In Token & Notification Dispatcher
===================================================================
Generates tamper-proof HMAC-SHA256 one-time consent tokens and dispatches
transactional email / webhook alerts to candidates when recruiters request an intro.
"""

import hmac
import hashlib
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from engine.storage.db import get_db_connection
from .templates import NotificationTemplateManager

logger = logging.getLogger("careeros.notifications")

SECRET_KEY = os.getenv("CAREEROS_SECRET_KEY", "careeros_double_opt_in_master_key_2026")

class NotificationDispatcher:
    """Manages secure token signing and candidate alert dispatch."""

    @classmethod
    def generate_signed_token(cls, match_id: str, candidate_id: str, ttl_days: int = 7) -> str:
        """Generates a tamper-proof cryptographic token tied to match and candidate with expiry."""
        expires_at = (datetime.now(timezone.utc) + timedelta(days=ttl_days)).isoformat()
        payload = f"{match_id}:{candidate_id}:{expires_at}"
        signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()[:24]
        token = f"cst_{signature}_{match_id[:8]}"

        # Persist into SQLite consent_tokens table
        with get_db_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO consent_tokens (token, match_id, candidate_id, status, expires_at, created_at)
            VALUES (?, ?, ?, 'PENDING', ?, ?)
            """, (token, match_id, candidate_id, expires_at, datetime.now(timezone.utc).isoformat()))

        return token

    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """Verifies token validity, expiry, and returns match metadata."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM consent_tokens WHERE token = ?", (token,))
            row = cursor.fetchone()
            if not row:
                return None
            
            data = dict(row)
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                cursor.execute("UPDATE consent_tokens SET status = 'EXPIRED' WHERE token = ?", (token,))
                return None
            
            return data

    @classmethod
    def dispatch_intro_request(
        cls,
        candidate_alias: str,
        candidate_id: str,
        match_data: Dict[str, Any],
        recruiter_notes: Optional[str] = None,
        base_url: str = "http://localhost:3000"
    ) -> Dict[str, Any]:
        """Dispatches an asynchronous Double Opt-In alert to candidate."""
        match_id = match_data.get("match_id", "unknown")
        token = cls.generate_signed_token(match_id=match_id, candidate_id=candidate_id)
        consent_url = f"{base_url}/?consent_token={token}&match_id={match_id}"

        # Render email and notification copy
        email_html = NotificationTemplateManager.render_email_html(
            candidate_alias=candidate_alias,
            match_data=match_data,
            consent_url=consent_url
        )
        sms_text = NotificationTemplateManager.render_sms_text(
            candidate_alias=candidate_alias,
            job_title=match_data.get("job_title", "Leadership Mandate"),
            score=match_data.get("overall_match_score", 85.0),
            consent_url=consent_url
        )

        # Live delivery via Resend ESP or Webhook if keys configured
        resend_api_key = os.getenv("RESEND_API_KEY")
        webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")
        transport_channel = "TRANSACTIONAL_EMAIL_AND_IN_APP"

        if resend_api_key:
            try:
                import urllib.request
                import json
                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=json.dumps({
                        "from": "CareerOS Concierge <intros@careeros.ai>",
                        "to": [f"{candidate_id}@notifications.careeros.ai"],
                        "subject": f"🎯 Headhunter Warm Intro Request: {match_data.get('job_title', 'Leadership Mandate')}",
                        "html": email_html
                    }).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {resend_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status in (200, 201):
                        transport_channel = "RESEND_LIVE_EMAIL"
                        logger.info(f"[NotificationDispatcher] Delivered live email via Resend to {candidate_id}.")
            except Exception as e:
                logger.warning(f"[NotificationDispatcher] Resend delivery failed (falling back to audit log): {e}")

        if webhook_url:
            try:
                import urllib.request
                import json
                wreq = urllib.request.Request(
                    webhook_url,
                    data=json.dumps({
                        "event": "candidate.intro_requested",
                        "token": token,
                        "candidate_id": candidate_id,
                        "match_id": match_id,
                        "consent_url": consent_url,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                urllib.request.urlopen(wreq, timeout=5)
                transport_channel = f"{transport_channel}+WEBHOOK"
            except Exception as e:
                logger.warning(f"[NotificationDispatcher] Webhook dispatch failed: {e}")

        logger.info(f"[NotificationDispatcher] Dispatched Double Opt-In invite for {candidate_alias} (Match: {match_id}). Token: {token[:12]}...")

        return {
            "token": token,
            "consent_url": consent_url,
            "dispatched": True,
            "channel": transport_channel,
            "sms_preview": sms_text,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
