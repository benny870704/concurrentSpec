import unittest
from scenario import Scenario, _generate_camel_case, _generate_lower_case_with_underscores
class TestScenario(unittest.TestCase):
    def test_generate_class_name(self):
        self.assertEqual("ThisIsTheNameForClass", _generate_camel_case("This is the name for class"))

    def test_generate_function_name(self):
        self.assertEqual("this_is_the_name_for_function", _generate_lower_case_with_underscores("This is the name for function"))
    
    def test_scenario_steps_class_name(self):
        scenario = Scenario()
        self.assertEqual("ScenarioSteps", scenario.step_class_name)

    def test_auto_generate_functions_and(self):
        scenario = Scenario()
        
        scenario.Given("process a is running at 8:00 am")
        scenario.And("process b is running")
        self.assertEqual("given_process_b_is_running", scenario.groups[0][1][2])


if __name__ == '__main__':
    unittest.main()