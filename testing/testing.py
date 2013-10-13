import pickle
import unittest
import re
import sys
sys.path.append('..')

import Track

class TestTrack(unittest.TestCase):
	
	def setUp(self):
		self.validTrack = Track.Track( pickle.load(open('data/sampleTrack1.pkl','r')) )

	def test_convertTime(self):
		test_times = [('209580', 210), ('198504', 199), ('233560', 234), ('191843', 192), ('238785', 239), ('275800', 276), ('237270', 237), ('210102', 210), ('132075', 132), ('224182', 224)]
		for t in test_times:
			self.assertEqual(t[1], self.validTrack.convertTime(t[0]))

	# Complete information
	def test_track1(self):
		track = Track.Track( pickle.load(open('data/sampleTrack1.pkl','r')) )
		self.assertTrue( track.valid ) 
		for (key,val) in [('Artist','Modest Mouse'), ('Name','Float On'), ('Album','Float On-(CDS)'), ('Total Time', 210), ('Rating',5), ('Play Count', 88), ('Date Added', '2006-12-19')]:
			self.assertTrue( key in track.tags )
			self.assertEqual( track.tags[key], val )
		self.assertTrue( 'Location' in track.tags )
	# Missing Album (missing line) and Name (due to incomplete XML tags)
	# Missing play count and rating in tags, which should report as 0
	def test_track2(self):
		track = Track.Track( pickle.load(open('data/sampleTrack2.pkl','r')) )
		self.assertTrue( track.valid )
		self.assertTrue( 'Artist' in track.tags )
		self.assertFalse( 'Album' in track.tags )
		self.assertFalse( 'Name' in track.tags )
		self.assertTrue( 'Play Count' in track.tags )

	# Invalid because no Total Time
	def test_track3(self):
		track = Track.Track( pickle.load(open('data/sampleTrack3.pkl','r')) )
		self.assertFalse( track.valid )
	# Invalid because Total Time of 0
	def test_track4(self):
		track = Track.Track( pickle.load(open('data/sampleTrack4.pkl','r')) )
		self.assertTrue( 'Total Time' in track.tags )
		self.assertFalse( track.valid )
	# Invalid because no Location
	def test_track5(self):
		track = Track.Track( pickle.load(open('data/sampleTrack5.pkl','r')) )
		self.assertFalse( 'Location' in track.tags )
		self.assertFalse( track.valid )
	# Invalid because blank location
	def test_track6(self):
		track = Track.Track( pickle.load(open('data/sampleTrack6.pkl','r')) )
		self.assertFalse( 'Location' in track.tags )
		self.assertFalse( track.valid )
	# Invalid because the Location isn't a valid URL
	def test_track7(self):
		track = Track.Track( pickle.load(open('data/sampleTrack7.pkl','r')) )
		self.assertTrue( 'Location' in track.tags )
		self.assertFalse( track.valid )
	# Invalid because media file path doesn't exist
	def test_track8(self):
		track = Track.Track( pickle.load(open('data/sampleTrack8.pkl','r')) )
		self.assertFalse( track.valid )
	# Invalid because media file path is empty
	def test_track9(self):
		track = Track.Track( pickle.load(open('data/sampleTrack9.pkl','r')) )
		self.assertFalse( track.valid )
	# A tagless file will produce the same hash as if tags are present
	def test_taglessHash(self):
		sampleMP3TaglessHash = self.validTrack.computeHash('data/sampleMP3Tagless.mp3')
		self.assertEqual( self.validTrack.fileHash, sampleMP3TaglessHash )
	# The same file with different tags produce equal hashes
	def test_equalHash(self):
		sampleMP3DifferentHash = self.validTrack.computeHash('data/sampleMP3Different.mp3')
		self.assertEqual( self.validTrack.fileHash, sampleMP3DifferentHash )
	# Two different media files produce different hashes
	def test_unequalHash(self):
		differentFileHash = self.validTrack.computeHash('data/otherSampleMP3.mp3')
		self.assertTrue( self.validTrack.fileHash != differentFileHash )
	# An empty file produces a different hash than the sample one
#	def test_emptyFileHash(self):
#		emptyHash = self.validTrack.computeHash('data/emptyfile')
#		self.assertTrue( self.validTrack.fileHash != emptyFileHash )


suite = unittest.TestLoader().loadTestsFromTestCase(TestTrack)
unittest.TextTestRunner(verbosity=3).run(suite)


