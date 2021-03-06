#!/usr/bin/env python
"""
geojsonmerge
Merges multiple GeoJSON files into one.
Copyright 2014 Michael Farrell <http://micolous.id.au>

License: 3-clause BSD, see COPYING
"""

import geojson, argparse, glob, itertools

class GlobbingFileType(argparse.FileType):
	"""
	Emulate behaviour of UNIX shells on Win32 to allow wildcarded arguments to be passed (glob-expansion).

	This only works with files opened for reading, and globs will be ignored for files not opened for reading.

	This will have the side-effect of not allowing filenames to be passed that contain an asterisk (``*``).

	This means that every ``file`` object returned is in a list, even if there is only one entry.  As a result, some cleanup of the options returned may be required to "flatten" this list::
	
		options = parser.parse_args()
		input_files = list(itertools.chain.from_iterable(options.inputs))
	"""
	def __call__(self, string):
		if string != '-' and '*' in string and 'r' in self._mode:
			# There is a glob in here, and we're reading the file
			# Expand!
			return [super(GlobbingFileType, self).__call__(fn) for fn in glob.glob(string)]
			
		# Fall back to normal behaviour, but put it in a 1-item list
		return [super(GlobbingFileType, self).__call__(string)]


def mergeme(inputs, output, no_dupe_handling, id_field, id_property):
	if no_dupe_handling:
		assert (not id_field) and (not id_property)
	else:
		assert (not id_field) or (not id_property)
		assert not (id_field and id_property)

	known_ids = set()
	crs = None
	output_layer = geojson.FeatureCollection([])

	# Flatten the list of inputs
	inputs = list(itertools.chain.from_iterable(inputs))
	
	for i, layer_f in enumerate(inputs):
		print "Processing input file #%d..." % i
		layer = geojson.load(layer_f)
		# FIXME: this requires the CRS be specified on a "layer" level.  GeoJSON allows this to be ommitted, and this should include a check to ensure it is ommitted for all in this case.

		# Some broken GeoJSON files do weird things...
		if isinstance(layer.crs, list):
			layer.crs = layer.crs[0]
		if isinstance(layer.crs.properties, list):
			newprops = {}
			for x in range(len(layer.crs.properties)/2):
				newprops[layer.crs.properties[x*2]] = layer.crs.properties[(x*2) + 1]
			layer.crs.properties = newprops

		# We don't care about per-geometry CRS, these can mingle
		if i == 0:
			# first file sets the CRS!
			crs = layer.crs.properties['name']
			output_layer.crs = layer.crs
		else:
			assert layer.crs.properties['name'] == crs, ('CRS of files must match.  File has CRS %r, expected %r' % (layer.crs.properties['name'], crs))
		
		# We have a matching CRS, start merging geometries.
		for geometry in layer.features:
			if not no_dupe_handling:
				if id_property and geometry.properties[id_property] in known_ids:
					# Geometry is already present, skip
					continue
				elif id_field and geometry.id in known_ids:
					# Geometry is already present, skip
					continue
			
			# Geometry is new, add to list
			output_layer.features.append(geometry)
			if id_property:
				known_ids.add(geometry.properties[id_property])
			elif id_field:
				known_ids.add(geometry.id)

		print "OK! (%d total geometries written, %d read from this file)" % (len(output_layer.features), len(layer.features))
	
	# all files complete
	geojson.dump(output_layer, output)
	print "Files merged!"


def main():
	parser = argparse.ArgumentParser()
	
	parser.add_argument('inputs', nargs='+',
		type=GlobbingFileType('rb'),
		help='Input GeoJSON file(s) to merge'
	)
	
	parser.add_argument('-o', '--output',
		required=True,
		type=argparse.FileType('wb'),
		help='Output GeoJSON file'
	)
	
	group = parser.add_mutually_exclusive_group()
	
	group.add_argument('-n', '--no-dupe-handling',
		action='store_true',
		help='Do not attempt to handle duplicate geometries specially.'
	)

	group.add_argument('-i', '--id-field',
		action='store_true',
		help='Match duplicate geometries by their id field.'
	)

	group.add_argument('-p', '--id-property',
		help='Field to use when merging features in order to drop duplicate geometries.'
	)
	
	options = parser.parse_args()
	
	mergeme(options.inputs, options.output, options.no_dupe_handling, options.id_field, options.id_property)
	
if __name__ == '__main__':
	main()
