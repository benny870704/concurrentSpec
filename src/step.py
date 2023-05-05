import re, sys
import textwrap
from .data_table import DataTable
from .status import Status
sys.path.append("../")
from .execute_state import ExecuteState
class Step:
    def __init__(self, step, description, kwargs, doc_string="", data_table=None, continue_after_failure=False, lead_step=None, location=""):
        self.step = step
        self.description = description
        self.kwargs = kwargs
        self.doc_string, self.data_table = self.__check_doc_string_and_data_table(doc_string, data_table)
        self.continue_after_failure = continue_after_failure
        self.lead_step = step if lead_step is None else lead_step
        self.method_name = self.__generate_method_name()
        self.location = location
        self.executed = ExecuteState.NOT_EXECUTED
        self.execution_result = Status.untested
        self.execution_time = None
        self.error_message = ""

    def get_method_name(self):
        return self.method_name

    def get_lead_step(self):
        return self.lead_step
    
    def __generate_method_name(self):
        return re.sub(r'\W+', '_', re.sub(r'\w+', lambda m:m.group(0).lower(), f"{self.lead_step} {self.description}"))
    
    def __repr__(self):
        return f"(step = {self.step}, description = {self.description}, method_name = {self.method_name}, kwargs = {self.kwargs}, lead_step = {self.lead_step})"

    def __check_doc_string_and_data_table(self, doc_string, data_table):
        if data_table is not None:
            data_table = DataTable(data_table)
        elif doc_string != "" and DataTable.is_data_table(doc_string):
            data_table = DataTable(doc_string)
            doc_string = ""
        elif doc_string != "":
            doc_string = textwrap.dedent(doc_string).strip()
        
        return doc_string, data_table

    def write_function_to_file(self, step_file, whole_class_text):
        keywords_arguments = ""
        for keyword in self.kwargs:
            keywords_arguments += ", "
            keywords_arguments += keyword 

        newLine = "" 
        if not whole_class_text.endswith("\n\n"):
            newLine = "\n" if whole_class_text.endswith("\n") else "\n\n"

            with open(step_file, "a") as f:
                whole_class_text += newLine
                f.write(newLine)

        if self.__method_is_not_exist(self.method_name, whole_class_text):
            with open(step_file, "a") as f:
                notImplementedStep = f"{newLine}    def {self.method_name}(self{keywords_arguments}):\n        raise NotImplementedError(\"{self.method_name}\")\n\n"
                whole_class_text += notImplementedStep
                f.write(notImplementedStep)

        return whole_class_text
    
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