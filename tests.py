import unittest

from engines import PatternEngine

class TestPatterns(unittest.TestCase):   
    def test(self):
        expected = 'white'
        testString = "color = white;"
        test = PatternEngine().test(testString)
        self.assertEqual(test, expected)

if __name__ == "__main__":
    unittest.main()