import sys
import shutil
import os.path
import warnings
import unittest
import traceback
from pathlib import Path
sys.path.append("../")
from concurrentSpec.src.scenario import Scenario
from concurrentSpec.src.feature import Feature, FeatureManager

class TestFeature(unittest.TestCase):
    def setUp(self):
        self.test_path = str(Path(traceback.extract_stack()[-1].filename).parent)
        self.step_definition_folder_name = "step_definitions"
        self.step_definition_folder_path = f"{self.test_path}/{self.step_definition_folder_name}/"
    
    def tearDown(self):
        FeatureManager.clear()
        if os.path.exists(self.step_definition_folder_path):
            shutil.rmtree(self.step_definition_folder_path)

    def test_feature_method(self):
        Feature(feature_name="Google search", feature_description="Use Google to search everything")

        self.assertTrue("Google search" in FeatureManager.get_features())

    def test_add_scenario_to_feature(self):
        Feature(feature_name="Scheduled sprinkling", feature_description="Sprinkler sprinkles when time arrived.")
        scenario = Scenario("All sprinklers sprinkles on time")

        self.assertTrue(scenario.feature_name in FeatureManager.get_features())
        self.assertTrue(scenario in FeatureManager.get_features()[scenario.feature_name]["scenarios"])

    def test_generate_folder_with_feature_name(self):
        Feature(feature_name="Google search", feature_description="Use Google to search everything")
        Scenario("Simple Google search")
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/google_search/"))
        self.assertEqual(1, len(os.listdir(f"{self.step_definition_folder_path}/google_search/")))
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/google_search/simple_google_search.py"))

    def test_feature_is_duplicated(self):
        Feature("Scheduled sprinkling", "Sprinkler sprinkles on time.")
        with warnings.catch_warnings(record=True) as caught_warnings:
            Feature("Scheduled sprinkling", "Sprinkler sprinkles on time.")

        self.assertTrue("[WARNING] Feature: Scheduled sprinkling has already existed" in str(caught_warnings[0].message))

    def test_declare_two_different_features_in_one_file(self):
        Feature("Scheduled sprinkling", "Sprinkler sprinkles on time.")
        with self.assertRaises(RuntimeError) as e:
            Feature("Scheduled sprinkling 1", "Sprinkler sprinkles on time.")

        self.assertTrue("Declare more than one feature in a file is not allowed." in str(e.exception))

    def test_feature_with_default_value(self):
        Feature()

        self.assertTrue("" in FeatureManager.get_features())
        self.assertEqual("", FeatureManager.get_features()[""]["description"])

    def test_add_duplicate_scenario_name_in_feature(self):
        Feature(feature_name="Scheduled sprinkling", feature_description="Sprinkler sprinkles when time arrived.")
        Scenario("All sprinklers sprinkles on time")
        with warnings.catch_warnings(record=True) as caught_warnings:
            Scenario("All sprinklers sprinkles on time")

        self.assertEqual("\033[1;93m[WARNING] Scenario: All sprinklers sprinkles on time is already in Feature: Scheduled sprinkling\033[0m", str(caught_warnings[0].message))
        self.assertEqual(1, len(FeatureManager.get_features()["Scheduled sprinkling"]["scenarios"]))

    def test_empty_name_of_scenario_should_add_to_feature(self):
        Feature(feature_name="Scheduled sprinkling", feature_description="Sprinkler sprinkles when time arrived.")
        Scenario()
        Scenario()

        self.assertEqual(2, len(FeatureManager.get_features()["Scheduled sprinkling"]["scenarios"]))

    def test_both_duplicated_empty_name_of_scenarios_should_add_to_feature(self):
        Feature()
        Scenario()
        Scenario()

        self.assertEqual(2, len(FeatureManager.get_features()[""]["scenarios"]))

    def test_add_duplicated_name_of_scenarios_to_a_feature_should_show_warning(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            Feature(feature_name="Google search", feature_description="Use Google to search everything")
            Scenario("Simple Google search")
            Scenario("Simple Google search")

        self.assertEqual("\033[1;93m[WARNING] Scenario: Simple Google search is already in Feature: Google search\033[0m", str(caught_warnings[0].message))
        self.assertEqual(1, len(FeatureManager.get_features()["Google search"]["scenarios"]))

    def test_generate_folder_without_feature_name(self):
        Feature()
        Scenario("Simple Google search")
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/feature/"))
        self.assertEqual(1, len(os.listdir(f"{self.step_definition_folder_path}/feature/")))
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/feature/simple_google_search.py"))

    def test_generate_folder_with_feature_name_without_scenario(self):
        Feature(feature_name="Google search", feature_description="Use Google to search everything")
        
        self.assertFalse(os.path.exists(f"{self.step_definition_folder_path}/google_search/"))

    def test_generate_folder_with_feature_name_and_add_scenario_without_scenario_name(self):
        Feature(feature_name="Google search", feature_description="Use Google to search everything")
        Scenario()
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/google_search/"))
        self.assertEqual(1, len(os.listdir(f"{self.step_definition_folder_path}/google_search/")))
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/google_search/step_definitions.py"))

    def test_generate_folder_without_feature_name_and_add_scenario_without_scenario_name(self):
        Feature()
        Scenario()
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/feature/"))
        self.assertEqual(1, len(os.listdir(f"{self.step_definition_folder_path}/feature/")))
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/feature/step_definitions.py"))

    def test_generate_folder_with_feature_name_and_add_duplicate_scenarios_without_scenario_name(self):
        Feature(feature_name="Google search", feature_description="Use Google to search everything")
        Scenario()
        Scenario()
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/google_search/"))
        self.assertEqual(1, len(os.listdir(f"{self.step_definition_folder_path}/google_search/")))
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/google_search/step_definitions.py"))
        self.assertEqual(2, len(FeatureManager.get_features()["Google search"]["scenarios"]))

    def test_generate_folder_without_feature_name_and_add_duplicate_scenarios_without_scenario_name(self):
        Feature()
        Scenario()
        Scenario()
        
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/feature/"))
        self.assertEqual(1, len(os.listdir(f"{self.step_definition_folder_path}/feature/")))
        self.assertTrue(os.path.exists(f"{self.step_definition_folder_path}/feature/step_definitions.py"))
        self.assertEqual(2, len(FeatureManager.get_features()[""]["scenarios"]))

    def test_get_features(self):
        Feature(feature_name="Google search", feature_description="Use Google to search everything")
        Scenario("Simple Google search")
        
        self.assertEqual(1, len(FeatureManager.get_features()))
        self.assertTrue("Google search" in FeatureManager.get_features())