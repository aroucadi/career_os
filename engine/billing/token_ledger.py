"""
CareerOS Anti-Burn Token Ledger Engine
======================================
Governs candidate Energy Credit (EC) quotas to prevent compute bankruptcy.
Enforces a 3-tier cost matrix:
- Tier 1: Local / Deterministic (0 EC)
- Tier 2: Low-Cost / Heuristic / Scan (5 EC)
- Tier 3: High-Cost LLM Synthesis / Tailoring (20-25 EC)
"""

import json
import logging
import threading
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("careeros.billing")

STORAGE_PATH = Path(__file__).resolve().parent.parent.parent / "storage" / "token_ledgers.json"
_ledger_lock = threading.Lock()

class ActionCost:
    DETERMINISTIC_CHECK = 0
    RADAR_SCAN = 5
    FAST_HEURISTIC_DEBATE = 5
    DEEP_LLM_DEBATE = 20
    TAILOR_RESUME = 25
    MOCK_INTERVIEW_TURN = 10
    GENERAL_CHAT_TURN = 1

    @classmethod
    def get_cost(cls, action: str) -> int:
        mapping = {
            "deterministic_check": cls.DETERMINISTIC_CHECK,
            "radar_scan": cls.RADAR_SCAN,
            "fast_heuristic_debate": cls.FAST_HEURISTIC_DEBATE,
            "deep_llm_debate": cls.DEEP_LLM_DEBATE,
            "tailor_resume": cls.TAILOR_RESUME,
            "mock_interview_turn": cls.MOCK_INTERVIEW_TURN,
            "general_chat_turn": cls.GENERAL_CHAT_TURN,
        }
        return mapping.get(action.lower(), cls.DETERMINISTIC_CHECK)


class LedgerTransaction(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    action: str
    amount: int
    balance_after: int
    details: str = ""


class TokenLedger(BaseModel):
    user_id: str
    balance_credits: int = 100
    max_credits: int = 100
    total_consumed: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    transactions: List[LedgerTransaction] = Field(default_factory=list)

    def can_afford(self, amount: int) -> bool:
        return self.balance_credits >= amount

    def deduct(self, amount: int, action: str, details: str = "") -> bool:
        if not self.can_afford(amount):
            return False
        self.balance_credits -= amount
        self.total_consumed += amount
        self.last_updated = datetime.now(timezone.utc).isoformat()
        self.transactions.append(LedgerTransaction(
            action=action,
            amount=-amount,
            balance_after=self.balance_credits,
            details=details
        ))
        return True

    def credit(self, amount: int, action: str, details: str = "") -> int:
        self.balance_credits = min(self.max_credits * 2, self.balance_credits + amount)
        self.last_updated = datetime.now(timezone.utc).isoformat()
        self.transactions.append(LedgerTransaction(
            action=action,
            amount=amount,
            balance_after=self.balance_credits,
            details=details
        ))
        return self.balance_credits


class TokenLedgerManager:
    """Manages persistent candidate token ledgers."""

    _ledgers: Dict[str, TokenLedger] = {}
    _loaded: bool = False

    @classmethod
    def _ensure_loaded(cls):
        with _ledger_lock:
            if cls._loaded:
                return
            STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            if STORAGE_PATH.exists():
                try:
                    with open(STORAGE_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cls._ledgers = {k: TokenLedger.model_validate(v) for k, v in data.items()}
                except Exception as e:
                    logger.error(f"Failed to load token ledgers: {e}")
                    cls._ledgers = {}
            cls._loaded = True

    @classmethod
    def _save(cls):
        try:
            STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            temp_file = STORAGE_PATH.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump({k: v.model_dump() for k, v in cls._ledgers.items()}, f, indent=2)
            shutil.move(str(temp_file), str(STORAGE_PATH))
        except Exception as e:
            logger.error(f"Failed to persist token ledgers: {e}")

    @classmethod
    def get_ledger(cls, user_id: Optional[str] = None) -> TokenLedger:
        cls._ensure_loaded()
        uid = (user_id or "default_user").strip()
        with _ledger_lock:
            if uid not in cls._ledgers:
                cls._ledgers[uid] = TokenLedger(user_id=uid)
                cls._save()
            return cls._ledgers[uid]

    @classmethod
    def can_afford(cls, user_id: Optional[str], action: str) -> bool:
        cost = ActionCost.get_cost(action)
        if cost == 0:
            return True
        ledger = cls.get_ledger(user_id)
        return ledger.can_afford(cost)

    @classmethod
    def consume(cls, user_id: Optional[str], action: str, details: str = "") -> Tuple[bool, int, str]:
        """
        Attempts to consume credits for a given action.
        Returns: (success: bool, remaining_balance: int, message: str)
        """
        cls._ensure_loaded()
        uid = (user_id or "default_user").strip()
        cost = ActionCost.get_cost(action)

        with _ledger_lock:
            if uid not in cls._ledgers:
                cls._ledgers[uid] = TokenLedger(user_id=uid)
            ledger = cls._ledgers[uid]

            if cost == 0:
                return True, ledger.balance_credits, f"Action '{action}' is deterministic and costs 0 EC."

            if not ledger.can_afford(cost):
                return False, ledger.balance_credits, (
                    f"Insufficient Energy Credits ({ledger.balance_credits} EC available, {cost} EC required for {action}). "
                    f"Deterministic checks remain active at 0 EC."
                )

            ledger.deduct(cost, action, details)
            cls._save()
            logger.info(f"[TokenLedger] Deducted {cost} EC for user '{uid}' ({action}). New balance: {ledger.balance_credits} EC.")
            return True, ledger.balance_credits, f"Consumed {cost} EC for {action}. Balance: {ledger.balance_credits} EC."

    @classmethod
    def award_bonus(cls, user_id: Optional[str], amount: int, reason: str = "Bonus") -> int:
        cls._ensure_loaded()
        uid = (user_id or "default_user").strip()
        with _ledger_lock:
            if uid not in cls._ledgers:
                cls._ledgers[uid] = TokenLedger(user_id=uid)
            ledger = cls._ledgers[uid]
            ledger.credit(amount, "BONUS", reason)
            cls._save()
            logger.info(f"[TokenLedger] Awarded {amount} EC to '{uid}' ({reason}). Balance: {ledger.balance_credits} EC.")
            return ledger.balance_credits

    @classmethod
    def get_cost_matrix(cls) -> Dict[str, int]:
        return {
            "deterministic_check": ActionCost.DETERMINISTIC_CHECK,
            "radar_scan": ActionCost.RADAR_SCAN,
            "fast_heuristic_debate": ActionCost.FAST_HEURISTIC_DEBATE,
            "deep_llm_debate": ActionCost.DEEP_LLM_DEBATE,
            "tailor_resume": ActionCost.TAILOR_RESUME,
            "mock_interview_turn": ActionCost.MOCK_INTERVIEW_TURN,
        }
