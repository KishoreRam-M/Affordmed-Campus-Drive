from typing import Any

from fastapi.testclient import TestClient

from app.api.routes import get_evaluation_client
from app.main import app
from app.models.schemas import Depot, MaintenanceTask, Vehicle
from app.utils.exceptions import ExternalAPIError


class StubEvaluationClient:
    def __init__(
        self,
        depots: list[Depot] | None = None,
        vehicles: list[Vehicle] | None = None,
        should_fail: bool = False,
    ) -> None:
        self.depots = depots or []
        self.vehicles = vehicles or []
        self.should_fail = should_fail

    async def get_depots_raw(self) -> Any:
        if self.should_fail:
            raise ExternalAPIError()
        return {"depots": [depot.model_dump() for depot in self.depots]}

    async def get_vehicles_raw(self) -> Any:
        if self.should_fail:
            raise ExternalAPIError()
        return {"vehicles": [vehicle.model_dump() for vehicle in self.vehicles]}

    async def get_depots(self) -> list[Depot]:
        if self.should_fail:
            raise ExternalAPIError()
        return self.depots

    async def get_vehicles(self) -> list[Vehicle]:
        if self.should_fail:
            raise ExternalAPIError()
        return self.vehicles


def override_client(stub: StubEvaluationClient) -> None:
    app.dependency_overrides[get_evaluation_client] = lambda: stub


def test_schedule_valid_depot() -> None:
    override_client(
        StubEvaluationClient(
            depots=[Depot(depot_id="D1", mechanic_hours=7)],
            vehicles=[
                Vehicle(
                    vehicle_id="V1",
                    depot_id="D1",
                    tasks=[
                        MaintenanceTask(task_id="T1", duration=2, impact=10),
                        MaintenanceTask(task_id="T2", duration=5, impact=30),
                    ],
                ),
                Vehicle(
                    vehicle_id="V2",
                    depot_id="D2",
                    tasks=[MaintenanceTask(task_id="T3", duration=1, impact=99)],
                ),
            ],
        )
    )

    response = TestClient(app).get("/api/v1/schedule/D1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["depot_id"] == "D1"
    assert payload["used_hours"] == 7
    assert payload["total_impact"] == 40
    assert [task["task_id"] for task in payload["selected_tasks"]] == ["T1", "T2"]
    assert {task["vehicle_id"] for task in payload["selected_tasks"]} == {"V1"}


def test_schedule_invalid_depot_returns_404() -> None:
    override_client(StubEvaluationClient(depots=[Depot(depot_id="D1", mechanic_hours=7)]))

    response = TestClient(app).get("/api/v1/schedule/UNKNOWN")

    assert response.status_code == 404
    assert "not found" in response.json()["error"].lower()


def test_schedule_external_api_failure_returns_502() -> None:
    override_client(StubEvaluationClient(should_fail=True))

    response = TestClient(app).get("/api/v1/schedule/D1")

    assert response.status_code == 502
    assert "external" in response.json()["error"].lower()


def test_proxy_endpoints_return_raw_external_payloads() -> None:
    override_client(StubEvaluationClient(depots=[Depot(depot_id="D1", mechanic_hours=3)]))
    client = TestClient(app)

    depots_response = client.get("/api/v1/depots")
    vehicles_response = client.get("/api/v1/vehicles")

    assert depots_response.status_code == 200
    assert depots_response.json() == {"depots": [{"depot_id": "D1", "mechanic_hours": 3}]}
    assert vehicles_response.status_code == 200
    assert vehicles_response.json() == {"vehicles": []}
