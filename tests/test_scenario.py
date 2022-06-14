import unittest
import sys
sys.path.append("../")
from io import StringIO
from src.scenario import Scenario

class TestScenario(unittest.TestCase):
    def test_generate_class_name(self):
        scenario = Scenario("This is a Scenario")
        self.assertEqual("ThisIsAScenarioSteps", scenario.step_class_name)

    def test_generate_file_name(self):
        scenario = Scenario("This is a Scenario")
        self.assertEqual("this_is_a_scenario_steps", scenario.step_file_name)
    
    def test_default_scenario_steps_class_name_and_file_name(self):
        scenario = Scenario()
        self.assertEqual("ScenarioSteps", scenario.step_class_name)
        self.assertEqual("scenario_steps", scenario.step_file_name)

    def test_auto_generate_functions_and(self):
        scenario = Scenario()
        
        scenario.Given("process a is running at 8:00 am")
        scenario.And("process b is running")
        self.assertEqual("given_process_b_is_running", scenario.groups[0][1].function_name)

    def test_given_should_not_appear_after_a_when(self):
        scenario = Scenario()
        
        with self.assertRaises(ValueError) as e:
            scenario.When("something happens")\
                    .Given("a precondition")

        self.assertEqual("Given: out of place", str(e.exception))

    def test_given_should_not_appear_after_a_then(self):
        scenario = Scenario()
        
        with self.assertRaises(ValueError) as e:
            scenario.Then("some outcomes")\
                    .Given("a precondition")

        self.assertEqual("Given: out of place", str(e.exception))

    def test_and_should_not_appear_without_any_leading_step(self):
        scenario = Scenario()
        
        with self.assertRaises(ValueError) as e:
            scenario.And("a condition")
                    
        self.assertEqual("And: must not be the first clause", str(e.exception))

    def test_but_should_not_appear_without_any_leading_step(self):
        scenario = Scenario()
        
        with self.assertRaises(ValueError) as e:
            scenario.But("a condition")
                    
        self.assertEqual("But: must not be the first clause", str(e.exception))

    def test_step_default_definition_should_throw_runtime_error(self):
        scenario = Scenario()
        
        with self.assertRaises(RuntimeError) as e:
            scenario.Given("a precondition")\
                    .execute()
                    
        self.assertEqual("Error(s) in the group:\n\n    NotImplementedError from step: a precondition,\n    error message: given_a_precondition\n\n", str(e.exception))

if __name__ == '__main__':
    unittest.main()