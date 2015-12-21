#!/usr/bin/env python
"""
geojsondiff
Finds the differences in points between two GeoJSON files
Copyright 2014-2015 Michael Farrell <http://micolous.id.au>

License: 3-clause BSD, see COPYING
"""

import geojson, argparse

def hash_coords(lng, lat=None, *args):
	if lat is None:
		print lng
		raise Exception
	return '%s,%s' % (lng, lat)

def loadpoints(layer, id_field):
	points = {}
	for point in layer:
		if point.geometry.type != 'Point':
			continue
		
		# we have a point, load it up
		if id_field is None:
			# match on geometry instead
			points[hash_coords(*point.geometry.coordinates)] = point
		else:
			points[point.properties[id_field]] = point
	
	return points


def diffme(original_file, new_file, new_points_f, deleted_points_f, id_field):
	original = geojson.load(original_file)
	new = geojson.load(new_file)

	# Load all the points into a dict
	original_layer = loadpoints(original.features, id_field)
	new_layer = loadpoints(new.features, id_field)

	# TODO: Check that CRS is identical.

	# Find all the points that were added
	original_guids = set(original_layer.keys())
	new_guids = set(new_layer.keys())

	added_guids = new_guids - original_guids
	new_points = geojson.FeatureCollection([])
	new_points.crs = new.crs
	if id_field is None:
		new_points.features = filter((lambda x: hash_coords(*x.geometry.coordinates) in added_guids), new.features)		
	else:
		new_points.features = filter((lambda x: x.properties[id_field] in added_guids), new.features)
	geojson.dump(new_points, new_points_f)
	new_points_f.close()

	deleted_guids = original_guids - new_guids	
	deleted_points = geojson.FeatureCollection([])
	deleted_points.crs = original.crs
	if id_field is None:
		deleted_points.features = filter((lambda x: hash_coords(*x.geometry.coordinates) in deleted_guids), original.features)
	else:
		deleted_points.features = filter((lambda x: x.properties[id_field] in deleted_guids), original.features)
	geojson.dump(deleted_points, deleted_points_f)
	deleted_points_f.close()
		
	# TODO: check differences
	

def main():
	parser = argparse.ArgumentParser()
	
	parser.add_argument('-O', '--original', required=True, type=argparse.FileType('rb'), help='Original file')
	parser.add_argument('-N', '--new', required=True, type=argparse.FileType('rb'), help='New file')
	
	parser.add_argument('-n', '--new-points', required=True, type=argparse.FileType('wb'), help='Where to write new points')
	parser.add_argument('-d', '--deleted-points', required=True, type=argparse.FileType('wb'), help='Where to write deleted points')
	#parser.add_argument('-c', '--changed-points', required=True, type=argparse.FileType('wb'), help='Where to write changed points')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-i', '--id-field', default='id', help='Field to check for when watching points that have changed  (default: %(default)s)')
	group.add_argument('-g', '--geometry', action='store_true', help='Match points on geometry instead of properties')
	
	options = parser.parse_args()
	
	diffme(options.original, options.new, options.new_points, options.deleted_points, None if options.geometry else options.id_field)

if __name__ == '__main__':
	main()
