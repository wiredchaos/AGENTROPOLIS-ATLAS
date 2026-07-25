import pytest
from pydantic import ValidationError

from atlas_mcp.models import (
    AuthorityGeometry,
    Coordinate,
    GeocodeRequest,
    Mandate,
    NearbyRequest,
    RouteRequest,
)
from atlas_mcp.providers import haversine_meters
from atlas_mcp.service import AtlasService
from atlas_mcp.settings import AtlasSettings


PRINCIPAL = "agent://neuro/navigation"
SACRAMENTO = Coordinate(longitude=-121.4944, latitude=38.5816)


@pytest.fixture
def settings() -> AtlasSettings:
    return AtlasSettings(
        authenticated_principal=PRINCIPAL,
        default_max_radius_meters=5000,
        max_result_limit=25,
    )


@pytest.fixture
def mandate() -> Mandate:
    return Mandate(
        agent_id=PRINCIPAL,
        purpose="Test bounded public infrastructure lookup",
        max_radius_meters=5000,
        authority_geometry=AuthorityGeometry(center=SACRAMENTO, radius_meters=10000),
    )


@pytest.fixture
def service(settings: AtlasSettings) -> AtlasService:
    return AtlasService(settings)


def test_geocode_emits_governed_receipt(service: AtlasService, mandate: Mandate) -> None:
    result = service.geocode(GeocodeRequest(query="Downtown Sacramento", mandate=mandate))
    assert result.data["name"] == "Downtown Sacramento"
    assert result.receipt.tool == "atlas_geocode"
    assert result.receipt.principal_id == PRINCIPAL
    assert result.receipt.policy_decision == "allow"
    assert "OpenStreetMap" in result.receipt.sources
    assert result.receipt.authority == "read_only"


def test_rejects_impersonated_agent(settings: AtlasSettings, mandate: Mandate) -> None:
    service = AtlasService(settings)
    forged = mandate.model_copy(update={"agent_id": "agent://attacker"})
    with pytest.raises(PermissionError, match="authenticated principal"):
        service.geocode(GeocodeRequest(query="Downtown Sacramento", mandate=forged))


def test_nearby_enforces_complete_radius_boundary(service: AtlasService, mandate: Mandate) -> None:
    request = NearbyRequest(
        center=Coordinate(longitude=-121.40, latitude=38.5816),
        category="ev_charging",
        radius_meters=5000,
        mandate=mandate,
    )
    with pytest.raises(PermissionError, match="extends outside authority geometry"):
        service.nearby(request)


def test_deployment_limit_overrides_caller_mandate(mandate: Mandate) -> None:
    service = AtlasService(
        AtlasSettings(
            authenticated_principal=PRINCIPAL,
            default_max_radius_meters=1000,
            max_result_limit=5,
        )
    )
    with pytest.raises(PermissionError, match="deployment limit"):
        service.geocode(GeocodeRequest(query="Downtown Sacramento", mandate=mandate))


def test_route_is_evidence_not_navigation_authority(service: AtlasService, mandate: Mandate) -> None:
    result = service.route(
        RouteRequest(
            origin=SACRAMENTO,
            destination=Coordinate(longitude=-121.4882, latitude=38.5767),
            mode="walk",
            mandate=mandate,
        )
    )
    assert result.data["distance_meters"] > 0
    assert "not navigation guidance" in result.data["warning"]
    assert result.receipt.request_boundary["type"] == "corridor"
    assert result.receipt.authority_geometry.type == "circle"


def test_route_rejects_destination_outside_authority(service: AtlasService, mandate: Mandate) -> None:
    with pytest.raises(PermissionError, match="outside authority geometry"):
        service.route(
            RouteRequest(
                origin=SACRAMENTO,
                destination=Coordinate(longitude=-122.4194, latitude=37.7749),
                mode="drive",
                mandate=mandate,
            )
        )


def test_route_contract_accepts_bike_and_transit(service: AtlasService, mandate: Mandate) -> None:
    for mode in ("bike", "transit"):
        result = service.route(
            RouteRequest(
                origin=SACRAMENTO,
                destination=Coordinate(longitude=-121.4882, latitude=38.5767),
                mode=mode,
                mandate=mandate,
            )
        )
        assert result.data["mode"] == mode


def test_reverse_rejects_outside_mock_coverage(service: AtlasService, mandate: Mandate) -> None:
    wide_mandate = mandate.model_copy(
        update={
            "max_radius_meters": 5000,
            "authority_geometry": AuthorityGeometry(
                center=Coordinate(longitude=139.6917, latitude=35.6895),
                radius_meters=10000,
            ),
        }
    )
    with pytest.raises(LookupError, match="outside mock provider coverage"):
        service.reverse(
            __import__("atlas_mcp.models", fromlist=["ReverseRequest"]).ReverseRequest(
                coordinate=Coordinate(longitude=139.6917, latitude=35.6895),
                mandate=wide_mandate,
            )
        )


def test_ambiguous_geocode_is_rejected(service: AtlasService, mandate: Mandate) -> None:
    with pytest.raises(LookupError, match="unambiguous"):
        service.geocode(GeocodeRequest(query="town", mandate=mandate))


def test_haversine_handles_antipodal_coordinates() -> None:
    distance = haversine_meters(
        Coordinate(longitude=0, latitude=0),
        Coordinate(longitude=180, latitude=0),
    )
    assert distance > 20_000_000


def test_receipt_validation(service: AtlasService, mandate: Mandate) -> None:
    result = service.geocode(GeocodeRequest(query="Sacramento City Hall", mandate=mandate))
    validation = service.validate_receipt(result.receipt)
    assert validation["valid"] is True
    assert validation["issues"] == []


def test_receipt_rejects_empty_tool(service: AtlasService, mandate: Mandate) -> None:
    result = service.geocode(GeocodeRequest(query="Sacramento City Hall", mandate=mandate))
    with pytest.raises(ValidationError):
        result.receipt.model_copy(update={"tool": ""}).model_dump_json()
