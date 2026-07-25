from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class AuthorityMode(StrEnum):
    READ_ONLY = "read_only"


class Coordinate(BaseModel):
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)


class Mandate(BaseModel):
    agent_id: str = Field(min_length=3, max_length=200)
    purpose: str = Field(min_length=3, max_length=500)
    authority: AuthorityMode = AuthorityMode.READ_ONLY
    max_radius_meters: int = Field(default=5000, gt=0, le=100000)


class GeocodeRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
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

    @field_validator("radius_meters")
    @classmethod
    def radius_within_mandate(cls, value: int, info: Any) -> int:
        mandate = info.data.get("mandate")
        if mandate and value > mandate.max_radius_meters:
            raise ValueError("requested radius exceeds mandate boundary")
        return value


class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    mode: Literal["drive", "walk", "bicycle"] = "drive"
    mandate: Mandate


class AtlasReceipt(BaseModel):
    request_id: str = Field(default_factory=lambda: f"atlas_{uuid4().hex[:16]}")
    agent_id: str
    mandate: str
    tool: str
    provider: str
    authority: AuthorityMode = AuthorityMode.READ_ONLY
    sources: list[str]
    attribution: str
    confidence: float = Field(ge=0, le=1)
    boundary: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToolResult(BaseModel):
    data: dict[str, Any]
    receipt: AtlasReceipt
