# import argparse
# import unittest
# import sys
# sys.path.append("../")
# from src.custom_test_loader import CustomTestLoader
# from src.custom_test_result import ShortTracebackResult
# from src.formatter.json_formatter import JsonFormatter
# from src.reporter.test_result_summarizer import TestResultSummarizer
# from src.reporter.test_result_xml_generator import generate_test_result_in_xml
# from src.reporter.test_result_html_generator import generate_test_result_in_html

# def main():
#     supported_format = ["json", "json.pretty", "xml", "html"]
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-p", "--path", help = "project path")
#     parser.add_argument("-t", "--tags", help = "scenarios with the given tags will be executed")
#     parser.add_argument("-f", "--format", help = "output format")

#     args = parser.parse_args()
#     project_path = args.path
#     tags = args.tags
#     format = args.format
    
#     if format != None and format not in supported_format: raise parser.error("Unsupported format")

#     suite = unittest.TestSuite()
#     try:
#         loader = CustomTestLoader()
#         if tags is not None: loader.add_filter_tag(tags.split(','))
#         suite = loader.loadTestsFromProjectPath(project_path)
#     except ImportError:
#         raise Exception(f"\033[0;31mDomain path: \"{project_path}\" should contain __init__.py\033[0m")

#     if suite.countTestCases() == 0:
#         raise Exception(f"\033[0;31mDomain path: \"{project_path}\" doesn't have any test case\033[0m")

#     runner = unittest.TextTestRunner(resultclass=ShortTracebackResult)
#     runner.run(suite)

#     summarizer = TestResultSummarizer()
#     summarizer.summarize()
#     print(summarizer.get_summary_printout())

#     if format == "json": print(JsonFormatter().format_result())
#     elif format == "json.pretty": print(JsonFormatter().format_result(pretty=True))
#     elif format == "xml": generate_test_result_in_xml()
#     elif format == "html": generate_test_result_in_html()

import sys
sys.path.append("../")
from src.main import main

if __name__ == '__main__':
    main()
