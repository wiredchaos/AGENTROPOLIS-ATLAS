# ATLAS ROUTE

Name: ATLAS ROUTE
Role: Calculate a policy-bounded route and return its evidence receipt.
Tier: infrastructure

## Triggers

Activate when a user or agent asks to:

- route between approved locations;
- compare authorized travel options;
- calculate travel distance or duration;
- generate a route constrained by mode, boundary or policy.

## Requires

- authenticated agent identity;
- valid spatial mandate;
- approved Valhalla or OSRM endpoint;
- ATG receipt service;
- attribution configuration.

## Chain in

- ATLAS GEOCODE when endpoints are supplied as place names;
- ATLAS AUTHORITY before provider execution.

## Chain out

- ATLAS LAYER for map rendering;
- ATLAS RECEIPT for evidence and audit;
- human review when the route leaves the approved boundary or affects physical operations.

## Output

```json
{
  "status": "ok|denied|review",
  "route": {
    "geometry": null,
    "distance_meters": 0,
    "duration_seconds": 0,
    "mode": "drive|walk|bike|transit"
  },
  "authority": {
    "inside_boundary": true,
    "decision": "allow"
  },
  "sources": [],
  "attribution": [],
  "receipt": {}
}
```

## Example

Request: "Find the fastest approved driving route between two field sites without leaving Sacramento County."

Behavior: Resolve both sites, verify the county boundary mandate, calculate the route, reject or flag any route crossing the boundary, and return the selected geometry with an ATG spatial receipt.

## Safety boundary

A route is advisory evidence. It does not authorize trespass, emergency dispatch, regulatory action or physical intervention.
