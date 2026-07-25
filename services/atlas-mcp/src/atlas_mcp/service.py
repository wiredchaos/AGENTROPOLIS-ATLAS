from __future__ import annotations

from typing import Any

from .models import (
    AtlasReceipt,
    Coordinate,
    GeocodeRequest,
    Mandate,
    NearbyRequest,
    PolicyDecision,
    ReverseRequest,
    RouteRequest,
    ToolResult,
)
from .providers import MockGeocoder, MockPlaces, MockRouter, haversine_meters
from .settings import AtlasSettings


ATTRIBUTION = "Map data © OpenStreetMap contributors"
SOURCES = ["OpenStreetMap", "AGENTROPOLIS mock fixtures"]


class AtlasService:
    def __init__(self, settings: AtlasSettings) -> None:
        self.settings = settings
        self.geocoder = MockGeocoder()
        self.places = MockPlaces()
        self.router = MockRouter()

    def _authenticate(self, mandate: Mandate) -> None:
        if mandate.agent_id != self.settings.authenticated_principal:
            raise PermissionError("mandate agent_id does not match authenticated principal")

    def _enforce_point(self, coordinate: Coordinate, mandate: Mandate) -> None:
        distance = haversine_meters(coordinate, mandate.authority_geometry.center)
        if distance > mandate.authority_geometry.radius_meters:
            raise PermissionError("coordinate is outside authority geometry")

    def _enforce_request_limits(self, mandate: Mandate) -> None:
        if mandate.max_radius_meters > self.settings.default_max_radius_meters:
            raise PermissionError("mandate radius exceeds deployment limit")

    def _authorize(self, mandate: Mandate) -> None:
        self._authenticate(mandate)
        self._enforce_request_limits(mandate)

    def _receipt(
        self,
        *,
        mandate: Mandate,
        tool: str,
        provider: str,
        confidence: float,
        request_boundary: dict[str, Any],
        reason: str,
    ) -> AtlasReceipt:
        return AtlasReceipt(
            principal_id=self.settings.authenticated_principal,
            agent_id=mandate.agent_id,
            mandate=mandate.purpose,
            tool=tool,
            provider=provider,
            authority_geometry=mandate.authority_geometry,
            policy_decision=PolicyDecision.ALLOW,
            policy_reason=reason,
            sources=SOURCES,
            attribution=ATTRIBUTION,
            confidence=confidence,
            request_boundary=request_boundary,
        )

    def geocode(self, request: GeocodeRequest) -> ToolResult:
        self._authorize(request.mandate)
        data = self.geocoder.geocode(request.query)
        coordinate = Coordinate(**data["coordinate"])
        self._enforce_point(coordinate, request.mandate)
        receipt = self._receipt(
            mandate=request.mandate,
            tool="atlas_geocode",
            provider=self.geocoder.name,
            confidence=data["confidence"],
            request_boundary={"type": "query", "value": request.query},
            reason="authenticated principal and resolved coordinate are within authority geometry",
        )
        return ToolResult(data=data, receipt=receipt)

    def reverse(self, request: ReverseRequest) -> ToolResult:
        self._authorize(request.mandate)
        self._enforce_point(request.coordinate, request.mandate)
        data = self.geocoder.reverse(request.coordinate)
        receipt = self._receipt(
            mandate=request.mandate,
            tool="atlas_reverse",
            provider=self.geocoder.name,
            confidence=data["confidence"],
            request_boundary={"type": "point", "coordinate": request.coordinate.model_dump()},
            reason="authenticated principal and requested coordinate are within authority geometry",
        )
        return ToolResult(data=data, receipt=receipt)

    def nearby(self, request: NearbyRequest) -> ToolResult:
        self._authorize(request.mandate)
        self._enforce_point(request.center, request.mandate)
        if request.radius_meters > request.mandate.max_radius_meters:
            raise PermissionError("requested radius exceeds mandate boundary")
        if request.radius_meters > self.settings.default_max_radius_meters:
            raise PermissionError("requested radius exceeds deployment limit")
        if request.limit > self.settings.max_result_limit:
            raise PermissionError("requested result limit exceeds deployment limit")
        distance_from_authority_center = haversine_meters(
            request.center, request.mandate.authority_geometry.center
        )
        if distance_from_authority_center + request.radius_meters > request.mandate.authority_geometry.radius_meters:
            raise PermissionError("requested radius extends outside authority geometry")
        features = self.places.nearby(
            request.center,
            request.category,
            request.radius_meters,
            request.limit,
        )
        data = {"features": features, "count": len(features)}
        receipt = self._receipt(
            mandate=request.mandate,
            tool="atlas_nearby",
            provider=self.places.name,
            confidence=0.94 if features else 0.5,
            request_boundary={
                "type": "radius",
                "center": request.center.model_dump(),
                "radius_meters": request.radius_meters,
            },
            reason="authenticated principal and complete query radius are within authority geometry",
        )
        return ToolResult(data=data, receipt=receipt)

    def route(self, request: RouteRequest) -> ToolResult:
        self._authorize(request.mandate)
        self._enforce_point(request.origin, request.mandate)
        self._enforce_point(request.destination, request.mandate)
        data = self.router.route(request.origin, request.destination, request.mode)
        receipt = self._receipt(
            mandate=request.mandate,
            tool="atlas_route",
            provider=self.router.name,
            confidence=data["confidence"],
            request_boundary={
                "type": "corridor",
                "origin": request.origin.model_dump(),
                "destination": request.destination.model_dump(),
            },
            reason="authenticated principal and route endpoints are within authority geometry",
        )
        return ToolResult(data=data, receipt=receipt)

    @staticmethod
    def validate_receipt(receipt: AtlasReceipt) -> dict[str, Any]:
        required_values = (
            receipt.request_id,
            receipt.principal_id,
            receipt.agent_id,
            receipt.mandate,
            receipt.tool,
            receipt.provider,
            receipt.sources,
            receipt.attribution,
            receipt.authority_geometry,
            receipt.policy_decision,
            receipt.policy_reason,
            receipt.request_boundary,
        )
        valid = all(bool(value) for value in required_values)
        return {
            "valid": valid,
            "request_id": receipt.request_id,
            "authority": receipt.authority,
            "policy_decision": receipt.policy_decision,
            "issues": [] if valid else ["receipt is missing required evidence fields"],
        }
