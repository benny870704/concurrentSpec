import os
import xml.etree.ElementTree as ET
from ..status import Status
from ..utils import is_instance
from ..feature import FeatureManager

OUTPUT_FILE = "test_result/test_result.xml"

def generate_test_result_in_xml(output_file=None):
    print("generating xml test result...")
    all_scenario_count = 0
    all_passed_scenario_count = 0
    all_execution_time = 0

    test_result = ET.Element("testsuites")
    test_result.set("name", "All Features")

    for feature_name, feature in FeatureManager.get_features().items():
        scenario_count = len(feature["scenarios"])
        passed_scenario_count = 0
        feature_execution_time = 0
        for scenario in feature["scenarios"]:
            feature_execution_time += scenario.execution_time
            if scenario.execution_result == Status.passed: passed_scenario_count += 1
        
        all_scenario_count += scenario_count
        all_passed_scenario_count += passed_scenario_count
        all_execution_time += feature_execution_time
        
        test_suite = ET.SubElement(test_result, "testsuite")
        test_suite.set("name", feature_name)
        test_suite.set("tests", str(scenario_count))
        test_suite.set("failures", str(scenario_count - passed_scenario_count))
        test_suite.set("errors", "0")
        test_suite.set("time", str(feature_execution_time))

        for scenario in feature["scenarios"]:
            if is_instance(scenario, 'ScenarioOutline') and scenario.has_examples():
                for iterate_count in range(len(scenario.examples)):
                    add_scenario_outline_as_test_case(test_suite, feature_name, scenario, iterate_count)
            else:
                add_scenario_as_test_case(test_suite, feature_name, scenario)

    test_result.set("errors", "0")
    test_result.set("time", str(all_execution_time))
    test_result.set("tests", str(all_scenario_count))
    test_result.set("failures", str(all_scenario_count - all_passed_scenario_count))

    tree = ET.ElementTree(test_result)
    ET.indent(tree, space="\t", level=0)
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        tree.write(output_file, encoding="utf-8")
    else:
        os.makedirs("test_result/", exist_ok=True)
        tree.write(OUTPUT_FILE, encoding="utf-8")
    print("done!")


def add_scenario_as_test_case(test_suite, feature_name, scenario, iterate_count=None):
    test_case = ET.SubElement(test_suite, "testcase")
    test_case_name = scenario.get_scenario_name() if iterate_count is None else scenario.get_scenario_name() + f" - Example #{iterate_count+1}"
    test_case.set("name", test_case_name)
    test_case.set("status", "run")
    test_case.set("result", "completed")
    test_case.set("time", str(scenario.execution_time))
    test_case.set("classname", feature_name)
    
    if scenario.execution_result == Status.failed or scenario.execution_result == Status.undefined:
        failure_message = ET.SubElement(test_case, "failure")
        failure_message.set("message", scenario.error_messages)
        failure_message.set("type", "")
        failure_message.text = scenario.traceback_messages

    system_out = ET.SubElement(test_case, "system-out")
    system_out.text = scenario.full_text() if iterate_count is None else scenario.full_text(iterate_count)

def add_scenario_outline_as_test_case(test_suite, feature_name, scenario, iterate_count):
    test_case = ET.SubElement(test_suite, "testcase")
    test_case_name = scenario.get_scenario_name() + f" - Example #{iterate_count+1}"
    test_case.set("name", test_case_name)
    test_case.set("status", "run")
    test_case.set("result", "completed")
    test_case.set("time", str(scenario.example_execution_result[iterate_count]["execution_time"]))
    test_case.set("classname", feature_name)

    example_execution_result = scenario.example_execution_result[iterate_count]["execution_result"]
    if example_execution_result == Status.failed or example_execution_result == Status.undefined:
        failure_message = ET.SubElement(test_case, "failure")
        failure_message.set("message", scenario.example_execution_result[iterate_count]["error_messages"])
        failure_message.set("type", "")
        failure_message.text = scenario.example_execution_result[iterate_count]["traceback_messages"]

    system_out = ET.SubElement(test_case, "system-out")
    system_out.text = scenario.full_text(iterate_count)
