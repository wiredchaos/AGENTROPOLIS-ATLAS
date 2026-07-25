from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from typing import Any

from .models import Coordinate


PLACES: list[dict[str, Any]] = [
    {
        "name": "Downtown Sacramento",
        "category": "district",
        "coordinate": Coordinate(longitude=-121.4944, latitude=38.5816),
    },
    {
        "name": "Sacramento Valley Station",
        "category": "transit",
        "coordinate": Coordinate(longitude=-121.5008, latitude=38.5848),
    },
    {
        "name": "Sacramento City Hall",
        "category": "civic",
        "coordinate": Coordinate(longitude=-121.4934, latitude=38.5812),
    },
    {
        "name": "Capitol Garage EV Charging",
        "category": "ev_charging",
        "coordinate": Coordinate(longitude=-121.4882, latitude=38.5767),
    },
]

MOCK_COVERAGE_RADIUS_METERS = 50_000
MOCK_COVERAGE_CENTER = Coordinate(longitude=-121.4944, latitude=38.5816)


def haversine_meters(a: Coordinate, b: Coordinate) -> float:
    earth_radius_m = 6_371_000
    lat1, lat2 = radians(a.latitude), radians(b.latitude)
    d_lat = radians(b.latitude - a.latitude)
    d_lon = radians(b.longitude - a.longitude)
    h = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    h = max(0.0, min(1.0, h))
    return earth_radius_m * 2 * atan2(sqrt(h), sqrt(1 - h))


class MockGeocoder:
    name = "mock-pelias"

    def geocode(self, query: str) -> dict[str, Any]:
        normalized_tokens = set(query.casefold().replace(",", " ").split())
        candidates: list[dict[str, Any]] = []
        for place in PLACES:
            place_tokens = set(place["name"].casefold().split())
            if normalized_tokens == place_tokens or normalized_tokens.issuperset(place_tokens):
                candidates.append(place)
        if len(candidates) != 1:
            raise LookupError(f"no unambiguous mock geocode result for: {query}")
        place = candidates[0]
        return {
            "name": place["name"],
            "coordinate": place["coordinate"].model_dump(),
            "confidence": 0.98,
        }

    def reverse(self, coordinate: Coordinate) -> dict[str, Any]:
        if haversine_meters(coordinate, MOCK_COVERAGE_CENTER) > MOCK_COVERAGE_RADIUS_METERS:
            raise LookupError("coordinate is outside mock provider coverage")
        nearest = min(PLACES, key=lambda place: haversine_meters(coordinate, place["coordinate"]))
        distance = haversine_meters(coordinate, nearest["coordinate"])
        return {
            "name": nearest["name"],
            "coordinate": nearest["coordinate"].model_dump(),
            "distance_meters": round(distance, 1),
            "confidence": max(0.5, round(1 - distance / MOCK_COVERAGE_RADIUS_METERS, 3)),
        }


class MockPlaces:
    name = "mock-postgis"

    def nearby(self, center: Coordinate, category: str, radius_meters: int, limit: int) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for place in PLACES:
            if place["category"] != category:
                continue
            distance = haversine_meters(center, place["coordinate"])
            if distance <= radius_meters:
                matches.append(
                    {
                        "name": place["name"],
                        "category": place["category"],
                        "coordinate": place["coordinate"].model_dump(),
                        "distance_meters": round(distance, 1),
                    }
                )
        return sorted(matches, key=lambda item: item["distance_meters"])[:limit]


class MockRouter:
    name = "mock-valhalla"

    SPEED_METERS_PER_SECOND = {
        "drive": 11.11,
        "walk": 1.4,
        "bike": 4.5,
        "transit": 8.0,
    }

    def route(self, origin: Coordinate, destination: Coordinate, mode: str) -> dict[str, Any]:
        direct = haversine_meters(origin, destination)
        routed = direct * 1.18
        duration = routed / self.SPEED_METERS_PER_SECOND[mode]
        return {
            "mode": mode,
            "distance_meters": round(routed, 1),
            "duration_seconds": round(duration),
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [origin.longitude, origin.latitude],
                    [destination.longitude, destination.latitude],
                ],
            },
            "confidence": 0.80,
            "warning": "Mock route for contract testing only; not navigation guidance.",
        }
