#!/usr/bin/env python
"""
Finds the differences in points between two GeoJSON files
Copyright 2014 Michael Farrell <http://micolous.id.au>

License: 3-clause BSD, see COPYING
"""

import geojson, argparse

def loadpoints(layer):
	points = {}
	for point in layer:
		if point.geometry.type != 'Point':
			continue
		
		# we have a point, load it up
		points[point.properties['guid']] = point
	
	return points


def diffme(original_file, new_file, new_points_f, deleted_points_f, id_field):
	original = geojson.load(original_file)
	new = geojson.load(new_file)
	
	# Load all the points into a dict
	original_layer = loadpoints(original.features)
	new_layer = loadpoints(new.features)
	
	# Find all the points that were added
	original_guids = set(original_layer.keys())
	new_guids = set(new_layer.keys())
	
	added_guids = new_guids - original_guids
	new_points = geojson.FeatureCollection([])
	new_points.crs = new.crs
	new_points.features = filter((lambda x: x.properties[id_field] in added_guids), new.features)
	geojson.dump(new_points, new_points_f)
	new_points_f.close()

	deleted_guids = original_guids - new_guids	
	deleted_points = geojson.FeatureCollection([])
	deleted_points.crs = original.crs
	deleted_points.features = filter((lambda x: x.properties[id_field] in deleted_guids), original.features)
	geojson.dump(deleted_points, deleted_points_f)
	deleted_points_f.close()
		
	# TODO: check differences
	

def main():
	parser = argparse.ArgumentParser()
	
	parser.add_argument('-O', '--original', required=True, type=argparse.FileType('rb'), help='Original file')
	parser.add_argument('-N', '--new', required=True, type=argparse.FileType('rb'), help='New file')
	parser.add_argument('-i', '--id-field', required=True, default='id', help='Field to check for when watching points that have changed  (default: %(default)s)')
	
	parser.add_argument('-n', '--new-points', required=True, type=argparse.FileType('wb'), help='Where to write new points')
	parser.add_argument('-d', '--deleted-points', required=True, type=argparse.FileType('wb'), help='Where to write deleted points')
	#parser.add_argument('-c', '--changed-points', required=True, type=argparse.FileType('wb'), help='Where to write changed points')
	
	options = parser.parse_args()
	
	diffme(options.original, options.new, options.new_points, options.deleted_points, options.id_field)

if __name__ == '__main__':
	main()
