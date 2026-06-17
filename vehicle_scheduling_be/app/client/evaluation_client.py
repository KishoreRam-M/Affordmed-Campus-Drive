from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.models.schemas import (
    Depot,
    Vehicle,
    extract_list,
    normalize_depot,
    normalize_vehicle,
)
from app.utils.exceptions import ExternalAPIError, ExternalAPITimeoutError


class EvaluationClient:
    def __init__(
        self,
        settings: Settings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._client = client

    async def _get(self, path: str) -> Any:
        url = f"{self.settings.evaluation_base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            if self._client is not None:
                response = await self._client.get(url)
            else:
                async with httpx.AsyncClient(
                    timeout=self.settings.request_timeout_seconds
                ) as client:
                    response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as exc:
            raise ExternalAPITimeoutError() from exc
        except (httpx.HTTPStatusError, httpx.RequestError, ValueError) as exc:
            raise ExternalAPIError() from exc

    async def get_depots_raw(self) -> Any:
        return await self._get("/depots")

    async def get_vehicles_raw(self) -> Any:
        return await self._get("/vehicles")

    async def get_depots(self) -> list[Depot]:
        raw_depots = extract_list(await self.get_depots_raw())
        try:
            return [normalize_depot(item) for item in raw_depots]
        except (TypeError, ValueError) as exc:
            raise ExternalAPIError("External depots payload is invalid") from exc

    async def get_vehicles(self) -> list[Vehicle]:
        raw_vehicles = extract_list(await self.get_vehicles_raw())
        try:
            return [normalize_vehicle(item) for item in raw_vehicles]
        except (TypeError, ValueError) as exc:
            raise ExternalAPIError("External vehicles payload is invalid") from exc

