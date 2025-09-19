from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.crm_models import Deal, DealStatusEnum, ActivityLog

router = APIRouter(prefix="/ai", tags=["ai"])


# PUBLIC_INTERFACE
@router.get(
    "/lead-scoring",
    summary="AI Lead Scoring",
    description="Return simple heuristic lead scores per deal based on activities and amount. Placeholder for future ML.",
)
def lead_scoring(
    db: Session = Depends(get_db),
    account_id: Optional[int] = Query(default=None, description="Filter deals by account id"),
    top_n: int = Query(default=20, ge=1, le=200, description="Number of top leads to return"),
) -> List[Dict]:
    stmt = select(Deal)
    if account_id is not None:
        stmt = stmt.filter(Deal.account_id == account_id)
    stmt = stmt.filter(Deal.status == DealStatusEnum.OPEN).order_by(Deal.created_at.desc()).limit(500)
    deals = db.execute(stmt).scalars().all()

    # Basic heuristic: base on log count in last 60 days and normalized amount
    deal_ids = [d.id for d in deals]
    if not deal_ids:
        return []

    act_counts = dict(
        db.execute(
            select(ActivityLog.deal_id, func.count(ActivityLog.id))
            .where(ActivityLog.deal_id.in_(deal_ids))
            .group_by(ActivityLog.deal_id)
        ).all()
    )

    max_amount = max((d.amount or 0.0) for d in deals) or 1.0

    scored = []
    for d in deals:
        activity_score = min(1.0, act_counts.get(d.id, 0) / 10.0)
        amount_score = min(1.0, (d.amount or 0.0) / max_amount)
        # Probability use if provided
        prob_score = ((d.probability or 50.0) / 100.0)
        score = round(0.5 * activity_score + 0.3 * amount_score + 0.2 * prob_score, 4)
        scored.append(
            {
                "deal_id": d.id,
                "deal_name": d.name,
                "account_id": d.account_id,
                "amount": d.amount,
                "stage_id": d.stage_id,
                "probability": d.probability,
                "score": score,
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]


# PUBLIC_INTERFACE
@router.get(
    "/forecast",
    summary="AI Forecast",
    description="Return a naive revenue forecast by summing (amount * probability) for open deals.",
)
def forecast(
    db: Session = Depends(get_db),
    account_id: Optional[int] = Query(default=None, description="Filter by account id"),
) -> Dict:
    stmt = select(Deal).where(Deal.status == DealStatusEnum.OPEN)
    if account_id is not None:
        stmt = stmt.filter(Deal.account_id == account_id)
    deals = db.execute(stmt).scalars().all()

    total_pipeline = sum((d.amount or 0.0) for d in deals)
    weighted = sum((d.amount or 0.0) * ((d.probability or 50.0) / 100.0) for d in deals)
    count = len(deals)
    avg_prob = (sum((d.probability or 50.0) for d in deals) / count) if count else 0.0

    return {
        "open_deals": count,
        "pipeline_total": total_pipeline,
        "weighted_pipeline": round(weighted, 2),
        "avg_probability": round(avg_prob, 2),
    }


# PUBLIC_INTERFACE
@router.get(
    "/win-probability/{deal_id}",
    summary="AI Win Probability",
    description="Return a heuristic probability of winning for a specific deal.",
)
def win_probability(deal_id: int, db: Session = Depends(get_db)) -> Dict:
    d = db.get(Deal, deal_id)
    if not d:
        return {"deal_id": deal_id, "probability": None, "message": "Deal not found"}

    # Heuristic based on amount and activity volume relative to dataset
    act_count = db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.deal_id == deal_id)
    ).scalar_one()
    activity_factor = min(1.0, act_count / 10.0)
    amount_factor = 0.0 if not d.amount else min(1.0, d.amount / max(d.amount, 1.0))

    base = (d.probability or 50.0) / 100.0
    prob = round(min(0.95, max(0.05, 0.5 * base + 0.3 * activity_factor + 0.2 * amount_factor))), 2  # type: ignore
    # Fix rounding logic
    prob = round(min(0.95, max(0.05, 0.5 * base + 0.3 * activity_factor + 0.2 * amount_factor)), 2)

    return {"deal_id": deal_id, "probability": prob}
