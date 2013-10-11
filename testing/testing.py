import pickle
import unittest
import re
import sys
sys.path.append('..')

import Track

class TestTrack(unittest.TestCase):
	XMLstring_regex_pass = ('<string>Testing</string>', 'Testing')
	XMLstring_regex_fail = '<string></string>'
	
	def setUp(self):
		sampleXML = pickle.load(open('sampleXMLdata.pkl','r'))
		self.track = Track.Track(sampleXML)

	# Probably necessary, but I want practice with the unittest module
	def test_stringRegex(self):
		good_result = re.search(self.track.stringRegex, self.XMLstring_regex_pass[0])
		self.assertTrue( good_result != None )	# Match found
		self.assertEqual( good_result.group(1), self.XMLstring_regex_pass[1] ) # 'Testing" matches

		bad_result = re.search(self.track.stringRegex, self.XMLstring_regex_fail)
		self.assertEqual( bad_result, None ) 
	
	


suite = unittest.TestLoader().loadTestsFromTestCase(TestTrack)
unittest.TextTestRunner(verbosity=2).run(suite)


