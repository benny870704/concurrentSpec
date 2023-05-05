import sys, io
import shutil
import os.path
import unittest
import warnings
import traceback
from pathlib import Path
sys.path.append("../")
from src.feature import FeatureManager
from src.scenario_outline import ScenarioOutline

class TestScenarioOutline(unittest.TestCase):

    def setUp(self):
        self.test_path = str(Path(traceback.extract_stack()[-1].filename).parent)
        FeatureManager.console_output = False
    
    def tearDown(self):
        FeatureManager.clear()
        dir = f"{self.test_path}/steps/"
        if os.path.exists(dir):
            shutil.rmtree(dir)

    def test_scenario_steps_class_name_and_file_name(self):
        scenario = ScenarioOutline("Scheduled sprinkling")
        self.assertEqual("ScheduledSprinkling", scenario.get_step_definition_class_name())
        self.assertEqual("scheduled_sprinkling", scenario.get_step_definition_file_name())

    def test_empty_scenario_outline_should_contain_set_up_and_tear_down(self):
        scenario = ScenarioOutline("Test set up and tear down")
        scenario_context = scenario.initialize_scenario_context()
        
        self.assertIsNotNone(getattr(scenario_context, 'set_up', None))
        self.assertIsNotNone(getattr(scenario_context, 'tear_down', None))

    def test_generate_file_with_name(self):
        ScenarioOutline("Scheduled sprinkling")
        
        self.assertTrue(os.path.exists(f"{self.test_path}/steps/scheduled_sprinkling.py"))
        
    def test_auto_generate_methods_And(self):
        scenario = ScenarioOutline("Scheduled sprinkling")
        
        scenario.Given("water supply is normal")\
                .And("all timers are set to 4:00:00 am")
        
        self.assertEqual("given_all_timers_are_set_to_4_00_00_am", scenario.get_groups()[0].get_all_steps()[1].get_method_name())

    def test_full_text(self):
        scenario = ScenarioOutline("Simple Google search")

        scenario.Given("a web browser is on the Google page")\
                \
                .When("the search phrase \"panda\" is entered")\
                \
                .Then("results for \"panda\" are shown")\
                .And("the related results include \"Panda Express\"")\
                .But("the related results do not include \"pandemonium\"")

        self.assertEqual(
            ("\n\033[1;34mScenario Outline: Simple Google search\033[0m\n"
            "  \033[0mGiven a web browser is on the Google page\033[0m\n"
            "  \033[0mWhen the search phrase \"panda\" is entered\033[0m\n"
            "  \033[0mThen results for \"panda\" are shown\033[0m\n"
            "  \033[0mAnd the related results include \"Panda Express\"\033[0m\n"
            "  \033[0mBut the related results do not include \"pandemonium\"\033[0m\n"),
            scenario.result_printout()
        )

    def test_full_text_with_examples(self):
        scenario = ScenarioOutline("Simple Google search")

        scenario.Given("a web browser is on the <webpage> page")\
                \
                .When("the search phrase <keyword> is entered")\
                \
                .Then("results for <keyword> are shown")\
                .And("the related results include <related>")\
                .But("the related results do not include <no_related>")\
                .WithExamples("""
                    | webpage |    keyword     |    related    |   no_related  |
                    | Google  |     panda      | Panda Express | pandemonium   |
                    | Bing    |  black panther | Black Panther | blackpink     |
                """)

        self.assertEqual(
            ("\n\033[1;34mScenario Outline: Simple Google search - Example #1\033[0m\n"
            "  \033[0mGiven a web browser is on the \033[1mGoogle\033[22m page\033[0m\n"
            "  \033[0mWhen the search phrase \033[1mpanda\033[22m is entered\033[0m\n"
            "  \033[0mThen results for \033[1mpanda\033[22m are shown\033[0m\n"
            "  \033[0mAnd the related results include \033[1mPanda Express\033[22m\033[0m\n"
            "  \033[0mBut the related results do not include \033[1mpandemonium\033[22m\033[0m\n"),
            scenario.result_printout(0)
        )
        self.assertEqual(
            ("\n\033[1;34mScenario Outline: Simple Google search - Example #2\033[0m\n"
            "  \033[0mGiven a web browser is on the \033[1mBing\033[22m page\033[0m\n"
            "  \033[0mWhen the search phrase \033[1mblack panther\033[22m is entered\033[0m\n"
            "  \033[0mThen results for \033[1mblack panther\033[22m are shown\033[0m\n"
            "  \033[0mAnd the related results include \033[1mBlack Panther\033[22m\033[0m\n"
            "  \033[0mBut the related results do not include \033[1mblackpink\033[22m\033[0m\n"),
            scenario.result_printout(1)
        )

    def test_full_text_with_examples_contains_newlines(self):
        scenario = ScenarioOutline("Simple Google search")

        scenario.Given("a web browser is on the <webpage> page")\
                \
                .When("the search phrase <keyword> is entered")\
                \
                .Then("results for <keyword> are shown")\
                .And("the related results include <related>")\
                .But("the related results do not include <no_related>")\
                .WithExamples("""
                    | webpage |     keyword      |     related     |   no_related  |
                    | Google  |     panda        | Panda Express\n | pandemonium   |
                    | Bing    |  \nblack panther | Black Panther   | blackpink     |
                """)

        self.assertEqual(
            ("\n\033[1;34mScenario Outline: Simple Google search - Example #1\033[0m\n"
            "  \033[0mGiven a web browser is on the \033[1mGoogle\033[22m page\033[0m\n"
            "  \033[0mWhen the search phrase \033[1mpanda\033[22m is entered\033[0m\n"
            "  \033[0mThen results for \033[1mpanda\033[22m are shown\033[0m\n"
            "  \033[0mAnd the related results include \033[1mPanda Express\\n\033[22m\033[0m\n"
            "  \033[0mBut the related results do not include \033[1mpandemonium\033[22m\033[0m\n"),
            scenario.result_printout(0)
        )
        self.assertEqual(
            ("\n\033[1;34mScenario Outline: Simple Google search - Example #2\033[0m\n"
            "  \033[0mGiven a web browser is on the \033[1mBing\033[22m page\033[0m\n"
            "  \033[0mWhen the search phrase \033[1m\\nblack panther\033[22m is entered\033[0m\n"
            "  \033[0mThen results for \033[1m\\nblack panther\033[22m are shown\033[0m\n"
            "  \033[0mAnd the related results include \033[1mBlack Panther\033[22m\033[0m\n"
            "  \033[0mBut the related results do not include \033[1mblackpink\033[22m\033[0m\n"),
            scenario.result_printout(1)
        )

    def test_raise_exception_if_examples_count_is_invalid(self):
        os.makedirs(f"{self.test_path}/steps", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/simple_google_search.py", f"{self.test_path}/steps/simple_google_search.py")

        scenario = ScenarioOutline("Simple Google search")

        with self.assertRaises(Exception) as e:
            scenario.Given("a web browser is on the <webpage> page")\
                    \
                    .When("the search phrase <keyword> is entered")\
                    \
                    .Then("results for <keyword> are shown")\
                    .And("the related results include <related>")\
                    .But("the related results do not include <no_related>")\
                    .WithExamples("""
                        | webpage |    keyword     |    related    |   no_related  |
                        |         |     panda      | Panda Express |               |
                        |         |  black panther |               | blackpink     |
                    """).execute()

    def test_execute_with_examples(self):
        os.makedirs(f"{self.test_path}/steps", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/simple_google_search.py", f"{self.test_path}/steps/simple_google_search.py")

        sys.stdout = io.StringIO()

        scenario = ScenarioOutline("Simple Google search")
        
        scenario.Given("a web browser is on the <webpage> page")\
                .When("the search phrase <keyword> is entered")\
                .Then("results for <keyword> are shown")\
                .And("the related results include <related>")\
                .But("the related results do not include <no related>")\
                .WithExamples("""
                    | webpage |    keyword     |    related    |   no related  |
                    | Google  |     panda      | Panda Express | pandemonium   |
                    | Bing    |  black panther | Black Panther | blackpink     |
                """).execute()

        sys.stdout = sys.__stdout__

    def test_Given_should_not_appear_after_a_When(self):
        with self.assertRaises(ValueError) as e:
            ScenarioOutline("Scheduled sprinkling")\
            .When("the time is 4:00:00 am")\
            .Given("water supply is normal")

        self.assertEqual("Given: out of place", str(e.exception))

    def test_Given_should_not_appear_after_a_Then(self):
        with self.assertRaises(ValueError) as e:
            ScenarioOutline("Scheduled sprinkling")\
            .Then("sprinkler A should emit water no later than 4:00:05 am")\
            .Given("timer of sprinkler A is set to 4:00:00 am")

        self.assertEqual("Given: out of place", str(e.exception))

    def test_And_should_not_appear_without_any_lead_step(self):
        with self.assertRaises(ValueError) as e:
            ScenarioOutline("Scheduled sprinkling")\
            .And("all timers are set to 4:00:00 am")
                    
        self.assertEqual("And: must not be the first clause", str(e.exception))

    def test_But_should_not_appear_without_any_lead_step(self):
        with self.assertRaises(ValueError) as e:
            ScenarioOutline("Scheduled sprinkling")\
            .But("timer of sprinklers B and C are not set")
                    
        self.assertEqual("But: must not be the first clause", str(e.exception))

    def test_step_default_definition_should_throw_runtime_error(self):
        with self.assertRaises(RuntimeError) as e:
            ScenarioOutline("Scheduled sprinkling")\
            .Given("water supply is normal")\
            .execute()

        self.assertTrue("Traceback (most recent call last):\n" in str(e.exception)) 
        self.assertTrue(
            ("\n\033[1;31mError(s) in the group:\n\n\033"
            "[0;31m    NotImplementedError from step: water supply is normal,\n"
            "    error message: given_water_supply_is_normal\n\n\033[0m") in str(e.exception)
        )

    def test_default_scenario_step_definition_class_name_and_file_name(self):
        scenario = ScenarioOutline()

        self.assertEqual("StepDefinitions", scenario.get_step_definition_class_name())
        self.assertEqual("step_definitions", scenario.get_step_definition_file_name())

    def test_generate_file_without_scenario_name(self):
        ScenarioOutline()
        
        self.assertTrue(os.path.exists(f"{self.test_path}/steps/step_definitions.py"))

    def test_generate_file_duplicated_empty_scenario_name(self):
        ScenarioOutline()
        ScenarioOutline()
        
        self.assertTrue(os.path.exists(f"{self.test_path}/steps/step_definitions.py"))
        self.assertEqual(1, len(os.listdir(f"{self.test_path}/steps/")))

    def test_generate_file_duplicated_scenario_name(self):
        ScenarioOutline("Scheduled sprinkling")
        ScenarioOutline("Scheduled sprinkling")
        
        self.assertTrue(os.path.exists(f"{self.test_path}/steps/scheduled_sprinkling.py"))
        self.assertEqual(1, len(os.listdir(f"{self.test_path}/steps/")))
        
    def test_duplicate_scenarios_should_generate_step_definition_only_once(self):
        ScenarioOutline("Simple Google search")\
        .Given("a web browser is on the Google page")\
        \
        .When("the search phrase \"panda\" is entered")\
        \
        .Then("results for \"panda\" are shown")\
        .And("the related results include \"Panda Express\"")\
        .But("the related results do not include \"pandemonium\"")
                  
        ScenarioOutline("Simple Google search")\
        .Given("a web browser is on the Google page")\
        \
        .When("the search phrase \"panda\" is entered")\
        \
        .Then("results for \"panda\" are shown")\
        .And("the related results include \"Panda Express\"")\
        .But("the related results do not include \"pandemonium\"")
        
        whole_class_text = Path(f"{self.test_path}/steps/simple_google_search.py").read_text()
        
        self.assertEqual(1, whole_class_text.count("given_a_web_browser_is_on_the_google_page(self)"))
        self.assertEqual(1, whole_class_text.count("when_the_search_phrase_panda_is_entered(self)"))
        self.assertEqual(1, whole_class_text.count("then_results_for_panda_are_shown(self)"))
        self.assertEqual(1, whole_class_text.count("then_the_related_results_include_panda_express_(self)"))
        self.assertEqual(1, whole_class_text.count("then_the_related_results_do_not_include_pandemonium_(self)"))

    def test_duplicate_steps_in_the_same_scenario_should_generate_step_definition_only_once(self):
        ScenarioOutline("Simple Google search")\
        .Given("a web browser is on the Google page")\
        .Given("a web browser is on the Google page")\
        \
        .When("the search phrase \"panda\" is entered")\
        .When("the search phrase \"panda\" is entered")\
        \
        .Then("results for \"panda\" are shown")\
        .Then("results for \"panda\" are shown")\
        .And("the related results include \"Panda Express\"")\
        .And("the related results include \"Panda Express\"")\
        .But("the related results do not include \"pandemonium\"")\
        .But("the related results do not include \"pandemonium\"")
        
        whole_class_text = Path(f"{self.test_path}/steps/simple_google_search.py").read_text()
        
        self.assertEqual(1, whole_class_text.count("given_a_web_browser_is_on_the_google_page(self)"))
        self.assertEqual(1, whole_class_text.count("when_the_search_phrase_panda_is_entered(self)"))
        self.assertEqual(1, whole_class_text.count("then_results_for_panda_are_shown(self)"))
        self.assertEqual(1, whole_class_text.count("then_the_related_results_include_panda_express_(self)"))
        self.assertEqual(1, whole_class_text.count("then_the_related_results_do_not_include_pandemonium_(self)"))

    def test_continuing_execution_on_a_step(self):
        os.makedirs(f"{self.test_path}/steps", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/continuing_execution_at_a_specific_step.py", f"{self.test_path}/steps/continuing_execution_at_a_specific_step.py")

        sys.stdout = io.StringIO()

        with self.assertRaises(RuntimeError) as e:
            ScenarioOutline("Continuing execution at a specific step")\
            .Given("Some precondition")\
            .When("An event happens")\
            .Then("The step is true")\
            .And("The step fails but it adds a tag to continue execution", continue_after_failure=True)\
            .Then("The step should be executed and it fails")\
            .execute()

        sys.stdout = sys.__stdout__

        self.assertTrue("\n\033[1;31mError(s) in the group:\n\n\033[0;31m")
        self.assertTrue("    AssertionError from step: The step fails but it adds a tag to continue execution\n\n" in str(e.exception))
        self.assertTrue("    AssertionError from step: The step should be executed and it fails\n\n" in str(e.exception))

    def test_set_continue_after_failure_on_Given_and_When_group_should_give_warnings(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            ScenarioOutline("Continuing execution at a specific step")\
            .Given("First precondition", continue_after_failure=True)\
            .And("Second precondition", continue_after_failure=True)\
            .But("Third precondition", continue_after_failure=True)\
            .When("First event happens", continue_after_failure=True)\
            .But("Second event doesn't happen", continue_after_failure=True)\
            .And("Third event does not happen", continue_after_failure=True)\
            .Then("The step is true")\
            .And("The step fails but it adds a tag to continue execution")\
            .Then("The step should be executed and it fails")

        self.assertEqual("\033[33m\nGiven should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", str(caught_warnings[0].message))
        self.assertEqual("\033[33m\nAnd in Given group should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", str(caught_warnings[1].message))
        self.assertEqual("\033[33m\nBut in Given group should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", str(caught_warnings[2].message))
        self.assertEqual("\033[33m\nWhen should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", str(caught_warnings[3].message))
        self.assertEqual("\033[33m\nBut in When group should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", str(caught_warnings[4].message))
        self.assertEqual("\033[33m\nAnd in When group should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", str(caught_warnings[5].message))
    
    def test_do_set_up_before_executing_scenario(self):
        os.makedirs(f"{self.test_path}/steps", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/set_up_should_be_executed.py", f"{self.test_path}/steps/set_up_should_be_executed.py")
        
        scenario = ScenarioOutline("Set Up Should Be Executed")

        scenario.Given("a web browser is on the Google page")\
                \
                .When("the search phrase \"panda\" is entered")\
                \
                .Then("results for \"panda\" are shown")\
                .execute()

        self.assertTrue("Set Up Executed" in scenario.captured_output_message())
    
    def test_do_tear_down_after_finish_execute_scenario(self):
        os.makedirs(f"{self.test_path}/steps", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/tear_down_should_be_executed.py", f"{self.test_path}/steps/tear_down_should_be_executed.py")
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        scenario = ScenarioOutline("Tear Down Should Be Executed")

        scenario.Given("a web browser is on the Google page")\
                \
                .When("the search phrase \"panda\" is entered")\
                \
                .Then("results for \"panda\" are shown")\
                .execute()

        sys.stdout = sys.__stdout__

        self.assertTrue("Tear Down Executed" in scenario.captured_output_message()) 
        
    def test_do_tear_down_after_fail_execute_scenario(self):
        os.makedirs(f"{self.test_path}/steps", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/tear_down_should_be_executed.py", f"{self.test_path}/steps/tear_down_should_be_executed.py")
        
        # captured_output = io.StringIO()
        # sys.stdout = captured_output
        with self.assertRaises(RuntimeError) as e:
            scenario = ScenarioOutline("Tear Down Should Be Executed")

            scenario.Given("a web browser is on the Google page")\
                    \
                    .When("the search phrase \"panda\" is entered")\
                    \
                    .Then("results for \"capybara\" are shown")\
                    .execute()

        # sys.stdout = sys.__stdout__

        self.assertTrue("Capybara Not Exist" in str(e.exception))
        self.assertTrue("Tear Down Executed" in scenario.captured_output_message())

if __name__ == '__main__':
    unittest.main()
