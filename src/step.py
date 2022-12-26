import re

class Step:
    def __init__(self, step, description, kwargs, continue_after_failure=False, lead_step=None):
        self.step = step
        self.description = description
        self.kwargs = kwargs
        self.continue_after_failure = continue_after_failure
        self.lead_step = step if lead_step is None else lead_step
        self.method_name = self.__generate_method_name()

    def get_function_name(self):
        return self.method_name

    def __generate_method_name(self):
        return re.sub(r'\W+', '_', re.sub(r'\w+', lambda m:m.group(0).lower(), f"{self.lead_step} {self.description}"))
    
    def __repr__(self):
        return f"{self.step=}, {self.description=}, {self.method_name=}, {self.kwargs=}, {self.lead_step=}"

    def write_function_to_file(self, step_file, whole_class_text):
        keywords_arguments = ""
        for keyword in self.kwargs:
            keywords_arguments += ", "
            keywords_arguments += keyword 

        with open(step_file, "a") as f:
            if self.method_name not in whole_class_text:
                f.write(f"    def {self.method_name}(self{keywords_arguments}):\n        raise NotImplementedError(\"{self.method_name}\")\n\n")
                f.close()
