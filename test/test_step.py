import unittest
import sys
sys.path.append("../")
from src.step import Step
from src.data_table import DataTable

class TestStep(unittest.TestCase):

    def test_lead_step_method_name(self):
        step = Step("Given", "this is the name for method", kwargs={})
        self.assertEqual("given_this_is_the_name_for_method", step.get_method_name())
    
    def test_concurrent_step_method_name(self):
        step = Step("And", "this is the name for method", kwargs={}, lead_step="When")
        self.assertEqual("when_this_is_the_name_for_method", step.get_method_name())

    def test_doc_string_should_be_transfer_to_data_table(self):
        doc_string = """
            |  item  |
            | apple  |
            | orange |
            | banana |
        """
        data_table_list = [['item'], ['apple'], ['orange'], ['banana']]
        step = Step("Given", "this is the name for method", kwargs={}, doc_string=doc_string, lead_step="When")
        self.assertEqual(data_table_list, step.data_table.to_list())

    def test_doc_string_should_not_be_transfer_to_data_table(self):
        doc_string = """
            |  item  |
            | apple  |
            | orange |
            | banana |
        """
        data_table_string = doc_string
        data_table = DataTable(doc_string)
        step = Step("Given", "this is the name for method", kwargs={}, doc_string=doc_string, data_table=data_table_string, lead_step="When")
        self.assertEqual(doc_string, step.doc_string)
        self.assertEqual(data_table.to_list(), step.data_table.to_list())


if __name__ == '__main__':
    unittest.main()