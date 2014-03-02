# geojsontools #

Some small tools to work with GeoJSON files, using the [python-geojson](https://github.com/frewsxcv/python-geojson) library.

## geojsondiff ##

Finds added and deleted points in two GeoJSON files.  Other types of geometry are ignored.

This matches points based on the `id` field by default, however may be changed to use other fields instead. (`-i`)

```
$ python geojsondiff.py -O points-2013.geojson -N points-2014.geojson -n AddedPoints.geojson -d DeletedPoints.geojson
```

## geojsonmerge ##

Merges multiple GeoJSON files' geometries into a single GeoJSON file.

This matches geometries (not just points) based on the `id` field by default, however may be adapted to use a different field instead.

This supports all types of geometries, not just points.  The `id` field must be unique across all files and all geometry types.

For example, a LineString in one file with the same ID as a Point in another file, these would be treated as the same geometry and only the first geometry would be included in the output file.

```
$ python geojsonmerge.py -o all.geojson -i guid regions/*.geojson
```
