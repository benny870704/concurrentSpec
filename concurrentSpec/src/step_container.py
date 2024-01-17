import re
import os
import warnings
import traceback
from enum import Enum
from pathlib import Path
from .utils import *
from .step import Step
from .feature import FeatureManager
from .sequential_group import SequentialGroup

STACK_FRAME_COUNT = 3
STEP_DEFINITIONS_FOLDER_NAME = "step_definitions"

class ChildType(Enum):
    Background = 0
    Scenario = 1
    ScenarioOutline = 2

    def __eq__(self, other_type) -> bool:
        if isinstance(other_type, str):
            return self.name == other_type
        return super(ChildType, self).__eq__(other_type)

class StepContainer:
    def __init__(self, name="", step_definition_folder_path=None, groups=None):
        self.name = name
        self.child_type = self.__get_child_type()
        self.sequential_groups = [] if groups == None else groups
        self.step_definition_folder_path = step_definition_folder_path if step_definition_folder_path is not None else str(Path(traceback.extract_stack()[-STACK_FRAME_COUNT].filename).parent) + f"/{STEP_DEFINITIONS_FOLDER_NAME}/"
        self.step_definition_class_name = self.__generate_step_definition_class_name()
        self.step_definition_file_name = self.__generate_step_definition_file_name()

        class_name, method_name, self.location = get_where_the_class_is_declared(STACK_FRAME_COUNT)
        self.feature_name = FeatureManager.get_feature_name_from_class_name(class_name)
        if self.child_type != ChildType.Background: FeatureManager.add_scenario(self, class_name, method_name)
        else: FeatureManager.add_background(self, class_name)
        
        os.makedirs(f"{self.step_definition_folder_path}", exist_ok = True)

        self.step_definition_file_path = f"{self.step_definition_folder_path}{self.step_definition_file_name}.py"
        self.__generate_step_definition_file()

        self.whole_class_text = Path(self.step_definition_file_path).read_text()

    def __get_child_type(self):
        if type(self).__name__ == "Scenario": return ChildType.Scenario
        elif type(self).__name__ == "ScenarioOutline": return ChildType.ScenarioOutline
        elif type(self).__name__ == "Background": return ChildType.Background

    def __generate_step_definition_class_name(self):
        if self.name == "":
            return "StepDefinitions" if self.child_type != ChildType.Background else "Background"
        return re.sub(r'\W+', '', re.sub(r'\w+', lambda m:m.group(0).capitalize(), f"{self.name}"))

    def __generate_step_definition_file_name(self):
        if self.name == "":
            return "step_definitions" if self.child_type != ChildType.Background else "background"
        return re.sub(r'\W+', '_', re.sub(r'\w+', lambda m:m.group(0).lower(), f"{self.name}"))

    def __generate_feature_folder_name(self):
        if self.feature_name == "":
            return "feature/"
        return re.sub(r'\W+', '_', re.sub(r'\w+', lambda m:m.group(0).lower(), f"{self.feature_name}")) + "/"
    
    def __generate_step_definition_file(self):
        with open(self.step_definition_file_path, "a") as f:
            if is_file_empty(self.step_definition_file_path):
                f.write(f"class {self.step_definition_class_name}:\n\n")
                f.write(f"    def set_up(self):\n        pass\n\n")
                if self.child_type != ChildType.Background:
                    f.write(f"    def tear_down(self):\n        pass\n\n")
                f.close()

    def get_feature_name(self):
        return self.feature_name

    def get_groups(self):
        return self.sequential_groups

    def get_step_definition_class_name(self):
        return self.step_definition_class_name

    def get_step_definition_file_name(self):
        return self.step_definition_file_name
    
    def __add_lead_step(self, lead_step, description, doc_string="", data_table=None, continue_after_failure=False, **kwargs):
        _, location = get_where_the_function_is_called(STACK_FRAME_COUNT)
        sequential_group = SequentialGroup()
        step = Step(lead_step, description, kwargs, doc_string, data_table, continue_after_failure, location=location)
        
        sequential_group.add_step(step)
        self.sequential_groups.append(sequential_group)
        self.__write_function_to_file(step.get_method_name(), kwargs)

    def __add_concurrent_step(self, lead_step, step, description, doc_string="", data_table=None, continue_after_failure=False, **kwargs):
        _, location = get_where_the_function_is_called(STACK_FRAME_COUNT)
        sequential_group = self.sequential_groups[-1]
        lead_step = sequential_group.get_lead_step_type()
        
        step = Step(step, description, kwargs, doc_string, data_table, continue_after_failure, lead_step, location=location)

        sequential_group.add_step(step)
        self.__write_function_to_file(step.get_method_name(), kwargs)

    def __check_continue_after_failure_flag(self, continue_after_failure, lead_step, step=None):
        if lead_step != "Then" and continue_after_failure is True:
            step_having_warning = f"{lead_step}" if step is None else f"{step} in {lead_step} group"
            warnings.warn("\033[33m\n" + f"{step_having_warning} should not set the keyword argument continue_after_failure as True! The keyword argument resets to False." + "\033[0m", stacklevel=2)
            continue_after_failure = False
        return continue_after_failure

    def Given(self, description, doc_string="", data_table=None, continue_after_failure=False, **kwargs):
        if (self.sequential_groups and self.sequential_groups[-1].get_lead_step_type() != "Given"):
            raise ValueError("Given: out of place")

        self.__check_continue_after_failure_flag(continue_after_failure, "Given")
        self.__add_lead_step("Given", description, doc_string, data_table, continue_after_failure, **kwargs)

        return self
   
    def When(self, description, doc_string="", data_table=None, continue_after_failure=False, **kwargs):
        
        self.__check_continue_after_failure_flag(continue_after_failure, "When")
        self.__add_lead_step("When", description, doc_string, data_table, continue_after_failure, **kwargs)

        return self

    def Then(self, description, doc_string="", data_table=None, continue_after_failure=False, **kwargs):

        self.__add_lead_step("Then", description, doc_string, data_table, continue_after_failure, **kwargs)

        return self
    
    def And(self, description, doc_string="", data_table=None, continue_after_failure=False, **kwargs):
        if (not self.sequential_groups):
            raise ValueError("And: must not be the first clause")

        lead_step = self.sequential_groups[-1].get_lead_step_type()
        self.__check_continue_after_failure_flag(continue_after_failure, lead_step, "And")
        self.__add_concurrent_step(lead_step, "And", description, doc_string, data_table, continue_after_failure, **kwargs)
        
        return self

    def But(self, description, doc_string="", data_table=None, continue_after_failure=False, **kwargs):
        if (not self.sequential_groups):
            raise ValueError("But: must not be the first clause")

        lead_step = self.sequential_groups[-1].get_lead_step_type()
        self.__check_continue_after_failure_flag(continue_after_failure, lead_step, "But")
        self.__add_concurrent_step(lead_step, "But", description, doc_string, data_table, continue_after_failure, **kwargs)
        
        return self

    def __write_function_to_file(self, step_method_name, step_kwargs):
        keywords_arguments = ""
        for keyword in step_kwargs:
            keywords_arguments += ", "
            keywords_arguments += keyword 

        newLine = "" 
        if not self.whole_class_text.endswith("\n\n"):
            newLine = "\n" if self.whole_class_text.endswith("\n") else "\n\n"

            with open(self.step_definition_file_path, "a") as f:
                self.whole_class_text += newLine
                f.write(newLine)

        if self.__method_is_not_exist(step_method_name, self.whole_class_text):
            with open(self.step_definition_file_path, "a") as f:
                notImplementedStep = f"{newLine}    def {step_method_name}(self{keywords_arguments}):\n        raise NotImplementedError(\"{step_method_name}\")\n\n"
                self.whole_class_text += notImplementedStep
                f.write(notImplementedStep)
    
    def __method_is_not_exist(self, method_name, whole_class_text):
        while re.search(r"(\s*\"\"\"\s*\n)", whole_class_text):
            multi_line_comments_symbol = re.search(r"(\s*\"\"\"\s*\n)", whole_class_text).group(0)
            part1 = whole_class_text.partition(multi_line_comments_symbol)
            multi_line_comments_symbol = re.search(r"(\s*\"\"\"\s*\n)", part1[2]).group(0)
            part2 = part1[2].partition(multi_line_comments_symbol)
            whole_class_text = part1[0] + part2[2]

        if re.search(fr"^[^#\n]*def\s+{method_name}", whole_class_text, re.MULTILINE):
            return False
        
        return True
    
    def initialize_scenario_context(self):
        import_module_name = self.step_definition_file_name
        steps_module = import_module(import_module_name, self.step_definition_file_path)
        steps_class = getattr(steps_module, self.step_definition_class_name)
        return steps_class()