import unittest
import os
import sys
import re

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT)

path = os.path.join(ROOT, "streamlit_app.py")
with open(path, "r") as f:
    source = f.read()

pattern = re.compile(r"def classify_query.*?return \"implicit\"", re.S)
match = pattern.search(source)
assert match, "classify_query function not found"
namespace = {}
exec(match.group(0), {"re": re}, namespace)
classify_query = namespace["classify_query"]


class ClassifyQueryTest(unittest.TestCase):
    def test_temporal_90_day(self):
        self.assertEqual(classify_query("90-day SEO roadmap"), "temporal")

    def test_location_city(self):
        self.assertEqual(classify_query("meetups in Denver"), "location")


if __name__ == "__main__":
    unittest.main()
