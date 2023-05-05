import sys, io
import shutil
import os.path
import unittest
import traceback
from pathlib import Path
sys.path.append("../../")
from concurrentSpec.src.scenario import Scenario
from concurrentSpec.src.scenario_outline import ScenarioOutline
from concurrentSpec.src.background import Background
from concurrentSpec.src.feature import Feature, FeatureManager

class TestBackground(unittest.TestCase):
    def setUp(self):
        self.test_path = str(Path(traceback.extract_stack()[-1].filename).parent)
        FeatureManager.console_output = False
    
    def tearDown(self):
        FeatureManager.clear()
        dir = f"{self.test_path}/steps/"
        if os.path.exists(dir):
            shutil.rmtree(dir)

    def test_default_background_step_definition_class_name_and_file_name(self):
        background = Background()

        self.assertEqual("Background", background.get_step_definition_class_name())
        self.assertEqual("background", background.get_step_definition_file_name())

    def test_background_steps_class_name_and_file_name(self):
        background = Background("Scheduled sprinkling setup")
        self.assertEqual("ScheduledSprinklingSetup", background.get_step_definition_class_name())
        self.assertEqual("scheduled_sprinkling_setup", background.get_step_definition_file_name())

    def test_generate_file_with_name(self):
        Background("Scheduled sprinkling setup")
        
        self.assertTrue(os.path.exists(f"{self.test_path}/steps/scheduled_sprinkling_setup.py"))

    def test_auto_generate_methods_And(self):
        background = Background("Scheduled sprinkling setup")
        
        background.Given("water supply is normal")\
                .And("all timers are set to 4:00:00 am")
        
        self.assertEqual("given_all_timers_are_set_to_4_00_00_am", background.get_groups()[0].get_all_steps()[1].get_method_name())

    def test_full_text(self):
        background = Background("Simple Google search")

        background.Given("a web browser is on the Google page")\

        self.assertEqual(
            ("\n  \033[1;34mBackground: Simple Google search\033[0m\n"
            "    \033[0mGiven a web browser is on the Google page\033[0m\n"),
            background.result_printout()
        )

    def test_And_should_not_appear_without_any_lead_step(self):
        with self.assertRaises(ValueError) as e:
            Background("Scheduled sprinkling setup")\
            .And("all timers are set to 4:00:00 am")
                    
        self.assertEqual("And: must not be the first clause", str(e.exception))

    def test_generate_file_without_background_name(self):
        Background()
        
        self.assertTrue(os.path.exists(f"{self.test_path}/steps/background.py"))

    def test_generate_file_duplicated_empty_background_name(self):
        Background()
        Background()
        
        self.assertTrue(os.path.exists(f"{self.test_path}/steps/background.py"))
        self.assertEqual(1, len(os.listdir(f"{self.test_path}/steps/")))

    def test_generate_file_duplicated_background_name(self):
        Background("Scheduled sprinkling setup")
        Background("Scheduled sprinkling setup")
        
        self.assertTrue(os.path.exists(f"{self.test_path}/steps/scheduled_sprinkling_setup.py"))
        self.assertEqual(1, len(os.listdir(f"{self.test_path}/steps/")))

    def test_run_background_with_feature_and_one_scenario(self):
        os.makedirs(f"{self.test_path}/steps/scheduled_sprinkling_feature", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/scheduled_sprinkling/scheduled_sprinkling_setup.py", f"{self.test_path}/steps/scheduled_sprinkling_feature/scheduled_sprinkling_setup.py")
        shutil.copyfile(f"{self.test_path}/test_data/scheduled_sprinkling/scheduled_sprinkling_of_timer_a.py", f"{self.test_path}/steps/scheduled_sprinkling_feature/scheduled_sprinkling_of_timer_a.py")

        sys.stdout = io.StringIO()
        
        Feature("Scheduled sprinkling feature")
        Background("Scheduled sprinkling setup")\
            .Given("Timer A")

        Scenario("Scheduled sprinkling of timer a")\
            .When("Timer A is open")\
            .Then("Timer A should close in 3 second")\
            .execute()

        sys.stdout = sys.__stdout__

    def test_run_background_with_feature_and_two_scenarios(self):
        os.makedirs(f"{self.test_path}/steps/scheduled_sprinkling_feature", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/scheduled_sprinkling/scheduled_sprinkling_setup.py", f"{self.test_path}/steps/scheduled_sprinkling_feature/scheduled_sprinkling_setup.py")
        shutil.copyfile(f"{self.test_path}/test_data/scheduled_sprinkling/scheduled_sprinkling_of_timer_a.py", f"{self.test_path}/steps/scheduled_sprinkling_feature/scheduled_sprinkling_of_timer_a.py")
        shutil.copyfile(f"{self.test_path}/test_data/scheduled_sprinkling/scheduled_sprinkling_of_timer_b.py", f"{self.test_path}/steps/scheduled_sprinkling_feature/scheduled_sprinkling_of_timer_b.py")
        shutil.copyfile(f"{self.test_path}/test_data/scheduled_sprinkling/scheduled_sprinkling_of_timer_a_and_b.py", f"{self.test_path}/steps/scheduled_sprinkling_feature/scheduled_sprinkling_of_timer_a_and_b.py")

        sys.stdout = io.StringIO()

        Feature("Scheduled sprinkling feature")
        Background("scheduled sprinkling setup")\
            .Given("Timer A")\
            .And("Timer B")

        Scenario("Scheduled sprinkling of timer a")\
            .When("Timer A is open")\
            .Then("Timer A should close in 3 second")\
            .execute()

        Scenario("Scheduled sprinkling of timer b")\
            .When("Timer B is scheduled to open")\
            .Then("Timer B should open in 3 second")\
            .execute()

        Scenario("Scheduled sprinkling of timer a and b")\
            .When("Timer A is scheduled to open")\
            .And("Timer B is open")\
            .Then("Timer A should open in 3 second")\
            .And("Timer B should close in 3 second")\
            .execute()

        sys.stdout = sys.__stdout__

    def test_And_should_not_appear_without_any_lead_step(self):
        with self.assertRaises(ValueError) as e:
            Background("Scheduled sprinkling setup")\
            .And("all timers are set to 4:00:00 am")
                    
        self.assertEqual("And: must not be the first clause", str(e.exception))

    def test_do_set_up_before_executing_scenario(self):
        os.makedirs(f"{self.test_path}/steps", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/set_up_should_be_executed.py", f"{self.test_path}/steps/set_up_should_be_executed.py")
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        Background("Set Up Should Be Executed")\
            .Given("a web browser is on the Google page")\
            .execute()

        sys.stdout = sys.__stdout__

        self.assertTrue("Set Up Executed" in captured_output.getvalue())

    # do background duplicated?
    def test_duplicate_backgrounds_should_generate_step_definition_only_once(self):
        Background("Simple Google search")\
        .Given("a web browser is on the Google page")\
                  
        Background("Simple Google search")\
        .Given("a web browser is on the Google page")\
        
        whole_class_text = Path(f"{self.test_path}/steps/simple_google_search.py").read_text()
        
        self.assertEqual(1, whole_class_text.count("given_a_web_browser_is_on_the_google_page(self)"))

    def test_duplicate_steps_in_the_same_background_should_generate_step_definition_only_once(self):
        Background("Simple Google search")\
        .Given("a web browser is on the Google page")\
        .Given("a web browser is on the Google page")\
        
        whole_class_text = Path(f"{self.test_path}/steps/simple_google_search.py").read_text()
        
        self.assertEqual(1, whole_class_text.count("given_a_web_browser_is_on_the_google_page(self)"))

    def test_background_work_with_scenario_outline(self):
        os.makedirs(f"{self.test_path}/steps/scheduled_sprinkling_feature", exist_ok = True)
        shutil.copyfile(f"{self.test_path}/test_data/scheduled_sprinkling/scheduled_sprinkling_setup.py", f"{self.test_path}/steps/scheduled_sprinkling_feature/scheduled_sprinkling_setup.py")
        shutil.copyfile(f"{self.test_path}/test_data/scheduled_sprinkling/scheduled_sprinkling_of_timer_c.py", f"{self.test_path}/steps/scheduled_sprinkling_feature/scheduled_sprinkling_of_timer_c.py")

        sys.stdout = io.StringIO()

        Feature("Scheduled sprinkling feature")
        Background("Scheduled sprinkling setup")\
            .Given("Timer C")

        ScenarioOutline("Scheduled sprinkling of timer c")\
            .When("Timer C is <operation>")\
            .Then("Timer C should <status> in 3 second")\
            .WithExamples("""
                | operation      | status |
                | open           | close  |
                | scheduled_open | open   |
            """).execute()

        sys.stdout = sys.__stdout__
