import pytest

from atlas_mcp.models import Coordinate, GeocodeRequest, Mandate, NearbyRequest, RouteRequest
from atlas_mcp.service import AtlasService


@pytest.fixture
def mandate() -> Mandate:
    return Mandate(
        agent_id="agent://neuro/navigation",
        purpose="Test bounded public infrastructure lookup",
        max_radius_meters=5000,
    )


def test_geocode_emits_receipt(mandate: Mandate) -> None:
    service = AtlasService()
    result = service.geocode(GeocodeRequest(query="Downtown Sacramento", mandate=mandate))
    assert result.data["name"] == "Downtown Sacramento"
    assert result.receipt.tool == "atlas_geocode"
    assert "OpenStreetMap" in result.receipt.sources
    assert result.receipt.authority == "read_only"


def test_nearby_enforces_mandate_radius(mandate: Mandate) -> None:
    service = AtlasService()
    request = NearbyRequest(
        center=Coordinate(longitude=-121.4944, latitude=38.5816),
        category="ev_charging",
        radius_meters=6000,
        mandate=mandate,
    )
    with pytest.raises(ValueError, match="exceeds mandate"):
        service.nearby(request)


def test_route_is_evidence_not_navigation_authority(mandate: Mandate) -> None:
    service = AtlasService()
    result = service.route(
        RouteRequest(
            origin=Coordinate(longitude=-121.4944, latitude=38.5816),
            destination=Coordinate(longitude=-121.4882, latitude=38.5767),
            mode="walk",
            mandate=mandate,
        )
    )
    assert result.data["distance_meters"] > 0
    assert "not navigation guidance" in result.data["warning"]
    assert result.receipt.boundary["type"] == "corridor"


def test_receipt_validation(mandate: Mandate) -> None:
    service = AtlasService()
    result = service.geocode(GeocodeRequest(query="Sacramento City Hall", mandate=mandate))
    validation = service.validate_receipt(result.receipt)
    assert validation["valid"] is True
    assert validation["issues"] == []
