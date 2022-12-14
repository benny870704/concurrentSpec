import unittest
import sys
sys.path.append("../")
import io
import os.path
import glob
from src.scenario import Scenario

class TestScenario(unittest.TestCase):
    
    @classmethod
    def tearDownClass(self):
        dir = "./steps/"

        files = glob.glob(os.path.join(dir, "*.py"))
        for f in files:
            if f != "./steps/continuing_execution_at_a_specific_step.py":
                os.remove(f)

    def test_generate_class_name(self):
        scenario = Scenario("This is a Scenario")
        self.assertEqual("ThisIsAScenario", scenario.get_step_class_name())

    def test_generate_file_name(self):
        scenario = Scenario("This is a Scenario")
        self.assertEqual("this_is_a_scenario", scenario.get_step_file_name())
    
    def test_default_scenario_steps_class_name_and_file_name(self):
        scenario = Scenario()
        self.assertEqual("Scenario", scenario.get_step_class_name())
        self.assertEqual("scenario", scenario.get_step_file_name())

    def test_auto_generate_functions_and(self):
        scenario = Scenario()
        
        scenario.Given("process a is running at 8:00 am")
        scenario.And("process b is running")
        self.assertEqual("given_process_b_is_running", scenario.get_groups()[0].get_all_steps()[1].get_function_name())

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
        
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        with self.assertRaises(RuntimeError) as e:
            scenario.Given("a precondition")\
                    .execute()
        sys.stdout = sys.__stdout__

        self.assertTrue("Traceback (most recent call last):\n" in str(e.exception)) 
        self.assertTrue("\n\033[1;31mError(s) in the group:\n\n\033[0;31m    NotImplementedError from step: a precondition,\n    error message: given_a_precondition\n\n\033[0m" in str(e.exception))

    def test_full_text(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        scenario = Scenario("Print full text")

        scenario.Given("I'm Given.")\
                .And("I'm an And after Given.")\
                .When("I'm When.")\
                .Then("I'm Then.")\
                .But("I'm a But after Then.")\
                .full_text()

        sys.stdout = sys.__stdout__
        self.assertEqual("\n\033[1;34mScenario: Print full text\033[0m\n\033[0;34m  Given\033[0m I'm Given.\n\033[0;34m  And\033[0m I'm an And after Given.\n\033[0;34m  When\033[0m I'm When.\n\033[0;34m  Then\033[0m I'm Then.\n\033[0;34m  But\033[0m I'm a But after Then.\n", capturedOutput.getvalue())

    def test_continuing_execution_on_a_step(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        scenario = Scenario("Continuing execution at a specific step")

        with self.assertRaises(RuntimeError) as e:
            scenario.Given("Some precondition")\
                    .When("An event happens")\
                    .Then("The step is true")\
                    .And("The step fails but it adds a tag to continue execution", continue_after_failure=True)\
                    .Then("The step should be executed and it fails")\
                    .execute()

        sys.stdout = sys.__stdout__
        self.assertTrue("\n\033[1;31mError(s) in the group:\n\n\033[0;31m    AssertionError from step: The step fails but it adds a tag to continue execution\n\n\n\033[0m" in str(e.exception))
        self.assertTrue("\n\033[1;31mError(s) in the group:\n\n\033[0;31m    AssertionError from step: The step should be executed and it fails\n\n\n\033[0m" in str(e.exception))
        

if __name__ == '__main__':
    unittest.main()