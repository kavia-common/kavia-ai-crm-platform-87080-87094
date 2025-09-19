from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from src.db.models import Deal, DealStageStatus, PipelineStage
from src.schemas.deals import DealCreate, DealUpdate
from src.services.common import CRUDService


class DealService(CRUDService[Deal, DealCreate, DealUpdate]):
    def amount_forecast(self, db: Session, pipeline_id: Optional[int] = None) -> float:
        """
        Simple forecast: sum(amount * stage.probability) for open deals.
        """
        stmt = (
            select(func.sum(Deal.amount * PipelineStage.probability))
            .join(PipelineStage, Deal.stage_id == PipelineStage.id)
            .where(Deal.status == DealStageStatus.open)
        )
        if pipeline_id:
            stmt = stmt.where(Deal.pipeline_id == pipeline_id)
        result = db.execute(stmt).scalar() or 0.0
        return float(result)


deal_service = DealService(Deal)
