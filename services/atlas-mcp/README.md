# ATLAS MCP Gateway

The ATLAS MCP Gateway is the governed interface between agents and geospatial providers. Phase 001 is read-only, provider-adapted, and receipt-first.

## Implemented tools

| Tool | Purpose | Phase 001 adapter |
|---|---|---|
| `atlas_geocode` | Resolve a place or address | deterministic mock Pelias |
| `atlas_reverse` | Resolve coordinates to a nearby named feature | deterministic mock Pelias |
| `atlas_nearby` | Find bounded nearby infrastructure | deterministic mock PostGIS |
| `atlas_route` | Calculate a constrained route | deterministic mock Valhalla |
| `atlas_receipt` | Validate an ATG spatial evidence record | local validator |

The mock adapters make the contract, governance rules, and tests reproducible without Google Maps or dependency on public OSM community servers.

## Run locally

Requirements: Python 3.11+ and `uv`.

```bash
cd services/atlas-mcp
uv sync --extra dev
uv run atlas-mcp
```

The server uses the stable MCP Python SDK v1 line (`mcp>=1.27,<2`) and communicates over stdio by default.

## Test

```bash
cd services/atlas-mcp
uv sync --extra dev
uv run pytest
```

## Example mandate

```json
{
  "agent_id": "agent://neuro/navigation",
  "purpose": "Locate public EV charging infrastructure",
  "authority": "read_only",
  "max_radius_meters": 5000
}
```

## Required middleware order

```text
Authenticate agent
  -> Validate mandate
  -> Resolve authority geometry
  -> Enforce rate and cost budget
  -> Select provider adapter
  -> Execute bounded request
  -> Validate and normalize result
  -> Attach attribution
  -> Emit ATG spatial receipt
```

## Provider configuration

Copy `.env.example` and replace mock adapters only with approved, preferably self-hosted services. Provider URLs must remain configurable. Public community endpoints are development fallbacks, never silent production defaults.

## Safety and governance boundaries

- no Google Maps dependency;
- no autonomous OpenStreetMap edits;
- no silent fallback to unapproved providers;
- no result without source and attribution metadata;
- no query outside the declared authority geometry;
- no route result may be interpreted as dispatch, entry permission, or physical-world authorization.

## Next adapters

1. Pelias or Nominatim geocoding;
2. PostGIS nearby-feature search;
3. Valhalla routing;
4. OSRM distance matrices;
5. Martin and PMTiles map delivery.
