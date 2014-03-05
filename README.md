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
	{"lat": -34.99, "long": 138.51, "name": "A"},
	{"lat": -35.04, "long": 138.42, "name": "B"}
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
                "coordinates": [
                    138.51,
                    -34.99
                ],
                "type": "Point"
            },
            "id": "7d9f10b7-1d95-464e-ad68-2f9859912151",
            "properties": {
                "name": "A",
                "uuid": "7d9f10b7-1d95-464e-ad68-2f9859912151"
            },
            "type": "Feature"
        },
        {
            "geometry": {
                "coordinates": [
                    138.42,
                    -35.04
                ],
                "type": "Point"
            },
            "id": "1e8b5fd0-7363-4272-9279-ac1c0ab0b5b3",
            "properties": {
                "name": "B",
                "uuid": "1e8b5fd0-7363-4272-9279-ac1c0ab0b5b3"
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
