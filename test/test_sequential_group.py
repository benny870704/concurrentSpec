import unittest
import sys
sys.path.append("../")
from src.sequential_group import SequentialGroup
from src.step import Step

class TestSequentialGroup(unittest.TestCase):
    def test_add_step(self):
        sequential_group = SequentialGroup()
        sequential_group.add_step(Step("Given", "a precondition", kwargs={}))
        sequential_group.add_step(Step("And", "another precondition", kwargs={}, lead_step="Given"))

        self.assertEqual(2, len(sequential_group.get_all_steps()))

if __name__ == '__main__':
    unittest.main()
