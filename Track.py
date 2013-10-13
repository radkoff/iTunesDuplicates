# Track.py defines a python class that represents a track read from an iTunes XML Library file.
# Evan Radkoff

import re
import urllib
import hashlib # requires python 2.5 or later
import os

'''
After construction, the Track class maintains the following meta information, extracted from XML tags
and kept in the self.tags dictionary with corresponding keys. 'required' means the track isn't
considered for duplicate-checking if not present (making self.valid==False)
	Name - Track's title, not required.
	Artist - Track's artist, not required.
	Album - Track's album, not required.
	Total Time - An int of the total time of the track rounded to the nearest second (required)
	Location - URL of the media file
	Rating - int 0-5
	Play Count - int
	Date Added - String of the date
It also maintians these self variables:
	valid
 	fileHash - MD5 hash checksum of the file contents (required)
 	filePath - The local UNIX file path of the track's file (required)
'''
class Track:
	
	def __init__(self, XMLdata):	# Initialization takes one parameter, the XML track info as a list
		self.tags = {}
		self.valid = True	# Potentially set to false by several functions, indicates the track is unfit for matching
		
		self.readXML(XMLdata)
		if 'Location' not in self.tags:
			self.valid = False
		# Convert the Total Time tag from a string of milliseconds to a rounded int of seconds
		if 'Total Time' in self.tags and self.tags['Total Time'] != '0':
			self.tags['Total Time'] = self.convertTime(self.tags['Total Time'])
		else:	# If it's absent, the Track isn't valid
			self.valid = False
		# Convert rating and play count to ints
		if 'Rating' in self.tags:
			# Convert from ratings of 0-100 to 0-5
			self.tags['Rating'] = int(self.tags['Rating']) / 20
		else:
			self.tags['Rating'] = 0
		# If there is no play count, set it to 0
		if 'Play Count' in self.tags:
			self.tags['Play Count'] = int(self.tags['Play Count'])
		else:
			self.tags['Play Count'] = 0
		# Trim date added from 2006-12-19T21:36:14Z to 2006-12-19
		if 'Date Added' in self.tags:
			date = self.tags['Date Added']
			self.tags['Date Added'] = date[:date.find('T')]

		if self.valid:
			# Store a local UNIX file path to the media instead of an HTML location
			self.filePath = self.convertURLtoPath(self.tags['Location'])
			# If the file does not have size 0, set the MD5 hash
			if self.filePath != '' and os.path.isfile(self.filePath) and os.stat(self.filePath).st_size > 0:
				self.fileHash = self.computeHash(open(self.filePath, 'rb'))
			else:
				self.valid = False


	# Parse XML track information line by line looking for certain values
	def readXML(self, XMLdata):
		for line in XMLdata:
			for key in ['Name','Artist','Album','Location']:
				self.extractTagOfKey(key, 'string', line)
			for key in ['Total Time', 'Rating', 'Play Count']:
				self.extractTagOfKey(key, 'integer', line)
			self.extractTagOfKey('Date Added', 'date', line)
	
	# Given something like ('Artist','string','<string>Modest Mouse</string>), this parses the artist name
	# and, if found and not blank, stores it in the self.tags dictionary as a string
	def extractTagOfKey(self, key, XMLtag, line):
		# If the line actually contains what we're looking for
		if re.search('<key>'+key+'</key>', line):
			search = re.search('<'+XMLtag+'>(.+)</'+XMLtag+'>', line)
			if search:
				self.tags[key] = search.group(1)
	
	# Converts from a string of milliseconds to an int of seconds (rounded)
	def convertTime(self, milliseconds):
		return int(round(int(milliseconds) / 1000.0))
	
	# Converts a URL style file name to a UNIX path. Returns '' on error
	def convertURLtoPath(self, fileURL):
		if fileURL == '' or fileURL == None:
			return ''
		else:
			try:
				return urllib.urlretrieve(fileURL)[0]
			except IOError:
				return ''
			
	
	# computeHash takes a python file object and returns an MD5 checksum value.
	# Most music files have ID3 tag information at the beginning. Since these are analyzed
	#  separately, hashing begins part way into the file so that two identical songs will
	#  be seen as a match even if they have different tags.
	# On success - returns MD5 checksum
	# On failure (nonexistent or empty file) - sets self.valid to False, returns garbage
	def computeHash(self, mediaFile):
		ID3offset = 40000	# How far to skip to avoid ID3 tags
		hashSize = 800000	# How many bytes are read for hashing
		hasher = hashlib.md5()
		
		hasherUpdated = False
		mediaFile.seek(ID3offset)	# Skip ahead in the file
		byte = mediaFile.read(1)	# Read a byte
		for i in range(hashSize):
			if byte == "":		# Reaching the end of file will trigger this
				break;
			hasher.update(byte)
			hasherUpdated = True
			byte = mediaFile.read(1)	# read another byte

		if not hasherUpdated:	# If the file is smaller than ID3offset, hash the whole thing
			mediaFile.seek(0)
			hasher.update(mediaFile.read())
		
		return hasher.digest()

