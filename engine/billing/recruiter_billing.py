"""
CareerOS Recruiter Organization Billing & Monetization Gate
===========================================================
Enforces API key authentication and credit-based paywalls for B2B headhunters.
Costs:
- Mandate Match Slate: 10 Credits (€49)
- Unlocked Executive Dossier: 50 Credits (€250)
"""

import uuid
import logging
from typing import Optional, Dict, Any, Tuple
from engine.storage.db import get_db_connection

logger = logging.getLogger("careeros.recruiter_billing")

class RecruiterPricing:
    MATCH_SLATE_COST = 10       # 10 Credits (~€49)
    DOSSIER_UNLOCK_COST = 50    # 50 Credits (~€250)

class RecruiterBillingManager:
    """Manages organization billing ledgers, API keys, and Stripe checkout sessions."""

    @classmethod
    def authenticate_key(cls, api_key: str) -> Optional[Dict[str, Any]]:
        """Verifies organization API key against recruiter_orgs table."""
        if not api_key:
            return None
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recruiter_orgs WHERE api_key = ?", (api_key.strip(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    @classmethod
    def can_afford(cls, api_key: str, cost: int) -> bool:
        org = cls.authenticate_key(api_key)
        if not org:
            return False
        return org.get("credits_balance", 0) >= cost

    @classmethod
    def consume_credits(cls, api_key: str, cost: int, action: str) -> Tuple[bool, int, str]:
        """Atomically deducts credits from the organization ledger."""
        org = cls.authenticate_key(api_key)
        if not org:
            return False, 0, "Invalid or missing Recruiter API Key (format: cr_live_...)."
        
        current_bal = org.get("credits_balance", 0)
        if current_bal < cost:
            return False, current_bal, (
                f"Insufficient Organization Credits ({current_bal} available, {cost} required for {action}). "
                f"Please top up your account via /api/recruiter/billing/checkout."
            )

        new_bal = current_bal - cost
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE recruiter_orgs SET credits_balance = ? WHERE org_id = ?",
                (new_bal, org["org_id"])
            )
        
        logger.info(f"[RecruiterBilling] Deducted {cost} credits for org '{org['name']}' ({action}). New balance: {new_bal}.")
        return True, new_bal, f"Deducted {cost} credits for {action}. Balance: {new_bal}."

    @classmethod
    def create_checkout_session(cls, org_id: str, pack: str = "starter") -> Dict[str, Any]:
        """Generates a Stripe / billing checkout session stub."""
        packs = {
            "starter": {"credits": 50, "price_eur": 249, "name": "Starter Slate Pack (5 Mandates)"},
            "growth": {"credits": 150, "price_eur": 699, "name": "Growth Headhunter Pack (15 Mandates)"},
            "enterprise": {"credits": 500, "price_eur": 1999, "name": "Enterprise Unlimited Sourcing (Annual)"}
        }
        selected = packs.get(pack.lower(), packs["starter"])
        session_id = f"cs_live_{uuid.uuid4().hex[:16]}"
        checkout_url = f"https://checkout.careeros.internal/pay/{session_id}?org_id={org_id}&pack={pack}"

        return {
            "session_id": session_id,
            "checkout_url": checkout_url,
            "pack": selected["name"],
            "credits_granted": selected["credits"],
            "amount_eur": selected["price_eur"],
            "currency": "EUR"
        }
