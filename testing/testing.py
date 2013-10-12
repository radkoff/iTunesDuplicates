import pickle
import unittest
import re
import sys
sys.path.append('..')

import Track

class TestTrack(unittest.TestCase):
	
	def setUp(self):
		self.track1 = Track.Track( pickle.load(open('data/sampleTrack1.pkl','r')) )
		self.track2 = Track.Track( pickle.load(open('data/sampleTrack2.pkl','r')) )

	def test_convertTime(self):
		test_times = [('209580', 210), ('198504', 199), ('233560', 234), ('191843', 192), ('238785', 239), ('275800', 276), ('237270', 237), ('210102', 210), ('132075', 132), ('224182', 224)]
		for t in test_times:
			self.assertEqual(t[1], self.track1.convertTime(t[0]))

	def test_track1(self):
		self.assertTrue( self.track1.valid ) 
		for (key,val) in [('Artist','Modest Mouse'), ('Name','Float On'), ('Album','Float On-(CDS)'), ('Total Time', 210)]:
			self.assertTrue( key in self.track1.tags )
			self.assertEqual( self.track1.tags[key], val )
		self.assertTrue( 'Location' in self.track1.tags )
	
	def test_hash(self):
		a = 1


suite = unittest.TestLoader().loadTestsFromTestCase(TestTrack)
unittest.TextTestRunner(verbosity=3).run(suite)


