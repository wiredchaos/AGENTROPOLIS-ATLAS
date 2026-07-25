# Spatial Authority Policy

ATLAS does not treat geographic access as implied permission.

## Required mandate fields

Every agent request must declare:

- agent identity;
- principal or delegating authority;
- permitted operation;
- geographic boundary;
- data classes allowed;
- validity window;
- maximum query cost or rate;
- required review level.

## Enforcement rules

1. Requests outside the mandate boundary are denied before provider execution.
2. Coordinates, routes and features must be clipped or filtered to the authorized geometry.
3. Sensitive private layers are denied unless explicitly named in the mandate.
4. Public OSM data may inform a result but does not grant authority to act in the physical world.
5. External map edits require human approval and a separate write mandate.
6. Provider responses are evidence, not unquestionable truth.

## Minimum receipt

```json
{
  "receipt_type": "atg.spatial.v1",
  "agent_id": "agent:example",
  "principal_id": "principal:example",
  "operation": "atlas.route",
  "authority_geometry": {
    "type": "Polygon",
    "coordinates": []
  },
  "requested_at": "RFC3339 timestamp",
  "sources": [],
  "result_confidence": 0.0,
  "attribution": [],
  "policy_decision": "allow|deny|review",
  "reason": ""
}
```

## Phase 001 boundary

Phase 001 is read-only. It may search, calculate, compare and render. It may not publish edits to OpenStreetMap, alter municipal systems, dispatch physical resources or claim legal jurisdiction.
