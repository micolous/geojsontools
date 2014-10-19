# geojsontools #

Some small tools to work with GeoJSON files, using the [python-geojson](https://github.com/frewsxcv/python-geojson) library.

These typically focus on small utilities in order to convert data between different formats, or perform operations that are difficult or impossible to do inside of software like `gpsbabel`, `ogr2ogr` or QGIS.

## geojson2osm ##

Converts a GeoJSON file containing points into OpenStreetMap XML format.  This does not convert other types of geometry, and data from this tool will violate OSM's metadata schemas.  It is designed to target a subset for use by rendering and routing applications.

For example, you may have a GeoJSON file containing a list of geocaches in your area which you wish to use with an application that uses OSM XML format:

```console
$ python geojson2osm.py -n cache_name geocaches-2014-06-01.geojson -o geocaches-pre-2014-06-01.osm
```

You can then annotate these points appropriately with a tool like `gpsbabel`, by having a user-defined point type to select on.

```console
$ gpsbabel -i osm -f geocaches-pre-2014-06-01.osm -o osm,tagnd="user_defined:geocache",created_by -F geocaches-2014-06-01.osm
```

And then this file can be used with other map creation software or tile renderers that read OSM XML format.

## geojsondiff ##

Finds added and deleted points in two GeoJSON files.  Other types of geometry are ignored.

This matches points based on the `id` field by default, however may be changed to use other fields instead. (`-i`)

```console
$ python geojsondiff.py -O points-2013.geojson -N points-2014.geojson -n AddedPoints.geojson -d DeletedPoints.geojson
```

## geojsonify ##

Given a JSON file with a list of points in it, convert to a GeoJSON file.  This aims to be able to read simple JSON point file formats that are made of an array of points.

This assumes that the input file is in the WGS84 datum.  It reads latitude and longitude from a field like `lat`/`lon`/`lng`, and handles scientific notation (where fields are specified like `latE3`).

The input data parses and writes the latitude and longitude as a `Decimal` type, not `float`, so there should not be a loss of precision.  However, some other software may not respect this, and loose precision by converting the values to floating-point, and even JavaScript itself defines numbers as a 64-bit floating point type.

Other properties on points in the GeoJSON file are made available as properties on the `Feature`.

For example, you might have a JSON file like this:

```json
[
	{"lat": -34.93, "long": 138.60, "name": "Adelaide"},
	{"lat": -37.81, "long": 144.95, "name": "Melbourne"}
]
```

This can be transformed with:

```
$ python geojsonify.py -o points.geojson points.json
```

And becomes:

```json
{
    "crs": {
        "properties": "urn:ogc:def:crs:OGC:1.3:CRS84",
        "type": "name"
    },
    "features": [
        {
            "geometry": {
                "coordinates": [138.6, -34.93],
                "type": "Point"
            },
            "id": "3245acc2-5d3a-43b3-9ecb-6e49ca763622",
            "properties": {
                "name": "Adelaide",
                "uuid": "3245acc2-5d3a-43b3-9ecb-6e49ca763622"
            },
            "type": "Feature"
        },
        {
            "geometry": {
                "coordinates": [144.95, -37.81],
                "type": "Point"
            },
            "id": "a4fb85ce-42a5-4a68-9150-2ece4cd6ce18",
            "properties": {
                "name": "Melbourne",
                "uuid": "a4fb85ce-42a5-4a68-9150-2ece4cd6ce18"
            },
            "type": "Feature"
        }
    ],
    "type": "FeatureCollection"
}
```

This will also attempt to search for a `id`, `uuid` or `guid` field and use this to populate the `id` field on the Feature.  If not present, a random UUID (`uuid4`) will be generated for each Feature and included in the Feature and in it's properties.

Some GIS software doesn't read the `id` field of the Feature, so it is included in the properties for good measure.  This also means that if the wrong field is automatically chosen, it doesn't matter as much.

## geojsonjoin ##

Merges the properties of two GeoJSON files.

This allows a side-by-side comparison of properties (not geometries) of geometries inside of two GeoJSON files, matching by a designated ID field.

For example, you may have a GeoJSON files describing traffic conditions at two different times, and wish to merge this data so that the information from both is shown at the same time:

```console
$ python geojsonjoin.py -n -o comparison-Oct-Nov-2013.geojson -O Oct13_ -N Nov13_ traffic-2013-10-01.geojson traffic-2013-11-01.geojson
```

This can then allow traditional GIS software to filter and categorise information based on differences or similarities between the two sets of metadata on the geometries.

Note: This doesn't compare changes in geometry between the versions.

## geojsonmerge ##

Merges multiple GeoJSON files' geometries into a single GeoJSON file.

This can behave in several ways:

- Add all geometries in with no regard for duplicates. (`-n`)
- Match by the "id" field in the geometry. (`-i`)
- Match by a particular property of the geometry. (`-f id`)

This supports all types of geometries, not just points.  The chosen field must be unique across all files and all geometry types.

For example, a LineString in one file with the same ID as a Point in another file, these would be treated as the same geometry and only the first geometry would be included in the output file.

```console
$ python geojsonmerge.py -o all.geojson -f guid regions/*.geojson
```

## gtfs2geojson ##

Converts data from [Google Transit Feed Specification (GTFS)](https://developers.google.com/transit/gtfs/) format into GeoJSON format.

This tool can transform routes (using `routes.txt`, `shapes.txt` and `trips.txt`) into a collection of LineStrings, and transform stops (using `stops.txt`) into a collection of Points.

For routes, in the case that multiple shapes exist for the same route, this tool will select the shape that has the most references in `trips.txt`.  This can mean that a more-frequent shortened route with the same route number as a longer route can sometimes display instead of the longer route.  This was selected as sometimes geometries are broken for routes with more points.

The `shape_id` and number of references it had is included as properties in the output GeoJSON geometries (as `shape_id` and `shape_refs` to aid debugging bad source data.

Google [has a list of transit authorities that provide GTFS data](https://code.google.com/p/googletransitdatafeed/wiki/PublicFeeds).  Most authorities provide this freely to anyone without registration, while others require registration and a license agreement be signed and returned to them.

For example, in order to create GeoJSON shape files describing the stops and routes of [Adelaide Metro's](http://www.adelaidemetro.com.au) services:

```console
$ wget http://adelaidemetro.com.au/GTFS/google_transit.zip
$ mkdir metro
$ cd metro
$ unzip ../google_transit.zip
$ python ../gtfs2geojson.py -o AdelaideMetro-routes.geojson -r routes.txt -s shapes.txt -t trips.txt
$ python ../gtfs2geojson.py -o AdelaideMetro-stops.geojson -p stops.txt
```

### marking up gtfs-converted data ###

This can then be marked up with some various rules in QGIS.  For colours, use a data defined property like:

```
CONCAT('#', "route_color")
```

This will add a `#` character to the start of the colours so that Qt will recognise the hexadecimal colours from `routes.txt` correctly.

For labels, use a data defined property like this, in order to add Unicode icons for each of the transport types.  Note that you'll require Unicode 6.0 support and a font that includes the "Transport and Map Symbols" block.

```
CONCAT((CASE 
WHEN "route_type" = '0' THEN '🚊'
WHEN "route_type" = '1' THEN '🚇'
WHEN "route_type" = '2' THEN '🚆'
WHEN "route_type" = '3' THEN '🚍'
WHEN "route_type" = '4' THEN '🚢'
WHEN "route_type" = '5' THEN '🚃'
WHEN "route_type" = '6' THEN '🚟'
WHEN "route_type" = '7' THEN '🚞'
END), ' ', CASE
WHEN "route_short_name" THEN "route_short_name"
ELSE "route_long_name"
END
)
```

After some other minor tweaks, QGIS will give you output that looks like this:

![Adelaide Metro route map](/examples/adelaidemetro.png?raw=true)


