import unittest
import sys, io
sys.path.append("../")
from src.feature import FeatureManager
from src.scenario import Scenario
from pathlib import Path
import os.path, importlib
import warnings
import traceback
import shutil

RESET = "\033[0m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
GRAY = "\033[90m"

def initialize_scenario_context(class_name, import_module_name, file_location):
    if import_module_name in sys.modules:
        del sys.modules[import_module_name]
    spec = importlib.util.spec_from_file_location(import_module_name, file_location)
    steps_module = importlib.util.module_from_spec(spec)
    sys.modules[import_module_name] = steps_module
    spec.loader.exec_module(steps_module)
    steps_class = getattr(steps_module, class_name)
    
    return steps_class()

class TestScenario(unittest.TestCase):

    def setUp(self):
        self.test_path = str(Path(traceback.extract_stack()[-1].filename).parent)
        self.step_definition_folder_name = "step_definitions"
        self.step_definition_folder_path = f"{self.test_path}/{self.step_definition_folder_name}/"
        FeatureManager.console_output = False

    def tearDown(self):
        if os.path.exists(self.step_definition_folder_path):
            shutil.rmtree(self.step_definition_folder_path)

    def test_scenario_steps_class_name_and_file_name(self):
        scenario = Scenario("Scheduled sprinkling")
        self.assertEqual("ScheduledSprinkling", scenario.get_step_definition_class_name())
        self.assertEqual("scheduled_sprinkling", scenario.get_step_definition_file_name())

    def test_empty_scenario_should_contain_set_up_and_tear_down(self):
        scenario = Scenario("Test set up and tear down")
        scenario_context = initialize_scenario_context(scenario.get_step_definition_class_name(), "test_set_up_and_tear_down", f"{self.step_definition_folder_path}/test_set_up_and_tear_down.py")
        
        self.assertIsNotNone(getattr(scenario_context, 'set_up', None))
        self.assertIsNotNone(getattr(scenario_context, 'tear_down', None))

    def test_generate_file_with_name(self):
        Scenario("Scheduled sprinkling")
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/scheduled_sprinkling.py"))
        
    def test_auto_generate_methods_And(self):
        scenario = Scenario("Scheduled sprinkling")
        
        scenario.Given("water supply is normal")\
                .And("all timers are set to 4:00:00 am")
        
        self.assertEqual("given_all_timers_are_set_to_4_00_00_am", scenario.get_groups()[0].get_all_steps()[1].get_method_name())

    def test_full_text(self):
        scenario = Scenario("Simple Google search")

        scenario.Given("a web browser is on the Google page")\
                \
                .When("the search phrase \"panda\" is entered")\
                \
                .Then("results for \"panda\" are shown")\
                .And("the related results include \"Panda Express\"")\
                .But("the related results do not include \"pandemonium\"")

        self.assertEqual(
            ("\nScenario: Simple Google search\n"
            "  Given a web browser is on the Google page\n"
            "  When the search phrase \"panda\" is entered\n"
            "  Then results for \"panda\" are shown\n"
            "  And the related results include \"Panda Express\"\n"
            "  But the related results do not include \"pandemonium\"\n"),
            scenario.full_text()
        )

    def test_Given_should_not_appear_after_a_When(self):
        with self.assertRaises(ValueError) as e:
            Scenario("Scheduled sprinkling")\
            .When("the time is 4:00:00 am")\
            .Given("water supply is normal")

        self.assertEqual("Given: out of place", str(e.exception))

    def test_Given_should_not_appear_after_a_Then(self):
        with self.assertRaises(ValueError) as e:
            Scenario("Scheduled sprinkling")\
            .Then("sprinkler A should emit water no later than 4:00:05 am")\
            .Given("timer of sprinkler A is set to 4:00:00 am")

        self.assertEqual("Given: out of place", str(e.exception))

    def test_And_should_not_appear_without_any_lead_step(self):
        with self.assertRaises(ValueError) as e:
            Scenario("Scheduled sprinkling")\
            .And("all timers are set to 4:00:00 am")
                    
        self.assertEqual("And: must not be the first clause", str(e.exception))

    def test_But_should_not_appear_without_any_lead_step(self):
        with self.assertRaises(ValueError) as e:
            Scenario("Scheduled sprinkling")\
            .But("timer of sprinklers B and C are not set")
                    
        self.assertEqual("But: must not be the first clause", str(e.exception))

    def test_default_step_definition_should_show_yellow_step(self):
        scenario = Scenario("Scheduled sprinkling")

        scenario.Given("water supply is normal")\
                .execute()
        
        self.assertTrue(f"{YELLOW}Given water supply is normal{RESET}\n" in scenario.result_printout())

    def test_passed_step_definition_should_show_green_step(self):
        os.makedirs(self.step_definition_folder_path, exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/simple_google_search.py", f"{self.step_definition_folder_path}/simple_google_search.py")
        scenario = Scenario("Simple Google search")

        scenario.Given("a web browser is on the webpage page", webpage = None)\
                .execute()

        self.assertTrue(f"{GREEN}Given a web browser is on the webpage page{RESET}\n" in scenario.result_printout())

    def test_failed_step_definition_should_show_red_step_and_traceback_message(self):
        os.makedirs(self.step_definition_folder_path, exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/simple_google_search.py", f"{self.step_definition_folder_path}/simple_google_search.py")
        scenario = Scenario("Simple Google search")

        scenario.Given("a web browser is on the webpage page")\
                .execute()

        self.assertTrue(f"{RED}Given a web browser is on the webpage page{RESET}\n" in scenario.result_printout())
        self.assertTrue("Traceback (most recent call last):" in scenario.result_printout())

    def test_skipped_step_definition_should_show_gray_step(self):
        os.makedirs(self.step_definition_folder_path, exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/simple_google_search.py", f"{self.step_definition_folder_path}/simple_google_search.py")
        scenario = Scenario("Simple Google search")

        scenario.Given("a web browser is on the webpage page")\
                .When("the search phrase keyword is entered")\
                .execute()

        self.assertTrue(f"{GRAY}When the search phrase keyword is entered{RESET}\n" in scenario.result_printout())

    def test_default_scenario_step_definition_class_name_and_file_name(self):
        scenario = Scenario()

        self.assertEqual("StepDefinitions", scenario.get_step_definition_class_name())
        self.assertEqual("step_definitions", scenario.get_step_definition_file_name())

    def test_generate_file_without_scenario_name(self):
        Scenario()
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/step_definitions.py"))

    def test_generate_file_duplicated_empty_scenario_name(self):
        Scenario()
        Scenario()
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/step_definitions.py"))
        self.assertEqual(1, len(os.listdir(f"{self.step_definition_folder_path}/")))

    def test_generate_file_duplicated_scenario_name(self):
        Scenario("Scheduled sprinkling")
        Scenario("Scheduled sprinkling")
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/scheduled_sprinkling.py"))
        self.assertEqual(1, len(os.listdir(f"{self.step_definition_folder_path}/")))
        
    def test_duplicate_scenarios_should_generate_step_definition_only_once(self):
        Scenario("Simple Google search")\
        .Given("a web browser is on the Google page")\
        \
        .When("the search phrase \"panda\" is entered")\
        \
        .Then("results for \"panda\" are shown")\
        .And("the related results include \"Panda Express\"")\
        .But("the related results do not include \"pandemonium\"")
                  
        Scenario("Simple Google search")\
        .Given("a web browser is on the Google page")\
        \
        .When("the search phrase \"panda\" is entered")\
        \
        .Then("results for \"panda\" are shown")\
        .And("the related results include \"Panda Express\"")\
        .But("the related results do not include \"pandemonium\"")
        
        whole_class_text = Path(f"{self.step_definition_folder_path}/simple_google_search.py").read_text()
        
        self.assertEqual(1, whole_class_text.count("given_a_web_browser_is_on_the_google_page(self)"))
        self.assertEqual(1, whole_class_text.count("when_the_search_phrase_panda_is_entered(self)"))
        self.assertEqual(1, whole_class_text.count("then_results_for_panda_are_shown(self)"))
        self.assertEqual(1, whole_class_text.count("then_the_related_results_include_panda_express_(self)"))
        self.assertEqual(1, whole_class_text.count("then_the_related_results_do_not_include_pandemonium_(self)"))

    def test_duplicate_steps_in_the_same_scenario_should_generate_step_definition_only_once(self):
        Scenario("Simple Google search")\
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
        
        whole_class_text = Path(f"{self.step_definition_folder_path}/simple_google_search.py").read_text()
        
        self.assertEqual(1, whole_class_text.count("given_a_web_browser_is_on_the_google_page(self)"))
        self.assertEqual(1, whole_class_text.count("when_the_search_phrase_panda_is_entered(self)"))
        self.assertEqual(1, whole_class_text.count("then_results_for_panda_are_shown(self)"))
        self.assertEqual(1, whole_class_text.count("then_the_related_results_include_panda_express_(self)"))
        self.assertEqual(1, whole_class_text.count("then_the_related_results_do_not_include_pandemonium_(self)"))

    def test_continuing_execution_on_a_step(self):
        os.makedirs(self.step_definition_folder_path, exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/continuing_execution_at_a_specific_step.py", f"{self.step_definition_folder_path}/continuing_execution_at_a_specific_step.py")

        scenario = Scenario("Continuing execution at a specific step")
        scenario.Given("Some precondition")\
                .When("An event happens")\
                .Then("The step is true")\
                .And("The step fails but it adds a tag to continue execution", continue_after_failure=True)\
                .Then("The step should be executed and it fails")\
                .execute()

        self.assertTrue(f"{RED}And The step fails but it adds a tag to continue execution" in scenario.result_printout())
        self.assertTrue(f"{RED}Then The step should be executed and it fails" in scenario.result_printout())
        
    def test_set_continue_after_failure_on_Given_and_When_group_should_give_warnings(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            Scenario("Continuing execution at a specific step")\
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
        os.makedirs(self.step_definition_folder_path, exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/set_up_should_be_executed.py", f"{self.step_definition_folder_path}/set_up_should_be_executed.py")
        
        scenario = Scenario("Set Up Should Be Executed")

        scenario.Given("a web browser is on the Google page")\
                \
                .When("the search phrase \"panda\" is entered")\
                \
                .Then("results for \"panda\" are shown")\
                .execute()

        self.assertTrue("Set Up Executed" in scenario.get_output_message())
    
    def test_do_tear_down_after_finish_execute_scenario(self):
        os.makedirs(self.step_definition_folder_path, exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/tear_down_should_be_executed.py", f"{self.step_definition_folder_path}/tear_down_should_be_executed.py")
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        scenario = Scenario("Tear Down Should Be Executed")

        scenario.Given("a web browser is on the Google page")\
                \
                .When("the search phrase \"panda\" is entered")\
                \
                .Then("results for \"panda\" are shown")\
                .execute()

        sys.stdout = sys.__stdout__

        self.assertTrue("Tear Down Executed" in scenario.get_output_message()) 
        
    def test_do_tear_down_after_fail_execute_scenario(self):
        os.makedirs(self.step_definition_folder_path, exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/tear_down_should_be_executed.py", f"{self.step_definition_folder_path}/tear_down_should_be_executed.py")

        scenario = Scenario("Tear Down Should Be Executed")

        scenario.Given("a web browser is on the Google page")\
                \
                .When("the search phrase \"panda\" is entered")\
                \
                .Then("results for \"capybara\" are shown")\
                .execute()

        self.assertTrue("Capybara Not Exist" in scenario.result_printout())
        self.assertTrue("Tear Down Executed" in scenario.get_output_message())

if __name__ == '__main__':
    unittest.main()
