import re
import os
import threading
import traceback
import importlib
from threading import Thread
from pathlib import Path

global_error = []

def __excepthook__(args):
    traceback.print_exc()
    global global_error
    global_error.append(args)

threading.excepthook = __excepthook__

def _generate_camel_case(string: str):
    return re.sub(r'\W+', '', re.sub(r'\w+', lambda m:m.group(0).capitalize(), string))

def _generate_lower_case_with_underscores(string: str):
    return re.sub(r'\W+', '_', re.sub(r'\w+', lambda m:m.group(0).lower(), string))

def is_file_empty(file_name):
    return os.path.isfile(file_name) and os.path.getsize(file_name) == 0

class Scenario:
    def __init__(self, name="scenario", groups=None):
        self.name = name
        self.groups = [] if groups == None else groups
        self.step_class_name = _generate_camel_case(f"{name} Steps")
        self.step_file_name = _generate_lower_case_with_underscores(f"{name}_steps")

        self.step_file = f"{self.step_file_name}.py"
        
        with open(self.step_file, "a") as f:
            if is_file_empty(self.step_file):
                f.write(f"class {self.step_class_name}:\n\n")
                f.write(f"    def __init__(self):\n        pass\n\n")
                f.close()
        self.whole_class_text = Path(self.step_file).read_text()

    
    def Given(self, description="", args=[]):
        if (self.groups and self.groups[-1][0][0] != "Given"):
            raise ValueError("Given: out of place")

        function_name = _generate_lower_case_with_underscores(f"given {description}")
        
        with open(self.step_file, "a") as f:
            if function_name not in self.whole_class_text:
                f.write(f"    def {function_name}(self):\n        raise NotImplementedError('{function_name}')\n\n")
                f.close()

        self.groups.append([["Given", description, function_name, args]])

        return self

    def And(self, description="", args=[]):
        if (not self.groups):
            raise ValueError("And: must not be the first clause")

        function_name = _generate_lower_case_with_underscores(f"{self.groups[-1][0][0]} {description}")

        with open(self.step_file, "a") as f:
            if function_name not in self.whole_class_text:
                f.write(f"    def {function_name}(self):\n        raise NotImplementedError('{function_name}')\n\n")
                f.close()
                
        self.groups[-1].append(["And", description, function_name, args])

        return self
    
    def When(self, description="", args=[]):
        
        function_name = _generate_lower_case_with_underscores(f"when {description}")
        
        with open(self.step_file, "a") as f:
            if function_name not in self.whole_class_text:
                f.write(f"    def {function_name}(self):\n        raise NotImplementedError('{function_name}')\n\n")
                f.close()
 
        self.groups.append([["When", description, function_name, args]])

        return self

    def Then(self, description="", args=[]):
        
        function_name = _generate_lower_case_with_underscores(f"then {description}")
        
        with open(self.step_file, "a") as f:
            if function_name not in self.whole_class_text:
                f.write(f"    def {function_name}(self):\n        raise NotImplementedError('{function_name}')\n\n")
                f.close()

        self.groups.append([["Then", description, function_name, args]])

        return self

    def full_text(self):
        full_text = "Scenario: " + self.name + "\n"
        for text, description in self.groups:
            full_text += "  " + text + " " + description + "\n"

        return full_text

    def execute(self):
        steps_module = importlib.import_module(self.step_file_name)
        steps_class = getattr(steps_module, self.step_class_name)
        self.steps_object = steps_class()

        for group in self.groups:
            thread_list = [Thread(target=getattr(self.steps_object, step[2]), name=step[1], args=step[3]) for step in group]
            self.all_done = False
            for t in thread_list:
                print(t.name + " start")
                t.start()
                
            while thread_list:
                for t in thread_list[:]:
                    if not t.is_alive():
                        t.join()
                        print(t.name + " end")
                        thread_list.remove(t)
            global global_error
            if global_error:
                error_message = ""
                for exception in global_error:
                    error_message += f"    {exception.exc_type.__name__} from step: {exception.thread.getName()}, \n\
    error message: {exception.exc_value}\n\n"
                raise RuntimeError("Error(s) in the group:\n\n" + error_message)
            print("---------------------------------")            
            