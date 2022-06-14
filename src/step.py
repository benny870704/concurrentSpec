import re

class Step:
    def __init__(self, step, description, kwargs, leading_step=None):
        self.step = step
        self.description = description
        self.kwargs = kwargs
        self.leading_step = step if leading_step is None else leading_step
        self.function_name = self.__generate_function_name()

    def __generate_function_name(self):
        return re.sub(r'\W+', '_', re.sub(r'\w+', lambda m:m.group(0).lower(), f"{self.leading_step} {self.description}"))
    
    def __repr__(self):
        return f"Step: {self.step}, {self.description}, {self.function_name}, kwargs: {self.kwargs}, leading_step: {self.leading_step}"

    def write_function_to_file(self, step_file, whole_class_text):
        keywords_arguments = ""
        for keyword in self.kwargs:
            keywords_arguments += ", "
            keywords_arguments += keyword 

        with open(step_file, "a") as f:
            if self.function_name not in whole_class_text:
                f.write(f"    def {self.function_name}(self{keywords_arguments}):\n        raise NotImplementedError('{self.function_name}')\n\n")
                f.close()
        
