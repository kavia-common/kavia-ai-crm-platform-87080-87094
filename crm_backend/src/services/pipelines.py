from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from src.db.models import Pipeline, PipelineStage
from src.schemas.pipelines import PipelineCreate, PipelineUpdate, PipelineStageCreate, PipelineStageUpdate
from src.services.common import CRUDService


class PipelineService(CRUDService[Pipeline, PipelineCreate, PipelineUpdate]):
    pass


class PipelineStageService(CRUDService[PipelineStage, PipelineStageCreate, PipelineStageUpdate]):
    def list_for_pipeline(self, db: Session, pipeline_id: int) -> List[PipelineStage]:
        stmt = select(PipelineStage).where(PipelineStage.pipeline_id == pipeline_id).order_by(PipelineStage.order.asc())
        return list(db.execute(stmt).scalars().all())


pipeline_service = PipelineService(Pipeline)
pipeline_stage_service = PipelineStageService(PipelineStage)
