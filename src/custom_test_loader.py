import os
import sys
import inspect
import importlib
import unittest
# from .tag_expressions import TagExpressions
from .tag_expressions_v2 import TagExpressionsV2

test_method_to_tag_map = {}
test_class_to_tag_map = {}

class CustomTestLoader(unittest.TestLoader):

    @classmethod
    def test_method_to_tag(cls, test_method_name, tag_name):
        if test_method_name not in test_method_to_tag_map:
            test_method_to_tag_map.update({test_method_name: [tag_name]})
        elif tag_name not in test_method_to_tag_map[test_method_name]:
            test_method_to_tag_map[test_method_name].append(tag_name)

    @classmethod
    def test_class_to_tag(cls, test_class_name, tag_name):
        if test_class_name not in test_class_to_tag_map:
            test_class_to_tag_map.update({test_class_name: [tag_name]})
        else:
            test_class_to_tag_map[test_class_name].append(tag_name)

    def __init__(self):
        self.filtered = False
        # self.tag_expression = TagExpressions()
        self.tag_expression = TagExpressionsV2()

    def add_filter_tag(self, tags):
        if tags:
            if not self.filtered: self.filtered = True
            # self.tag_expression.add_filter_tags(tags)
            self.tag_expression.parse(tags)
    
    def __match_filtered_tags(self, method_name):
        feature_tags = test_class_to_tag_map[method_name.split('.')[0]] if method_name.split('.')[0] in test_class_to_tag_map else []
        scenario_tags = test_method_to_tag_map[method_name] if method_name in test_method_to_tag_map else []

        return self.tag_expression.match(feature_tags + scenario_tags)
    
    def find_test_modules(self, path):
        """Find all Python modules in the given directory tree that inherit unittest.TestCase."""
        test_modules = []
        for dirpath, dirnames, filenames in os.walk(path):
            sys.path.append(os.path.abspath(dirpath))
            for filename in filenames:
                if filename.endswith('.py'):
                    module_name = os.path.splitext(filename)[0]
                    module_path = os.path.join(dirpath, module_name).replace('/', '.').replace('\\', '.')
                    try:
                        module = importlib.import_module(module_path)
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj) and issubclass(obj, unittest.TestCase):
                                test_modules.append(module)
                                break
                    except:
                        pass

        return test_modules

    def loadTestsFromTestCase(self, testCaseClass) -> unittest.suite.TestSuite:
        tests = super().loadTestsFromTestCase(testCaseClass)
        suite = unittest.TestSuite()
        for test in tests:
            if not self.filtered:
                suite.addTest(test)
            elif self.__match_filtered_tags(f"{test.__class__.__name__}.{test._testMethodName}"):
                suite.addTest(test)
                
        return suite
    
    def loadTestsFromProjectPath(self, project_path):
        modules = self.find_test_modules(project_path)
        tests = [unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules]
        suite = unittest.TestSuite()

        for test_class in tests:
            for tests_in_a_feature in test_class._tests:
                for test in tests_in_a_feature._tests:
                    if not self.filtered:
                        suite.addTest(test)
                    elif self.__match_filtered_tags(f"{test.__class__.__name__}.{test._testMethodName}"):
                        suite.addTest(test)
        return suite
    
    def loadTestsFromNames(self, names, module=None) -> unittest.suite.TestSuite:
        raise Exception("unsupported yet")
    
    def loadTestsFromName(self, name, module=None) -> unittest.suite.TestSuite:
        raise Exception("unsupported yet")
    
    def loadTestsFromModule(self, module) -> unittest.suite.TestSuite:
        module = importlib.import_module(module)
        tests = unittest.defaultTestLoader.loadTestsFromModule(module)
        suite = unittest.TestSuite()

        for tests_in_a_feature in tests._tests:
            for test in tests_in_a_feature._tests:
                if not self.filtered:
                    suite.addTest(test)
                elif self.__match_filtered_tags(f"{test.__class__.__name__}.{test._testMethodName}"):
                    suite.addTest(test)
        return suite

