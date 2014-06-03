#!/usr/bin/env python
"""
geojson2osm
Converts a GeoJSON shapefile to OSM XML. WIP PROBABLY BROKEN
Copyright 2014 Michael Farrell <http://micolous.id.au>

License: 3-clause BSD, see COPYING
"""

import geojson, argparse
import xml.etree.ElementTree as ET


def osmme(input_f, output_f, name_field, all_tags=False):
	output_dom = ET.Element('osm', dict(version='0.5', generator='geojson2osm'))

	layer = geojson.load(input_f, use_decimal=True)
	# Note: does not check CRS, assumes WGS84!

	for gid, point in enumerate(layer.features):
		# Only supports points!
		if point.geometry.type != 'Point':
			continue

		node = ET.SubElement(output_dom, 'node', dict(
			id=unicode(-gid),
			visible='true',
			lat=unicode(point.geometry.coordinates[1]),
			lon=unicode(point.geometry.coordinates[0])
		))

		ET.SubElement(node, 'tag', dict(k='name', v=unicode(point.properties[name_field])))
		ET.SubElement(node, 'tag', dict(k='note', v=unicode(point.properties[name_field])))

		# so that this doesn't show up in the output again.
		del point.properties[name_field]

		if all_tags:
			# write out other properties as custom tags
			for k, v in point.properties.iteritems():
				ET.SubElement(node, 'tag', dict(k=u'custom:' + k, v=unicode(v)))

	# write XML
	output_f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
	output_f.write(ET.tostring(output_dom, encoding='utf-8'))
	output_f.write('\n')
	output_f.close()


def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('input', nargs=1,
		type=argparse.FileType('rb'),
		help='Input GeoJSON file'
	)

	parser.add_argument('-o', '--output',
		required=True,
		type=argparse.FileType('wb'),
		help='Output OSM file'
	)

	parser.add_argument('-n', '--name-field',
		default='name',
		help='Field to use for the "name" tag [default: %(default)s]'
	)

	parser.add_argument('-a', '--all-tags',
		action='store_true',
		help='Include all properties of the GeoJSON file as tags'
	)

	options = parser.parse_args()

	osmme(options.input[0], options.output, options.name_field, options.all_tags)


if __name__ == '__main__':
	main()

