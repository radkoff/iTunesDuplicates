# iTunesDuplicates.py analyzes an iTunes Library and identifies duplicate tracks (Mac OSX only)
# 
# Use it by providing your XML iTunes Library file as an argument (this file is usually in ~/Music/iTunes/)
# If the files of two tracks generate identical MD5 hashes, they are reported as sure duplicates.
# Otherwise, different combinations of matching track titles, artists, albums, and times are used
#  to come up with an estimate for how likely the songs are the same.
# Sample output for what this script generates can be found in "Sample Output.txt"
#
# Evan Radkoff 2013

from Track import Track		# Track.py
import sys
import re

# Check for arg, else print directions
if len(sys.argv) < 2:
	print "Usage: python",sys.argv[0],"path_to_XML_library_file"
	print "In Mac OSX, XML library files are usually found in ~/Music/iTunes/"
	exit()

XMLfile = sys.argv[1]

try:	# Attempt to read the XML library file
	fileObject = open(XMLfile, 'r')
except:
	print XMLfile,"not found or unable to be opened."
	exit()

XMLdata = fileObject.read().split('\n')		# XMLdata is a list of lines within the XML file
fileObject.close()

print "Finding duplicate songs in",XMLfile

# Compares two strings (track titles, artists, or albums)
def compareStrings(stringA, stringB):
	return stringA.strip().lower() == stringB.strip().lower()

# Compares two track times (given in seconds)
def compareTimes(timeA, timeB):
	return abs(timeA - timeB) <= 1

# Function to compare two Track objects.
# Returns a number from 0-100 representing an estimated similarity metric of the two.
def compareTracks(trackA, trackB):
	if trackA.fileHash == trackB.fileHash:	# If they have equal hashes, they are the same
		return 100
	# A list of tags that match (confined to the set {Name, Artist, Album, Total Time}
	matchingTags = []
	if compareTimes(trackA.tags['Total Time'], trackB.tags['Total Time']):
		matchingTags.append( 'Total Time' )
	for key in ['Name', 'Artist', 'Album']:
		if key in trackA.tags and key in trackB.tags and compareStrings(trackA.tags[key], trackB.tags[key]):
			matchingTags.append( key )

	if len(matchingTags) == 4:	# All tags match, they are confidently duplicates
		return 95
	elif len(matchingTags) == 3:	# 3/4 tags match. Confidently duplicates, unless the titles are what differ
		if 'Name' not in matchingTags:
			return 40
		else:
			return 90
	elif len(matchingTags) == 2:	# If only 2 tags match
		if 'Name' in matchingTags and ('Artist' in matchingTags or 'Album' in matchingTags):
			return 75 # the only combinations with merit are title+artist and title+album
		else:
			return 25
	elif len(matchingTags) == 1:	# 1 tags matches, almost certainly not duplicates
		return 3
	else:
		return 0

tracks = []		# Maintains a list of tracks as they are parsed
cutoff = 90		# If comparison scores fall below this threashold, don't report them as duplicates
inTracks = False	# While parsing, this is set to true when within the "tracks" portion of the XML document
dictStack = 0 		# When <dict> is seen, increment. When </dict> is seen, decrement.
trackInfo = [] 		# Throughout parsing, this stores the XML information for the current track
for line in XMLdata:
	if not inTracks and re.search('<key>.*Tracks.*</key>',line):
		inTracks = True		# We've entered the relevent portion of the XML document
	if not inTracks:	# ...and if we haven't yet, skip this line
		continue
	if re.search('^\s*<dict>\s*$',line):
		dictStack += 1
	elif re.search('^\s*</dict>\s*$',line):
		dictStack -= 1
		if dictStack > 0:	# This is true when a track is finished being parsed
			newTrack = Track(trackInfo)	# Create a new Track object
			if not newTrack.valid:		# If there was a problem with the Track
				trackInfo = []
				continue
#			if 'Name' in newTrack.tags:
#				print newTrack.tags['Name']
			for someTrack in tracks:	# Compare the new Track to all previous ones
				score = compareTracks(newTrack, someTrack)
				if score >= cutoff:	# If the confidence estimate is above the cutoff, print
					print "Possible duplicates, with",(str(score) + "%"),"confidence:"
					print newTrack.filePath
					print someTrack.filePath
					print
			tracks.append(newTrack)		# Add the new Track to the tracks list
			trackInfo = []			# Clear track info
		else:
			break
	if dictStack == 2:	# If the parsed line is within some track, add it to trackInfo
		trackInfo.append(line)


