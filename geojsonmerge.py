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


def mergeme(inputs, output, id_field):
	known_ids = set()
	crs = None
	output_layer = geojson.FeatureCollection([])

	# Flatten the list of inputs
	inputs = list(itertools.chain.from_iterable(inputs))
	
	for i, layer_f in enumerate(inputs):
		print "Processing input file #%d..." % i
		layer = geojson.load(layer_f)
		
		# FIXME: this requires the CRS be specified on a "layer" level.  GeoJSON allows this to be ommitted, and this should include a check to ensure it is ommitted for all in this case.
		#
		# We don't care about per-geometry CRS, these can mingle
		if i == 0:
			# first file sets the CRS!
			crs = layer.crs.properties['name']
			output_layer.crs = layer.crs
		else:
			assert layer.crs.properties['name'] == crs, ('CRS of files must match.  File has CRS %r, expected %r' % (layer.crs.properties['name'], crs))
		
		# We have a matching CRS, start merging geometries.
		for geometry in layer.features:
			if geometry.properties[id_field] in known_ids:
				# Geometry is already present, skip
				continue
			
			# Geometry is new, add to list
			output_layer.features.append(geometry)
			known_ids.add(geometry.properties[id_field])

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
	
	parser.add_argument('-i', '--id-field',
		required=True,
		default='id',
		help='Field to use when merging features in order to drop duplicate geometries (default: %(default)s)'
	)
	
	options = parser.parse_args()
	
	mergeme(options.inputs, options.output, options.id_field)
	
if __name__ == '__main__':
	main()
