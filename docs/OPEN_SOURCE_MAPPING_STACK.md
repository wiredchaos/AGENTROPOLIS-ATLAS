# Open-Source Mapping Stack Registry

This registry identifies production-relevant open-source tools that can replace Google Maps capabilities without creating a new single-vendor dependency.

## Selected default stack

| Capability | Default | Alternatives |
|---|---|---|
| Web rendering | MapLibre GL JS | Leaflet, OpenLayers |
| Native/mobile | MapLibre Native | Tangram ES forks, platform SDKs |
| 3D globe | CesiumJS | deck.gl, Three.js integrations |
| Spatial database | PostgreSQL + PostGIS | SpatiaLite, GeoPackage |
| Local analytics | DuckDB Spatial | GeoPandas, Apache Sedona |
| OSM import | osm2pgsql | imposm3 |
| Basemap generation | Planetiler | tilemaker, OpenMapTiles tooling |
| Custom vector tiles | Tippecanoe | GDAL, ogr2ogr pipelines |
| Static tile archive | PMTiles | MBTiles |
| Dynamic tile server | Martin | Tegola, pg_tileserv, t-rex |
| Geocoding | Pelias | Nominatim, Photon |
| Address parsing | libpostal | custom normalization |
| General routing | Valhalla | GraphHopper, openrouteservice engine |
| Fast road matrix | OSRM | Valhalla matrix, GraphHopper |
| Transit | OpenTripPlanner | MOTIS |
| OSM feature queries | PostGIS | self-hosted Overpass API |
| GIS server | GeoServer | QGIS Server, MapServer, pygeoapi |
| Styling | Maputnik | custom MapLibre style tooling |
| Drawing/editing | Terra Draw | Leaflet-Geoman, OpenLayers interactions |
| OSM editing | iD, JOSM | Vespucci, StreetComplete |
| Street imagery | Panoramax | KartaView |
| Raster processing | GDAL | Rasterio |
| Traffic simulation | SUMO | MATSim |

## Capability groups

### Rendering
- MapLibre GL JS
- MapLibre Native
- Leaflet
- OpenLayers
- CesiumJS
- deck.gl
- TerriaJS

### Data and tiles
- OpenStreetMap extracts
- Planetiler
- OpenMapTiles
- Protomaps Basemap
- tilemaker
- Tippecanoe
- PMTiles
- MBTiles
- Martin
- Tegola
- pg_tileserv
- t-rex
- TileServer GL

### Search and geocoding
- Pelias
- Nominatim
- Photon
- libpostal
- PostGIS full-text and spatial search
- self-hosted Overpass API

### Routing and mobility
- Valhalla
- OSRM
- GraphHopper
- openrouteservice engine
- pgRouting
- BRouter
- OpenTripPlanner
- MOTIS

### Spatial infrastructure
- PostgreSQL/PostGIS
- DuckDB Spatial
- GDAL/OGR
- GeoParquet
- GeoPackage
- SpatiaLite
- Apache Sedona
- GeoMesa

### GIS services and standards
- GeoServer
- QGIS Server
- MapServer
- pygeoapi
- deegree
- MapProxy
- GeoWebCache

### Editing and field mapping
- iD Editor
- JOSM
- Vespucci
- StreetComplete
- QGIS Desktop
- Terra Draw
- Maputnik

### Imagery and simulation
- Panoramax
- KartaView
- SUMO
- MATSim

## Production warning

Open-source software does not make public community servers an unlimited backend. Production deployments must self-host or contract for capacity when agents generate sustained geocoding, tile, routing or Overpass traffic.

ATLAS should treat public endpoints as development fallbacks only and expose every provider through configurable adapters.
