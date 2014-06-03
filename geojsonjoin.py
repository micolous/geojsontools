#!/usr/bin/env python
"""
geojsonjoin
Join attributes across points in different GeoJSON files.
Copyright 2014 Michael Farrell <http://micolous.id.au>

License: 3-clause BSD, see COPYING
"""

import geojson, argparse

def loadpoints(layer, id_field):
	points = {}
	for point in layer:
		# we have a point, load it up
		points[point.properties[id_field]] = point

	return points


def joinme(original_file, new_file, output_f, id_field, exclude_original_only=False, include_new_only=False, original_prefix='old_', new_prefix='new_'):
	original = geojson.load(original_file)
	new = geojson.load(new_file)

	# Load all the points into a dict
	original_layer = loadpoints(original.features, id_field)
	new_layer = loadpoints(new.features, id_field)

	output_layer = geojson.FeatureCollection([])
	output_layer.crs = original.crs

	for feature in original.features:
		if exclude_original_only and feature.properties[id_field] not in new_layer:
			# feature is missing from new file.
			continue

		output_layer.features.append(feature)

		old_properties = {}
		for k, v in feature.properties.iteritems():
			if k == id_field:
				old_properties[k] = v
			else:
				old_properties[original_prefix + k] = v

		feature.properties = old_properties

		# Add in "new" properties if they exist
		if feature.properties[id_field] in new_layer:
			for k, v in new_layer[feature.properties[id_field]].properties.iteritems():
				if k == id_field:
					continue

				feature.properties[new_prefix + k] = v

	if include_new_only:
		for feature in new.features:
			if feature.properties[id_field] not in original_layer:
				properties = {}
				for k, v in feature.properties.iteritems():
					properties[new_prefix + k] = v

				feature.properties = properties
				output_layer.features.append(feature)

	# now dump the resulting file
	geojson.dump(output_layer, output_f)
	output_f.close()


def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('original',
		type=argparse.FileType('rb'),
		help='Original (first) file to join into'
	)

	parser.add_argument('new',
		type=argparse.FileType('rb'),
		help='New (second) file to join fields from'
	)

	parser.add_argument('-i', '--id-field',
		required=True,
		default='id',
		help='Field to match points with  (default: %(default)s)'
	)

	parser.add_argument('-o', '--output',
		required=True,
		type=argparse.FileType('wb'),
		help='Where to write the joined file.'
	)

	parser.add_argument('-r', '--exclude-original-only',
		action='store_true',
		help='If set, this will exclude geometries from the "original" file that do not also appear in the "new" file.'
	)

	parser.add_argument('-n', '--include-new-only',
		action='store_true',
		help='If set, this will include geometries from the "new" file that have no matching entry in the "original" file.  If unset, geometries that only appear in the "new" file will never be included.'
	)

	parser.add_argument('-O', '--original-prefix',
		default='old_',
		help='Prefix for properties coming from the old file. [default: %(default)s]'
	)

	parser.add_argument('-N', '--new-prefix',
		default='new_',
		help='Prefix for properties coming from the new file. [default: %(default)s]'
	)

	options = parser.parse_args()

	joinme(options.original, options.new, options.output, options.id_field, options.exclude_original_only, options.include_new_only,  options.original_prefix, options.new_prefix)

if __name__ == '__main__':
	main()
