import unittest
from src.tag_expressions import TagExpressions

class TestTagExpressions(unittest.TestCase):

    def setUp(self) -> None:
        self.tag_expressions = TagExpressions()

    def test_match_one_tag(self):
        self.tag_expressions.add_filter_tags([["tag1"]])
        self.assertTrue(self.tag_expressions.match(["tag1", "tag2"]))
        self.assertFalse(self.tag_expressions.match(["tag2", "tag3"]))

    def test_match_one_tag_with_symbol(self):
        self.tag_expressions.add_filter_tags([["@tag1"]])
        self.assertTrue(self.tag_expressions.match(["tag1", "tag2"]))
        self.assertFalse(self.tag_expressions.match(["tag2", "tag3"]))

    def test_match_one_negative_tag(self):
        self.tag_expressions.add_filter_tags([["~@tag1"]])
        self.assertTrue(self.tag_expressions.match(["tag2"]))
        self.assertFalse(self.tag_expressions.match(["tag1"]))
        self.assertFalse(self.tag_expressions.match(["tag1", "tag2"]))

    def test_match_all_tags(self):
        self.tag_expressions.add_filter_tags([["tag1,tag2"]])
        self.assertTrue(self.tag_expressions.match(["tag1", "tag2"]))

    def test_match_all_tags_with_symbol(self):
        self.tag_expressions.add_filter_tags([["@tag1,@tag2"]])
        self.assertTrue(self.tag_expressions.match(["tag1", "tag2"]))

    def test_match_all_tags_containing_negative(self):
        self.tag_expressions.add_filter_tags([["tag1,~@tag2"]])
        self.assertTrue(self.tag_expressions.match(["tag1"]))
        self.assertTrue(self.tag_expressions.match(["tag3"]))
        self.assertFalse(self.tag_expressions.match(["tag2"]))

    def test_match_multple_condition(self):
        self.tag_expressions.add_filter_tags([["tag1,~@tag2"], ["tag3"]])
        self.assertTrue(self.tag_expressions.match(["tag1", "tag3"]))
        self.assertTrue(self.tag_expressions.match(["tag3"]))
        self.assertFalse(self.tag_expressions.match(["tag2"]))
        self.assertFalse(self.tag_expressions.match(["tag2", "tag3"]))
