import unittest
from src.tag_expressions_v2 import TagExpressionsV2

class TestTagExpressionsV2(unittest.TestCase):

    def setUp(self) -> None:
        self.tag_expression = TagExpressionsV2()

    def test_match_one_tag(self):
        self.tag_expression.parse("tag1")
        self.assertTrue(self.tag_expression.match(["tag1", "tag2"]))
        self.assertFalse(self.tag_expression.match(["tag2", "tag3"]))

    def test_match_one_tag_with_symbol(self):
        self.tag_expression.parse("@tag1")
        self.assertTrue(self.tag_expression.match(["tag1", "tag2"]))
        self.assertFalse(self.tag_expression.match(["tag2", "tag3"]))

    def test_match_one_negative_tag(self):
        self.tag_expression.parse("not @tag1")
        self.assertTrue(self.tag_expression.match(["tag2"]))
        self.assertFalse(self.tag_expression.match(["tag1"]))
        self.assertFalse(self.tag_expression.match(["tag1", "tag2"]))

    def test_match_all_tags(self):
        self.tag_expression.parse("tag1 or tag2")
        self.assertTrue(self.tag_expression.match(["tag1", "tag2"]))

    def test_match_all_tags_with_symbol(self):
        self.tag_expression.parse("@tag1 or @tag2")
        self.assertTrue(self.tag_expression.match(["tag1", "tag2"]))

    def test_match_all_tags_containing_negative(self):
        self.tag_expression.parse("tag1 or not @tag2")
        self.assertTrue(self.tag_expression.match(["tag1"]))
        self.assertTrue(self.tag_expression.match(["tag3"]))
        self.assertFalse(self.tag_expression.match(["tag2"]))

    def test_match_multple_condition(self):
        self.tag_expression.parse("(tag1 or not @tag2) and tag3")
        self.assertTrue(self.tag_expression.match(["tag1", "tag3"]))
        self.assertTrue(self.tag_expression.match(["tag3"]))
        self.assertFalse(self.tag_expression.match(["tag2"]))
        self.assertFalse(self.tag_expression.match(["tag2", "tag3"]))

    def test_throw_exception_if_lpar_missing(self):
        with self.assertRaises(SyntaxError) as e:
            self.tag_expression.parse("tag1 or not @tag2) and tag3")

        self.assertEqual("Unexpected token RPAR within the given input 'tag1 or not @tag2) and tag3'.", e.exception.msg)

    def test_throw_exception_if_rpar_missing(self):
        with self.assertRaises(SyntaxError) as e:
            self.tag_expression.parse("(tag1 or not @tag2 and tag3")

        self.assertEqual("Missing closing parenthesis within the given input '(tag1 or not @tag2 and tag3'.", e.exception.msg)

    def test_exception_if_input_is_none(self):
        with self.assertRaises(ValueError) as e:
            self.tag_expression.parse(None)

        self.assertEqual("Invalid input: None.", e.exception.args[0])
