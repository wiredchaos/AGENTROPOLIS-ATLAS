from __future__ import annotations

from typing import Any

from .models import (
    AtlasReceipt,
    GeocodeRequest,
    NearbyRequest,
    ReverseRequest,
    RouteRequest,
    ToolResult,
)
from .providers import MockGeocoder, MockPlaces, MockRouter


ATTRIBUTION = "Map data © OpenStreetMap contributors"
SOURCES = ["OpenStreetMap", "AGENTROPOLIS mock fixtures"]


class AtlasService:
    def __init__(self) -> None:
        self.geocoder = MockGeocoder()
        self.places = MockPlaces()
        self.router = MockRouter()

    @staticmethod
    def _receipt(
        *,
        agent_id: str,
        purpose: str,
        tool: str,
        provider: str,
        confidence: float,
        boundary: dict[str, Any],
    ) -> AtlasReceipt:
        return AtlasReceipt(
            agent_id=agent_id,
            mandate=purpose,
            tool=tool,
            provider=provider,
            sources=SOURCES,
            attribution=ATTRIBUTION,
            confidence=confidence,
            boundary=boundary,
        )

    def geocode(self, request: GeocodeRequest) -> ToolResult:
        data = self.geocoder.geocode(request.query)
        receipt = self._receipt(
            agent_id=request.mandate.agent_id,
            purpose=request.mandate.purpose,
            tool="atlas_geocode",
            provider=self.geocoder.name,
            confidence=data["confidence"],
            boundary={"type": "query", "value": request.query},
        )
        return ToolResult(data=data, receipt=receipt)

    def reverse(self, request: ReverseRequest) -> ToolResult:
        data = self.geocoder.reverse(request.coordinate)
        receipt = self._receipt(
            agent_id=request.mandate.agent_id,
            purpose=request.mandate.purpose,
            tool="atlas_reverse",
            provider=self.geocoder.name,
            confidence=data["confidence"],
            boundary={"type": "point", "coordinate": request.coordinate.model_dump()},
        )
        return ToolResult(data=data, receipt=receipt)

    def nearby(self, request: NearbyRequest) -> ToolResult:
        if request.radius_meters > request.mandate.max_radius_meters:
            raise ValueError("requested radius exceeds mandate boundary")
        features = self.places.nearby(
            request.center,
            request.category,
            request.radius_meters,
            request.limit,
        )
        data = {"features": features, "count": len(features)}
        receipt = self._receipt(
            agent_id=request.mandate.agent_id,
            purpose=request.mandate.purpose,
            tool="atlas_nearby",
            provider=self.places.name,
            confidence=0.94 if features else 0.5,
            boundary={
                "type": "radius",
                "center": request.center.model_dump(),
                "radius_meters": request.radius_meters,
            },
        )
        return ToolResult(data=data, receipt=receipt)

    def route(self, request: RouteRequest) -> ToolResult:
        data = self.router.route(request.origin, request.destination, request.mode)
        receipt = self._receipt(
            agent_id=request.mandate.agent_id,
            purpose=request.mandate.purpose,
            tool="atlas_route",
            provider=self.router.name,
            confidence=data["confidence"],
            boundary={
                "type": "corridor",
                "origin": request.origin.model_dump(),
                "destination": request.destination.model_dump(),
            },
        )
        return ToolResult(data=data, receipt=receipt)

    @staticmethod
    def validate_receipt(receipt: AtlasReceipt) -> dict[str, Any]:
        valid = bool(
            receipt.request_id
            and receipt.agent_id
            and receipt.mandate
            and receipt.sources
            and receipt.attribution
            and receipt.boundary
        )
        return {
            "valid": valid,
            "request_id": receipt.request_id,
            "authority": receipt.authority,
            "issues": [] if valid else ["receipt is missing required evidence fields"],
        }
