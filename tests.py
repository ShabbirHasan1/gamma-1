import unittest

from engines import PatternEngine

class TestPatterns(unittest.TestCase):   
    def test(self):
        expected = False
        testString = "color = white; color == black;"
        test = PatternEngine().test(testString)
        self.assertEqual(test, expected)

if __name__ == "__main__":
    unittest.main()