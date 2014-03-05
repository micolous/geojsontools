# geojsontools #

Some small tools to work with GeoJSON files, using the [python-geojson](https://github.com/frewsxcv/python-geojson) library.

## geojsondiff ##

Finds added and deleted points in two GeoJSON files.  Other types of geometry are ignored.

This matches points based on the `id` field by default, however may be changed to use other fields instead. (`-i`)

```
$ python geojsondiff.py -O points-2013.geojson -N points-2014.geojson -n AddedPoints.geojson -d DeletedPoints.geojson
```

## geojsonify ##

Given a JSON file with a list of points in it, convert to a GeoJSON file.

This assumes that the input file is in the WGS84 datum.  It reads latitude and longitude from a field like `lat`/`lon`/`lng`, and handles factorials (where fields are specified like `latE3`).

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

## geojsonmerge ##

Merges multiple GeoJSON files' geometries into a single GeoJSON file.

This matches geometries (not just points) based on the `id` field by default, however may be adapted to use a different field instead.

This supports all types of geometries, not just points.  The `id` field must be unique across all files and all geometry types.

For example, a LineString in one file with the same ID as a Point in another file, these would be treated as the same geometry and only the first geometry would be included in the output file.

```
$ python geojsonmerge.py -o all.geojson -i guid regions/*.geojson
```
