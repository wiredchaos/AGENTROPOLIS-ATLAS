from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class AuthorityMode(StrEnum):
    READ_ONLY = "read_only"


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"


class Coordinate(BaseModel):
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)


class AuthorityGeometry(BaseModel):
    type: Literal["circle"] = "circle"
    center: Coordinate
    radius_meters: int = Field(gt=0, le=200000)


class Mandate(BaseModel):
    agent_id: str = Field(min_length=3, max_length=200)
    purpose: str = Field(min_length=3, max_length=500)
    authority: AuthorityMode = AuthorityMode.READ_ONLY
    authority_geometry: AuthorityGeometry
    max_radius_meters: int = Field(default=5000, gt=0, le=100000)

    @model_validator(mode="after")
    def radius_within_authority_geometry(self) -> "Mandate":
        if self.max_radius_meters > self.authority_geometry.radius_meters:
            raise ValueError("mandate radius exceeds authority geometry")
        return self


class GeocodeRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    mandate: Mandate


class ReverseRequest(BaseModel):
    coordinate: Coordinate
    mandate: Mandate


class NearbyRequest(BaseModel):
    center: Coordinate
    category: str = Field(min_length=2, max_length=100)
    radius_meters: int = Field(gt=0, le=100000)
    limit: int = Field(default=10, gt=0, le=100)
    mandate: Mandate


class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    mode: Literal["drive", "walk", "bike", "transit"] = "drive"
    mandate: Mandate


class AtlasReceipt(BaseModel):
    receipt_type: Literal["atg.spatial.receipt.v1"] = "atg.spatial.receipt.v1"
    request_id: str = Field(default_factory=lambda: f"atlas_{uuid4().hex[:16]}", min_length=8)
    principal_id: str = Field(min_length=3, max_length=200)
    agent_id: str = Field(min_length=3, max_length=200)
    mandate: str = Field(min_length=3, max_length=500)
    tool: str = Field(min_length=3, max_length=100)
    provider: str = Field(min_length=3, max_length=200)
    authority: AuthorityMode = AuthorityMode.READ_ONLY
    authority_geometry: AuthorityGeometry
    policy_decision: PolicyDecision
    policy_reason: str = Field(min_length=3, max_length=500)
    sources: list[str] = Field(min_length=1)
    attribution: str = Field(min_length=3, max_length=500)
    confidence: float = Field(ge=0, le=1)
    request_boundary: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToolResult(BaseModel):
    data: dict[str, Any]
    receipt: AtlasReceipt
