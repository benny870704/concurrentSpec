import sys
import unittest
sys.path.append("../")
from src.data_table import DataTable

class TestDataTable(unittest.TestCase):

    def test_input_invalid_table(self):
        invalid_data_table_string = """
            |  item  | price |
            | apple  |
            | orange |
            | banana |
        """
        with self.assertRaises(Exception) as e:
            DataTable(invalid_data_table_string)
        self.assertEqual(e.exception.args[0], "Cannot parse table correctly.")
    
    def test_data_table_pretty_string(self):
        indent = "    "
        data_table_string = """
            |  item  |
            | apple  |
            | orange |
            | banana |
        """
        data_table = DataTable(data_table_string)
        self.assertEqual(data_table.get_pretty_string(), f"{indent}|  item  |\n{indent}| apple  |\n{indent}| orange |\n{indent}| banana |\n")

    def test_data_table_string(self):
        data_table_string = """
            |  item  |
            | apple  |
            | orange |
            | banana |
        """
        data_table = DataTable(data_table_string)
        self.assertEqual(data_table.get_string(), f"|  item  |\n| apple  |\n| orange |\n| banana |\n")

    def test_data_table_string_with_two_columns(self):
        data_table_string = """
            |  item  | price |
            | apple  | 123456789 |
            | orange | 21245 |
            | banana | 1234 |
        """
        data_table = DataTable(data_table_string)
        self.assertEqual(data_table.get_string(), f"|  item  |   price   |\n| apple  | 123456789 |\n| orange |   21245   |\n| banana |    1234   |\n")

    def test_data_contains_newline(self):
        data_table_string = """
            |  item  |
            | apple\n  |
            | orange\n |
            | banana |
        """
        data_table = DataTable(data_table_string)
        self.assertEqual(data_table.get_string(), f"|  item  |\n| apple  |\n| orange |\n| banana |\n")
