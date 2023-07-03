import argparse
import unittest
import io
# import sys
# sys.path.append("../../")
from .custom_test_loader import CustomTestLoader
from .custom_test_result import ShortTracebackResult
from .feature import FeatureManager
from .formatter.json_formatter import JsonFormatter
from .reporter.test_result_summarizer import TestResultSummarizer
from .reporter.test_result_xml_generator import generate_test_result_in_xml
from .reporter.test_result_html_generator import generate_test_result_in_html

def main():
    supported_format = ["json", "json.pretty", "xml", "html"]
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help = "project path")
    # parser.add_argument("-t", "--tags", action="append", nargs="+", help = "scenarios with the given tags will be executed") # tag expression v1
    parser.add_argument("-t", "--tags", help = "scenarios with the given tags will be executed") # tag expression v2
    parser.add_argument("-f", "--format", help = "output format")
    parser.add_argument("-o", "--output", help = "output file")

    args = parser.parse_args()
    project_path = args.path
    tags = args.tags
    format = args.format
    output_file = args.output
    
    if format != None and format not in supported_format: raise parser.error("Unsupported format")

    suite = unittest.TestSuite()
    try:
        loader = CustomTestLoader()
        if tags is not None: loader.add_filter_tag(tags)
        suite = loader.loadTestsFromProjectPath(project_path)
    except ImportError:
        raise Exception(f"\033[0;31mDomain path: \"{project_path}\" should contain __init__.py\033[0m")

    if suite.countTestCases() == 0:
        raise Exception(f"\033[0;31mDomain path: \"{project_path}\" doesn't have any test case\033[0m")

    if format != None and format.find("json") != -1: FeatureManager.console_output = False
    FeatureManager.capture_output = False
    # runner = unittest.TextTestRunner(resultclass=ShortTracebackResult)
    runner = unittest.TextTestRunner(resultclass=ShortTracebackResult, stream=io.StringIO())
    runner.run(suite)

    summarizer = TestResultSummarizer()
    summarizer.summarize()
    print(summarizer.get_summary_printout()) if summarizer.feature_count > 0 else print("\n")

    if format == "json": print(JsonFormatter().format_result(output_file=output_file))
    elif format == "json.pretty": print(JsonFormatter().format_result(pretty=True, output_file=output_file))
    elif format == "xml": generate_test_result_in_xml(output_file=output_file)
    elif format == "html": generate_test_result_in_html(output_file=output_file)

if __name__ == '__main__':
    main()
