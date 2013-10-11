# Track.py defines a python class that represents a track read from an iTunes XML Library file.
# Evan Radkoff

import re
import urllib
import hashlib # requires python 2.5 or later
from os import stat	# Used to read the size of song files

# After construction, the Track class maintains the following self variables with meta information:
# 	FileHash - MD5 hash checksum of the file contents (required)
# 	FilePath - The local file path of the track's file (required)
# 	Time - Total time of the track rounded down to the nearest second (required)
# 	Title - Track's title, not required.
# 	hasTitle - set to true if a track title was found
# 	Artist - Track's artist, not required.
# 	hasArtist - set to true if an artist was found
# 	Album - Track's album, not required.
# 	hasAblum - set to true if an album was found
class Track:
	stringRegex = '<string>(.+)</string>'	# Regular expression to extract XML string values
	
	def __init__(self, XMLdata):	# Initialization takes one parameter, the XML track info
		self.valid = True
		self.hasArtist = False
		self.hasTitle = False
		self.hasAlbum = False
		# Begin parsing XML track information line by line
		for line in XMLdata:
			# Title
			if re.search('<key>Name</key>', line):
				titleSearch = re.search(self.stringRegex, line)
				if titleSearch:		# If a title was found
					self.Title = titleSearch.group(1)
					self.hasTitle = True
			# Arist
			if re.search('<key>Artist</key>', line):
				artistSearch = re.search(self.stringRegex, line)
				if artistSearch:	# If an artist was found
					self.Artist = artistSearch.group(1)
					self.hasArtist = True
			# Album
			if re.search('<key>Album</key>', line):
				albumSearch = re.search(self.stringRegex, line)
				if albumSearch:		# If an album was found
					self.Album = albumSearch.group(1)
					self.hasAlbum = True
			# Total time
			if re.search('<key>Total Time</key>', line):
				timeSearch = re.search('<integer>(.+)</integer>', line)
				if timeSearch:
					self.Time = int(timeSearch.group(1)) / 1000
			# File location
			if re.search('<key>Location</key>', line):
				locationSearch = re.search(self.stringRegex, line)
				if locationSearch:
					# Use urllib to convert from a location URL to a file path
					self.FilePath = urllib.urlretrieve(locationSearch.group(1))[0]
					self.FileHash = self.computeHash()	# Set the MD5 hash

		try:	# Test that the track has a time. Else, set it to invalid
			self.Time	# If not set, this will cause an exception to be thrown
		except AttributeError:
			self.valid = False
	
	# computeHash takes a python file object and returns an MD5 checksum value.
	# Most music files have ID3 tag information at the beginning. Since these are analyzed
	#  separately, hashing begins part way into the file so that two identical songs will
	#  be seen as a match even if they have different tags.
	# On success - returns MD5 checksum
	# On failure (nonexistent or empty file) - sets self.valid to False, returns garbage
	def computeHash(self):
		try:
			fileObject = open(self.FilePath, 'rb')	# Attempt to open the file
		except:
			self.valid = False	# If the file doesn't exist, the track is invalid
			return 0
		if stat(self.FilePath).st_size == 0:
			self.valid = False
			return 0

		ID3offset = 40000	# How far to skip to avoid ID3 tags
		hashSize = 800000	# How many bytes are read for hashing
		hasher = hashlib.md5()
		
		hasherUpdated = False
		fileObject.seek(ID3offset)	# Skip ahead in the file
		byte = fileObject.read(1)	# Read a byte
		for i in range(hashSize):
			if byte == "":		# Reaching the end of file will trigger this
				break;
			hasher.update(byte)
			hasherUpdated = True
			byte = fileObject.read(1)	# read another byte

		if not hasherUpdated:	# If the file is smaller than ID3offset, hash the whole thing
			fileObject.seek(0)
			hasher.update(fileObject.read())
		
		return hasher.digest()

