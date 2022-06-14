import re
import os, sys
import threading
import traceback
import importlib
import importlib.util
from threading import Thread
from pathlib import Path
from .step import Step

GLOBAL_ERROR = []

def __excepthook__(args):
    traceback.print_exc()
    global GLOBAL_ERROR
    GLOBAL_ERROR.append(args)

threading.excepthook = __excepthook__

def is_file_empty(file_name):
    return os.path.isfile(file_name) and os.path.getsize(file_name) == 0

class Scenario:
    def __init__(self, name="scenario", groups=None, step_path="./steps/"):
        self.name = name
        self.groups = [] if groups == None else groups
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

    def __generate_step_class_name(self):
        return re.sub(r'\W+', '', re.sub(r'\w+', lambda m:m.group(0).capitalize(), f"{self.name} Steps"))

    def __generate_step_file_name(self):
        return re.sub(r'\W+', '_', re.sub(r'\w+', lambda m:m.group(0).lower(), f"{self.name}_steps"))
    
    def Given(self, description, **kwargs):
        if (self.groups and self.groups[-1][0].step != "Given"):
            raise ValueError("Given: out of place")

        step = Step("Given", description, kwargs)
        
        step.write_function_to_file(self.step_file, self.whole_class_text)
        self.groups.append([step])

        return self
   
    def When(self, description, **kwargs):
        
        step = Step("When", description, kwargs)

        step.write_function_to_file(self.step_file, self.whole_class_text)
        self.groups.append([step])

        return self

    def Then(self, description, **kwargs):
        
        step = Step("Then", description, kwargs)
        
        step.write_function_to_file(self.step_file, self.whole_class_text)
        self.groups.append([step])

        return self
    
    def And(self, description, **kwargs):
        if (not self.groups):
            raise ValueError("And: must not be the first clause")

        step = Step("And", description, kwargs, leading_step=self.groups[-1][0].step)
        
        step.write_function_to_file(self.step_file, self.whole_class_text)
        self.groups[-1].append(step)
        
        return self

    def But(self, description, **kwargs):
        if (not self.groups):
            raise ValueError("But: must not be the first clause")

        step = Step("But", description, kwargs, leading_step=self.groups[-1][0].step)
        
        step.write_function_to_file(self.step_file, self.whole_class_text)
        self.groups[-1].append(step)
        
        return self

    # def full_text(self):
    #     full_text = "Scenario: " + self.name + "\n"
    #     for text, description in self.groups:
    #         full_text += "  " + text + " " + description + "\n"

    #     return full_text

    def execute(self):
        import_path = str.replace(str.replace(self.step_path, "./", ""), "/", ".")
        import_module_name = f"{import_path}{self.step_file_name}"
        if import_module_name in sys.modules:
            del sys.modules[import_module_name]
        steps_module = importlib.import_module(import_module_name)
        steps_class = getattr(steps_module, self.step_class_name)
        self.steps_object = steps_class()

        print("") # make a line break
        for group in self.groups:
            thread_list = [Thread(target=getattr(self.steps_object, step.function_name), name=step.description, kwargs=step.kwargs) for step in group]
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
            
            global GLOBAL_ERROR
            if GLOBAL_ERROR:
                error_message = ""
                for exception in GLOBAL_ERROR:
                    error_message += f"    {exception.exc_type.__name__} from step: {exception.thread.getName()},\n\
    error message: {exception.exc_value}\n\n"
                GLOBAL_ERROR.clear()
                raise RuntimeError("Error(s) in the group:\n\n" + error_message)
            print("---------------------------------")
            