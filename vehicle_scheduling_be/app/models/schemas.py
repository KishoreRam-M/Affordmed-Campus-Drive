from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MaintenanceTask(BaseModel):
    task_id: str = Field(..., examples=["T-101"])
    duration: int = Field(..., ge=0, examples=[3])
    impact: int = Field(..., ge=0, examples=[25])

    model_config = ConfigDict(populate_by_name=True)


class ScheduledTask(MaintenanceTask):
    vehicle_id: str | None = None


class Depot(BaseModel):
    depot_id: str
    mechanic_hours: int = Field(..., ge=0)


class Vehicle(BaseModel):
    vehicle_id: str
    depot_id: str | None = None
    tasks: list[MaintenanceTask] = Field(default_factory=list)


class ScheduleResponse(BaseModel):
    depot_id: str
    mechanic_hours: int
    used_hours: int
    remaining_hours: int
    total_impact: int
    selected_tasks: list[ScheduledTask]


def first_present(data: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in data:
            return data[name]
    return None


def extract_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("data", "items", "depots", "vehicles", "results", "notifications"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def normalize_depot(raw: dict[str, Any]) -> Depot:
    depot_id = first_present(raw, ("depot_id", "DepotID", "DepotId", "id", "ID"))
    hours = first_present(
        raw,
        (
            "mechanic_hours",
            "MechanicHours",
            "MechanicHour",
            "available_mechanic_hours",
            "AvailableMechanicHours",
            "capacity",
            "Capacity",
        ),
    )
    return Depot(depot_id=str(depot_id), mechanic_hours=int(hours))


def normalize_task(raw: dict[str, Any]) -> MaintenanceTask:
    task_id = first_present(raw, ("task_id", "TaskID", "TaskId", "id", "ID"))
    duration = first_present(raw, ("duration", "Duration"))
    impact = first_present(raw, ("impact", "Impact"))
    return MaintenanceTask(task_id=str(task_id), duration=int(duration), impact=int(impact))


def normalize_vehicle(raw: dict[str, Any]) -> Vehicle:
    vehicle_id = first_present(raw, ("vehicle_id", "VehicleID", "VehicleId", "id", "ID"))
    depot_id = first_present(raw, ("depot_id", "DepotID", "DepotId"))
    raw_tasks = first_present(
        raw,
        ("tasks", "Tasks", "maintenance_tasks", "MaintenanceTasks", "maintenanceTasks"),
    )

    tasks: list[MaintenanceTask] = []
    if isinstance(raw_tasks, list):
        tasks = [normalize_task(task) for task in raw_tasks if isinstance(task, dict)]
    elif all(key in raw for key in ("TaskID", "Duration", "Impact")) or all(
        key in raw for key in ("task_id", "duration", "impact")
    ):
        tasks = [normalize_task(raw)]

    return Vehicle(
        vehicle_id=str(vehicle_id),
        depot_id=str(depot_id) if depot_id is not None else None,
        tasks=tasks,
    )


class Notification(BaseModel):
    id: str
    title: str = ""
    category: str
    is_read: bool = False
    created_at: str = ""

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value: Any) -> str:
        return str(value)

