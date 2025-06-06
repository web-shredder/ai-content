import unittest
import os
import sys
import types
import re

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT)

path = os.path.join(ROOT, "streamlit_app.py")
with open(path, "r") as f:
    source = f.read()

pattern = re.compile(r"def parse_queries.*?return unique", re.S)
match = pattern.search(source)
assert match, "parse_queries function not found"
namespace = {}
exec(match.group(0), {"re": re}, namespace)
parse_queries = namespace["parse_queries"]

class ParseQueriesTest(unittest.TestCase):
    def test_blank_line_after_heading(self):
        text = """Search Queries:\n\n- Reformulation: what is fasttrace?\n- Implicit: tracing library benefits"""
        expected = [
            {"type": "reformulation", "query": "what is fasttrace?", "note": ""},
            {"type": "implicit", "query": "tracing library benefits", "note": ""},
        ]
        self.assertEqual(parse_queries(text), expected)

    def test_query_with_note(self):
        text = """Search Queries:\n- Comparative: fasttrace vs jaeger - note\n- Reformulation: what is fasttrace - explanation"""
        expected = [
            {"type": "comparative", "query": "fasttrace vs jaeger", "note": "note"},
            {"type": "reformulation", "query": "what is fasttrace", "note": "explanation"},
        ]
        self.assertEqual(parse_queries(text), expected)

    def test_non_bullet_lines(self):
        text = """Search Queries:\n1. Why use FastTrace?\n2. FastTrace vs Zipkin\nNotes:"""
        expected = [
            {"type": "", "query": "Why use FastTrace?", "note": ""},
            {"type": "", "query": "FastTrace vs Zipkin", "note": ""},
        ]
        self.assertEqual(parse_queries(text), expected)

    def test_numbered_parentheses_and_blank_lines(self):
        text = """Search Queries:\n1) Comparative: fasttrace vs jaeger\n\n2) Reformulation: what is fasttrace - expl"""
        expected = [
            {"type": "comparative", "query": "fasttrace vs jaeger", "note": ""},
            {"type": "reformulation", "query": "what is fasttrace", "note": "expl"},
        ]
        self.assertEqual(parse_queries(text), expected)

if __name__ == '__main__':
    unittest.main()
