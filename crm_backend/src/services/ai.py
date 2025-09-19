from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from src.db.models import Contact, Deal, PipelineStage, DealStageStatus


class AIService:
    """
    Lightweight heuristic-based AI service. Replace with ML models later.
    """

    def score_lead(self, db: Session, contact_id: int) -> float:
        """
        Heuristic lead score [0, 100].
        """
        contact = db.get(Contact, contact_id)
        if not contact:
            raise ValueError("Contact not found")

        score = 30.0
        if contact.title:
            title = contact.title.lower()
            if any(k in title for k in ["chief", "head", "director", "vp"]):
                score += 10.0

        if contact.phone and contact.email:
            score += 15.0

        activities = len(contact.activities or [])
        score += min(activities * 5.0, 25.0)

        stmt = (
            select(func.sum(Deal.amount))
            .where(Deal.contact_id == contact_id)
            .where(Deal.status == DealStageStatus.open)
        )
        total_amount = db.execute(stmt).scalar() or 0.0
        if total_amount > 0:
            import math
            score += min(20.0, 10.0 * math.log10(1 + total_amount / 1000.0))

        return float(max(0.0, min(100.0, score)))

    def win_probability(self, db: Session, deal_id: int) -> float:
        """
        Estimate win probability using stage baseline and simple adjustments.
        """
        deal = db.get(Deal, deal_id)
        if not deal:
            raise ValueError("Deal not found")
        stage = db.get(PipelineStage, deal.stage_id)
        base_prob = (stage.probability if stage else 0.2) or 0.2

        # median amount heuristic per pipeline (best effort)
        try:
            stmt = select(func.percentile_cont(0.5).within_group(Deal.amount)).where(Deal.pipeline_id == deal.pipeline_id)
            median_amount = db.execute(stmt).scalar()
        except Exception:
            median_amount = None

        prob = base_prob
        if median_amount is not None and deal.amount is not None and deal.amount <= median_amount:
            prob += 0.05

        try:
            from datetime import date
            if deal.close_date:
                days = (deal.close_date - date.today()).days
                if 0 <= days <= 14:
                    prob += 0.05
        except Exception:
            pass

        return float(max(0.0, min(1.0, prob)))

    def forecast(self, db: Session, pipeline_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Simple forecast aggregations.
        """
        stmt = select(Deal.id, Deal.amount, Deal.stage_id).where(Deal.status == DealStageStatus.open)
        if pipeline_id:
            stmt = stmt.where(Deal.pipeline_id == pipeline_id)
        rows = list(db.execute(stmt).all())

        if not rows:
            return {"weighted_amount": 0.0, "total_open": 0, "total_amount_open": 0.0}

        stage_ids = [r.stage_id for r in rows]
        stage_map = dict(
            db.execute(
                select(PipelineStage.id, PipelineStage.probability).where(PipelineStage.id.in_(stage_ids))
            ).all()
        )
        weighted = 0.0
        total_amount = 0.0
        for _, amount, stage_id in rows:
            p = float(stage_map.get(stage_id, 0.2))
            amt = float(amount or 0.0)
            weighted += amt * p
            total_amount += amt

        return {
            "weighted_amount": float(weighted),
            "total_open": len(rows),
            "total_amount_open": float(total_amount),
        }


ai_service = AIService()
