# ATLAS MCP Gateway

The ATLAS MCP Gateway is the governed interface between agents and geospatial providers.

## Phase 001 tools

| Tool | Purpose | Default adapter |
|---|---|---|
| `atlas_geocode` | Resolve a place or address | Pelias |
| `atlas_reverse` | Resolve coordinates to nearby named features | Pelias or Nominatim |
| `atlas_nearby` | Find authorized nearby infrastructure | PostGIS |
| `atlas_route` | Calculate a constrained route | Valhalla |
| `atlas_matrix` | Calculate travel-time and distance matrices | OSRM |
| `atlas_feature_query` | Query OSM-derived features | PostGIS or Overpass |
| `atlas_receipt` | Return a signed spatial evidence record | ATG receipt service |

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

All provider URLs must be configurable. Public community endpoints are development fallbacks, not production defaults.

```env
ATLAS_POSTGIS_URL=
ATLAS_PELIAS_URL=
ATLAS_NOMINATIM_URL=
ATLAS_VALHALLA_URL=
ATLAS_OSRM_URL=
ATLAS_OVERPASS_URL=
ATLAS_MARTIN_URL=
ATLAS_PMtiles_URL=
```

## Non-goals

- no Google Maps dependency;
- no autonomous OSM edits;
- no silent fallback to unapproved providers;
- no result without source and attribution metadata;
- no query outside the declared authority geometry.
