from typing import Annotated

from fastapi import APIRouter, Depends

from app.clients.evaluation_client import EvaluationClient
from app.models.schemas import ScheduleResponse, ScheduledTask
from app.services.optimizer import optimize_tasks
from app.utils.exceptions import DepotNotFoundError, InvalidDepotError

router = APIRouter()


def get_evaluation_client() -> EvaluationClient:
    return EvaluationClient()


EvaluationClientDep = Annotated[EvaluationClient, Depends(get_evaluation_client)]


@router.get("/depots")
async def get_depots(client: EvaluationClientDep) -> object:
    return await client.get_depots_raw()


@router.get("/vehicles")
async def get_vehicles(client: EvaluationClientDep) -> object:
    return await client.get_vehicles_raw()


@router.get("/schedule/{depot_id}", response_model=ScheduleResponse)
async def get_schedule(depot_id: str, client: EvaluationClientDep) -> ScheduleResponse:
    depots = await client.get_depots()
    depot = next((item for item in depots if item.depot_id == depot_id), None)
    if depot is None:
        raise DepotNotFoundError(depot_id)
    if depot.mechanic_hours < 0:
        raise InvalidDepotError(depot_id)

    vehicles = await client.get_vehicles()
    candidate_tasks: list[ScheduledTask] = []
    for vehicle in vehicles:
        if vehicle.depot_id is not None and vehicle.depot_id != depot_id:
            continue
        candidate_tasks.extend(
            ScheduledTask(
                task_id=task.task_id,
                duration=task.duration,
                impact=task.impact,
                vehicle_id=vehicle.vehicle_id,
            )
            for task in vehicle.tasks
        )

    selected, used_hours, total_impact = optimize_tasks(
        candidate_tasks,
        depot.mechanic_hours,
    )
    selected_tasks = [
        task if isinstance(task, ScheduledTask) else ScheduledTask(**task.model_dump())
        for task in selected
    ]
    return ScheduleResponse(
        depot_id=depot.depot_id,
        mechanic_hours=depot.mechanic_hours,
        used_hours=used_hours,
        remaining_hours=depot.mechanic_hours - used_hours,
        total_impact=total_impact,
        selected_tasks=selected_tasks,
    )

