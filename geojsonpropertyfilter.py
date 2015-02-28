#!/usr/bin/env python
"""
geojsonpropertyfilter
Filters GeoJSON Feature properties to a subset
Copyright 2014-2015 Michael Farrell <http://micolous.id.au>

License: 3-clause BSD, see COPYING
"""

import geojson, argparse

def propertyfilterme(original_file, output_file, allowed_properties):
	original = geojson.load(original_file)
	output = geojson.FeatureCollection([])
	output.crs = original.crs
	allowed_properties = [x.lower() for x in allowed_properties]
	
	for feature in original.features:
		for k in feature.properties.keys():
			if k.lower() not in allowed_properties:
				del feature.properties[k]
		output.features.append(feature)

	geojson.dump(output, output_file)


def main():
	parser = argparse.ArgumentParser()
	
	parser.add_argument('input', nargs=1, type=argparse.FileType('rb'), help='Input file')
	parser.add_argument('-o', '--output', required=True, type=argparse.FileType('wb'), help='Output file')

	parser.add_argument('fields', nargs='*', help='Fields to keep in the output file.')
	options = parser.parse_args()
	
	propertyfilterme(options.input[0], options.output, options.fields)

if __name__ == '__main__':
	main()

