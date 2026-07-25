# AGENTROPOLIS-ATLAS

**Accountable spatial intelligence for autonomous agents.**

AGENTROPOLIS-ATLAS tells an accountable agent where it has authority to act, what exists there, which route is permitted, and which evidence supports the conclusion.

ATLAS is the geospatial layer of the AGENTROPOLIS Intelligence Grid. It replaces dependence on Google Maps MCP with an open, composable stack built around OpenStreetMap data, MapLibre, PostGIS, Pelias, Valhalla, OSRM, PMTiles, Martin and open geospatial standards.

## Phase 001: Spatial Read Plane

The first release is read-only. Agents may:

- geocode a place;
- reverse-geocode coordinates;
- find nearby infrastructure and points of interest;
- calculate routes and distance matrices;
- render map layers;
- return an ATG spatial receipt with provenance and authority boundaries.

Autonomous edits to OpenStreetMap are explicitly out of scope for Phase 001.

## Architecture

```text
Agent / Application
        |
        v
ATLAS MCP Gateway
        |
        +-- Geocode ------> Pelias / Nominatim
        +-- Search --------> PostGIS / Overpass
        +-- Route ---------> Valhalla / OSRM
        +-- Transit -------> OpenTripPlanner
        +-- Tiles ---------> PMTiles / Martin
        +-- Render --------> MapLibre GL JS
        +-- Analytics -----> DuckDB Spatial / GDAL
        |
        v
ATG Spatial Receipt + Audit Ledger
```

## Repository map

```text
docs/          architecture and open-source stack registry
policies/      authority, attribution and data-boundary rules
services/      MCP and geospatial service contracts
skills/        ATLAS CHAOS SKILL definitions
infrastructure deployment and self-hosting configuration
```

## Core principles

1. **Open data is not the same as free production infrastructure.** Public OSM endpoints are for responsible use, not unbounded agent traffic.
2. **Authority is geographic and explicit.** Every spatial action must remain inside its mandate and jurisdiction.
3. **Receipts are mandatory.** Every result records source, time, area, confidence and applicable attribution.
4. **Private operations remain separate from OSM-derived data.** They are joined at query time, not casually merged.
5. **Read before write.** Human review is required before any external map edit.

## License

The original software in this repository is licensed under Apache-2.0. Mapping data and third-party components retain their own licenses. OpenStreetMap-derived data requires ODbL attribution and may carry database share-alike obligations.

> Google Maps returns locations. ATLAS returns accountable spatial intelligence.
