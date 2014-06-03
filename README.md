# geojsontools #

Some small tools to work with GeoJSON files, using the [python-geojson](https://github.com/frewsxcv/python-geojson) library.

These typically focus on small utilities in order to convert data between different formats, or perform operations that are difficult or impossible to do inside of software like `ogr2ogr` or QGIS.

## geojsondiff ##

Finds added and deleted points in two GeoJSON files.  Other types of geometry are ignored.

This matches points based on the `id` field by default, however may be changed to use other fields instead. (`-i`)

```
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

This matches geometries (not just points) based on the `id` field by default, however may be adapted to use a different field instead.

This supports all types of geometries, not just points.  The `id` field must be unique across all files and all geometry types.

For example, a LineString in one file with the same ID as a Point in another file, these would be treated as the same geometry and only the first geometry would be included in the output file.

```console
$ python geojsonmerge.py -o all.geojson -i guid regions/*.geojson
```

## gtfs2geojson ##

Converts data from [Google Transit Feed Specification (GTFS)](https://developers.google.com/transit/gtfs/) format into GeoJSON format.

This tool can transform routes (using `routes.txt`, `shapes.txt` and `trips.txt`) into a collection of LineStrings, and transform stops (using `stops.txt`) into a collection of Points.

For routes, in the case that multiple shapes exist for the same route, this tool will select the shape with the most points.  This particularly applies to services which start or finish prematurely -- the longer route will always be shown instead.

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

