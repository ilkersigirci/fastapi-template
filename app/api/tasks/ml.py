"""ML Hatchet task endpoints."""

from typing import Annotated

from api_shared.tasks.ml import (
    ML_INFERENCE_TASK,
    TRAIN_MODEL_TASK,
    MLInferenceInput,
    MLInferenceResult,
    MLTrainingInput,
    MLTrainingResult,
)
from fastapi import APIRouter, Depends, HTTPException
from hatchet_sdk.clients.rest.models.v1_workflow_run import V1WorkflowRun
from hatchet_sdk.clients.rest.models.v1_workflow_run_details import (
    V1WorkflowRunDetails,
)

from app.api.tasks.deps import get_runner
from app.core.hatchet import ExternalRunner

router = APIRouter(prefix="/tasks/ml", tags=["ml-tasks"])


@router.post("/inference", response_model=V1WorkflowRun)
async def trigger_ml_inference(
    params: MLInferenceInput,
    runner: Annotated[ExternalRunner, Depends(get_runner)],
) -> V1WorkflowRun:
    return await runner.trigger_task(
        name=ML_INFERENCE_TASK,
        input=params,
        input_validator=MLInferenceInput,
        output_validator=MLInferenceResult,
    )


@router.post("/training", response_model=V1WorkflowRun)
async def trigger_ml_training(
    params: MLTrainingInput,
    runner: Annotated[ExternalRunner, Depends(get_runner)],
) -> V1WorkflowRun:
    return await runner.trigger_task(
        name=TRAIN_MODEL_TASK,
        input=params,
        input_validator=MLTrainingInput,
        output_validator=MLTrainingResult,
    )


@router.get("/{task_id}", response_model=V1WorkflowRunDetails)
async def get_ml_task_result(
    task_id: str,
    runner: Annotated[ExternalRunner, Depends(get_runner)],
) -> V1WorkflowRunDetails:
    try:
        return await runner.get_task(task_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
