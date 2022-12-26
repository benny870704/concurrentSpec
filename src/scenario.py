import re
import os, sys
import threading
import traceback
import importlib
import importlib.util
from pathlib import Path
from .sequential_group import SequentialGroup
from .step import Step
import warnings

def is_file_empty(file_name):
    return os.path.isfile(file_name) and os.path.getsize(file_name) == 0

class Scenario:
    def __init__(self, name="scenario", step_path="./steps/", groups=None):
        self.name = name
        self.sequential_groups = [] if groups == None else groups
        self.step_path = step_path if step_path.endswith("/") else step_path+"/"
        self.step_class_name = self.__generate_step_class_name()
        self.step_file_name = self.__generate_step_file_name()

        self.step_file = f"{self.step_path}{self.step_file_name}.py"

        os.makedirs(f"{self.step_path}", exist_ok = True) 
        
        with open(self.step_file, "a") as f:
            if is_file_empty(self.step_file):
                f.write(f"class {self.step_class_name}:\n\n")
                f.write(f"    def __init__(self):\n        pass\n\n")
                f.close()
        self.whole_class_text = Path(self.step_file).read_text()

    def get_groups(self):
        return self.sequential_groups

    def get_step_class_name(self):
        return self.step_class_name

    def get_step_file_name(self):
        return self.step_file_name

    def __generate_step_class_name(self):
        return re.sub(r'\W+', '', re.sub(r'\w+', lambda m:m.group(0).capitalize(), f"{self.name}"))

    def __generate_step_file_name(self):
        return re.sub(r'\W+', '_', re.sub(r'\w+', lambda m:m.group(0).lower(), f"{self.name}"))
    
    def Given(self, description, continue_after_failure=False, **kwargs):
        if (self.sequential_groups and self.sequential_groups[-1].get_all_steps()[0].step != "Given"):
            raise ValueError("Given: out of place")

        if continue_after_failure is True:
            warnings.warn("\033[33m\nGiven should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", stacklevel=2)
            continue_after_failure = False

        sequential_group = SequentialGroup()
        step = Step("Given", description, kwargs, continue_after_failure)
        
        step.write_function_to_file(self.step_file, self.whole_class_text)
        
        sequential_group.add_step(step)
        self.sequential_groups.append(sequential_group)

        return self
   
    def When(self, description, continue_after_failure=False, **kwargs):
        
        if continue_after_failure is True:
            warnings.warn("\033[33m\nWhen should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", stacklevel=2)
            continue_after_failure = False

        sequential_group = SequentialGroup()
        step = Step("When", description, kwargs, continue_after_failure)

        step.write_function_to_file(self.step_file, self.whole_class_text)
        sequential_group.add_step(step)
        self.sequential_groups.append(sequential_group)

        return self

    def Then(self, description, continue_after_failure=False, **kwargs):

        sequential_group = SequentialGroup()
        step = Step("Then", description, kwargs, continue_after_failure)
        
        step.write_function_to_file(self.step_file, self.whole_class_text)
        sequential_group.add_step(step)
        self.sequential_groups.append(sequential_group)

        return self
    
    def And(self, description, continue_after_failure=False, **kwargs):
        if (not self.sequential_groups):
            raise ValueError("And: must not be the first clause")

        lead_step=self.sequential_groups[-1].get_all_steps()[0].step
        if lead_step != "Then" and continue_after_failure is True:
            warnings.warn(f"\033[33m\n{lead_step} should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", stacklevel=2)
            continue_after_failure = False
        
        sequential_group = self.sequential_groups[-1]
        step = Step("And", description, kwargs, continue_after_failure, lead_step)
        
        step.write_function_to_file(self.step_file, self.whole_class_text)
        sequential_group.add_step(step)
        
        return self

    def But(self, description, continue_after_failure=False, **kwargs):
        if (not self.sequential_groups):
            raise ValueError("But: must not be the first clause")

        lead_step=self.sequential_groups[-1].get_all_steps()[0].step
        if lead_step != "Then" and continue_after_failure is True:
            warnings.warn(f"\033[33m\n{lead_step} should not set the keyword argument continue_after_failure as True! The keyword argument resets to False.\033[0m", stacklevel=2)
            continue_after_failure = False
        
        sequential_group = self.sequential_groups[-1]
        step = Step("But", description, kwargs, continue_after_failure, lead_step)
        
        step.write_function_to_file(self.step_file, self.whole_class_text)
        sequential_group.add_step(step)
        
        return self

    def full_text(self):
        full_text = "\n\033[1;34mScenario: " + self.name + "\033[0m\n"
        for group in self.sequential_groups:
            for step in group.get_all_steps():
                full_text += "\033[0;34m  " + step.step + "\033[0m " + step.description + "\n"
        print(full_text, end = "")

    def execute(self):
        print()
        self.full_text()
        print()
        
        step_definition_instance = self.create_step_definition_instance()
        
        error_log = ""
        for sequential_group in self.sequential_groups:

            group_errors = sequential_group.run_all_steps(step_definition_instance)
            
            if group_errors:
                traceback_message = ""
                error_message = ""
                continue_after_failure_flag = True
                for traceback, exception in group_errors:
                    traceback_message += traceback
                    if str(exception.exc_value) != "":
                        error_message += f"    {exception.exc_type.__name__} from step: {exception.thread.name},\n\
    error message: {exception.exc_value}\n\n"
                    else:
                        error_message += f"    {exception.exc_type.__name__} from step: {exception.thread.name}\n\n\n"
                    for step in sequential_group.get_all_steps():
                        if step.description == exception.thread.name and step.continue_after_failure is not True:
                            continue_after_failure_flag = False
                
                error_log += traceback_message + "\n\033[1;31mError(s) in the group:\n\n\033[0;31m" + error_message + "\033[0m"

                group_errors.clear()

                if not continue_after_failure_flag:
                    raise RuntimeError(error_log)

        if error_log != "":
            raise RuntimeError(error_log)

    def create_step_definition_instance(self):
        import_path = str.replace(str.replace(self.step_path, "./", ""), "/", ".")
        import_module_name = f"{import_path}{self.step_file_name}"
        if import_module_name in sys.modules:
            del sys.modules[import_module_name]
        steps_module = importlib.import_module(import_module_name)
        steps_class = getattr(steps_module, self.step_class_name)
        return steps_class()
