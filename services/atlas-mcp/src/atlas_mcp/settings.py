from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AtlasSettings:
    authenticated_principal: str
    default_max_radius_meters: int
    max_result_limit: int

    @classmethod
    def from_env(cls) -> "AtlasSettings":
        principal = os.getenv("ATLAS_AUTHENTICATED_PRINCIPAL", "").strip()
        if not principal:
            raise RuntimeError("ATLAS_AUTHENTICATED_PRINCIPAL is required")
        return cls(
            authenticated_principal=principal,
            default_max_radius_meters=int(os.getenv("ATLAS_DEFAULT_MAX_RADIUS_METERS", "5000")),
            max_result_limit=int(os.getenv("ATLAS_MAX_RESULT_LIMIT", "100")),
        )
