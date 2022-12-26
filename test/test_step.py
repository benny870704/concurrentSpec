import unittest
import sys
sys.path.append("../")
from src.step import Step

class TestStep(unittest.TestCase):

    def test_leading_step_function_name(self):
        step = Step("Given", "this is the name for function", kwargs={})
        self.assertEqual("given_this_is_the_name_for_function", step.get_function_name())
    
    def test_concurrent_step_function_name(self):
        step = Step("And", "this is the name for function", kwargs={}, lead_step="When")
        self.assertEqual("when_this_is_the_name_for_function", step.get_function_name())


if __name__ == '__main__':
    unittest.main()
