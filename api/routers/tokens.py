"""
CareerOS Token & Talent Intelligence Lake Router
================================================
Exposes energy credit balances, daily claim check-ins, and anonymized talent lake queries.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

from engine.billing.token_ledger import TokenLedgerManager
from engine.talent_graph.store import TalentLakeStore
from engine.talent_graph.models import TalentGraphProfile

router = APIRouter(prefix="/api/tokens", tags=["tokens"])

class TokenBalanceResponse(BaseModel):
    user_id: str
    balance_credits: int
    max_credits: int
    total_consumed: int
    cost_matrix: Dict[str, int]

class ClaimResponse(BaseModel):
    user_id: str
    new_balance: int
    message: str

@router.get("/balance", response_model=TokenBalanceResponse)
async def get_token_balance(user_id: Optional[str] = Query("alaa_roucadi")):
    """Returns current Energy Credit balance and cost matrix."""
    ledger = TokenLedgerManager.get_ledger(user_id)
    return TokenBalanceResponse(
        user_id=ledger.user_id,
        balance_credits=ledger.balance_credits,
        max_credits=ledger.max_credits,
        total_consumed=ledger.total_consumed,
        cost_matrix=TokenLedgerManager.get_cost_matrix()
    )

@router.post("/claim-daily", response_model=ClaimResponse)
async def claim_daily_credits(user_id: Optional[str] = Query("alaa_roucadi")):
    """Awards daily login bonus (+10 EC)."""
    new_bal = TokenLedgerManager.award_bonus(user_id, amount=10, reason="Daily Active Check-in")
    return ClaimResponse(
        user_id=user_id or "default_user",
        new_balance=new_bal,
        message="Claimed +10 Energy Credits successfully."
    )

@router.get("/talent-lake", response_model=List[TalentGraphProfile])
async def get_anonymized_talent_lake(governance_tag: Optional[str] = Query(None)):
    """Returns the anonymized candidate intelligence lake without exposing PII."""
    return TalentLakeStore.list_profiles(governance_tag=governance_tag)
