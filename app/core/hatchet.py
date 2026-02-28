from typing import Any

from api_shared.hatchet_client import get_hatchet
from hatchet_sdk import Hatchet
from hatchet_sdk.clients.rest.models.v1_workflow_run import V1WorkflowRun
from hatchet_sdk.clients.rest.models.v1_workflow_run_details import (
    V1WorkflowRunDetails,
)


class ExternalRunner:
    """Abstraction over external task execution/read operations."""

    def __init__(self, hatchet: Hatchet | None = None):
        self.hatchet = hatchet or get_hatchet()

    async def trigger_task(
        self,
        *,
        name: str,
        input: Any,
        input_validator: type[Any] | None = None,
        output_validator: type[Any] | None = None,
    ) -> V1WorkflowRun:
        stub = self.hatchet.stubs.task(
            name=name,
            input_validator=input_validator,
            output_validator=output_validator,
        )
        run_ref = await stub.aio_run_no_wait(input=input)
        return (await self.hatchet.runs.aio_get(run_ref.workflow_run_id)).run

    async def get_task(self, task_id: str) -> V1WorkflowRunDetails:
        return await self.hatchet.runs.aio_get(task_id)
