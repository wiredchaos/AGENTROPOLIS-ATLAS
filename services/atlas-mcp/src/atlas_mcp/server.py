from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .models import AtlasReceipt, GeocodeRequest, NearbyRequest, ReverseRequest, RouteRequest
from .service import AtlasService


mcp = FastMCP("AGENTROPOLIS-ATLAS", json_response=True)
service = AtlasService()


@mcp.tool()
def atlas_geocode(request: GeocodeRequest) -> dict:
    """Resolve a place or address and emit an ATG spatial receipt."""
    return service.geocode(request).model_dump(mode="json")


@mcp.tool()
def atlas_reverse(request: ReverseRequest) -> dict:
    """Resolve a coordinate to the nearest known feature."""
    return service.reverse(request).model_dump(mode="json")


@mcp.tool()
def atlas_nearby(request: NearbyRequest) -> dict:
    """Find bounded nearby infrastructure within the declared mandate."""
    return service.nearby(request).model_dump(mode="json")


@mcp.tool()
def atlas_route(request: RouteRequest) -> dict:
    """Calculate a read-only route and return evidence, not authorization."""
    return service.route(request).model_dump(mode="json")


@mcp.tool()
def atlas_receipt(receipt: AtlasReceipt) -> dict:
    """Validate required evidence fields on an ATG spatial receipt."""
    return service.validate_receipt(receipt)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
