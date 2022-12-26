import unittest
import sys
sys.path.append("../")
from src.scenario import Scenario

class TestLabelWarning(unittest.TestCase):

    def test_label_error(self):
        Scenario("label warning")\
        .Given("should warn by setting continue execution as true in Given", continue_after_failure=True)\
        .execute()

if __name__ == '__main__':
    unittest.main()