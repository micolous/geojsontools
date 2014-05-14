#!/usr/bin/env python
"""
gtfs2geojson
Converts GTFS data into GeoJSON format
Copyright 2014 Michael Farrell <http://micolous.id.au>

License: 3-clause BSD, see COPYING
"""

import geojson, argparse, csv
from decimal import Decimal

def gtfs_stops(stops_f, output_f):
	"""
	For each stop, convert it into a GeoJSON Point, and make all of it's attributes available.
	
	:param stops_f file: Input 'stops.txt' file from the GTFS feed.
	:param output_f file: Output GeoJSON file stream.
	"""
	stops_c = csv.reader(stops_f)

	output_layer = geojson.FeatureCollection([])
	# assume WGS84 CRS
	output_layer.crs = geojson.crs.Named('urn:ogc:def:crs:OGC:1.3:CRS84')

	header = stops_c.next()
	lat_col = header.index('stop_lat')
	lng_col = header.index('stop_lon')
	id_col = header.index('stop_id')

	for row in stops_c:
		lat, lng = Decimal(row[lat_col]), Decimal(row[lng_col])

		# make dict of other properties
		props = dict()
		for i, h in enumerate(header):
			if h in ('stop_lat', 'stop_lon'):
				continue

			if row[i] != '':
				props[h] = row[i]

		output_layer.features.append(geojson.Feature(
			geometry=geojson.Point(
				coordinates=(lng, lat)
			),
			properties=props,
			id=row[id_col]
		))
	
	geojson.dump(output_layer, output_f)



def gtfs_routes(routes_f, shapes_f, output_f):
	"""
	For each route, convert it's 'shape' into a GeoJSON LineString, and make all
	of it's attributes available.
	
	:param routes_f file: Input 'routes.txt' file from the GTFS feed.
	:param shapes_f file: Input 'shapes.txt' file from the GTFS feed.
	:param output_f file: Output GeoJSON file stream.
	
	"""
	print 'not implemented yet'



def main():
	parser = argparse.ArgumentParser()
	
	parser.add_argument('-o', '--output',
		required=True,
		type=argparse.FileType('wb'),
		help='Output GeoJSON file'
	)

	group = parser.add_argument_group(title='Route conversion')
	group.add_argument('-r', '--routes',
		type=argparse.FileType('rb'),
		help='Path to agency\'s `routes.txt` file.'
	)

	group.add_argument('-s', '--shapes',
		type=argparse.FileType('rb'),
		help='Path to agency\'s `shapes.txt` file.'
	)


	group = parser.add_argument_group(title='Stop conversion')
	group.add_argument('-t', '--stops',
		type=argparse.FileType('rb'),
		help='Path to agency\'s `stops.txt` file.'
	)

	options = parser.parse_args()

	if options.routes and not options.stops:
		gtfs_routes(options.routes, options.shapes, options.output)
	elif options.stops and not options.routes:
		gtfs_stops(options.stops, options.output)
	else:
		print 'invalid options combination'


if __name__ == '__main__':
	main()

