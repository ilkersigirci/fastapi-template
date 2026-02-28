"""General Hatchet task endpoints."""

from typing import Annotated

from api_shared.tasks.general import (
    FAILING_PROCESS_TASK,
    LONG_RUNNING_PROCESS_TASK,
    PYDANTIC_PARSE_CHECK_TASK,
    FailingProcessInput,
    LongRunningProcessInput,
    LongRunningProcessResult,
    PydanticParseInput,
    PydanticParseResult,
)
from fastapi import APIRouter, Depends, HTTPException
from hatchet_sdk.clients.rest.models.v1_workflow_run import V1WorkflowRun
from hatchet_sdk.clients.rest.models.v1_workflow_run_details import (
    V1WorkflowRunDetails,
)

from app.api.tasks.deps import get_runner
from app.core.hatchet import ExternalRunner

router = APIRouter(prefix="/tasks/general", tags=["tasks"])


@router.post("/long-running", response_model=V1WorkflowRun)
async def trigger_task(
    params: LongRunningProcessInput,
    runner: Annotated[ExternalRunner, Depends(get_runner)],
) -> V1WorkflowRun:
    return await runner.trigger_task(
        name=LONG_RUNNING_PROCESS_TASK,
        input=params,
        input_validator=LongRunningProcessInput,
        output_validator=LongRunningProcessResult,
    )


@router.post("/fail", response_model=V1WorkflowRun)
async def trigger_failing_task(
    params: FailingProcessInput,
    runner: Annotated[ExternalRunner, Depends(get_runner)],
) -> V1WorkflowRun:
    return await runner.trigger_task(
        name=FAILING_PROCESS_TASK,
        input=params,
        input_validator=FailingProcessInput,
    )


@router.post("/pydantic", response_model=V1WorkflowRun)
async def trigger_pydantic_parse(
    params: PydanticParseInput,
    runner: Annotated[ExternalRunner, Depends(get_runner)],
) -> V1WorkflowRun:
    return await runner.trigger_task(
        name=PYDANTIC_PARSE_CHECK_TASK,
        input=params,
        input_validator=PydanticParseInput,
        output_validator=PydanticParseResult,
    )


@router.get("/{task_id}", response_model=V1WorkflowRunDetails)
async def get_task_result(
    task_id: str,
    runner: Annotated[ExternalRunner, Depends(get_runner)],
) -> V1WorkflowRunDetails:
    try:
        return await runner.get_task(task_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
