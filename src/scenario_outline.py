import re
import time
import textwrap
import traceback
from .utils import *
from .status import Status
from .feature import FeatureManager
from .step_container import StepContainer
from .output_interceptor import OutputInterceptor

class ScenarioOutline(StepContainer):
    def __init__(self, scenario_name="", step_definition_folder_path=None, groups=None):
        self.scenario_name = scenario_name
        self.traceback_messages, self.error_messages = "", ""
        self.background_execution_result = None
        self.execution_result = Status.untested
        self.execution_time = None
        self.examples = None
        self.example_execution_result = {}
        self.example_error_log = ""
        super().__init__(scenario_name, step_definition_folder_path, groups)
    
    def get_scenario_name(self):
        return self.scenario_name
    
    def has_examples(self):
        return self.examples != None and self.examples != []

    """
    Given an example:
    | key1 | key2 |
    |  1   |  a   |
    |  2   |  b   |
    translate the example above to [{key1: 1, key2: 'a'}, {key1: 2, key2: 'b'}]
    """
    def WithExamples(self, examples):
        self.examples = []
        self.example_rows = []
    
        examples = re.split(r'\|\s*\n\s*\|\s*', examples)
        examples = [row.strip().split('|') for row in examples]

        for index, row in enumerate(examples[:]):
            examples[index] = [re.sub(r'^[ \t]+|[ \t]+$', '', variable, flags=re.MULTILINE) for variable in row if variable != ""]

        self.example_rows = examples
        keys = examples[0]
        for values in examples[1:]:
            if len(values) == len(keys):
                example = {}
                for key, value in zip(keys, values):
                    example[key] = value
                self.examples.append(example)
            else:
                raise Exception("Cannot parse example correctly.")
        
        return self

    def __add_example_variables_to_step_kwargs(self):
        for sequential_group in self.sequential_groups:
            for step in sequential_group.get_all_steps():
                example_variables = re.findall(r"<(.*?)>", step.description)
                if example_variables:
                    for variable in example_variables:
                        variable_to_keyword = {variable.replace(' ', '_'): None}
                        step.kwargs = {**step.kwargs, **variable_to_keyword}

    def full_text(self, iterate_count = None):
        full_text, indent, indent_count = "", "  ", 0

        if self.feature_name is not None:
            if FeatureManager.get_tags_of_feature(self.feature_name):
                full_text += "".join([f"@{tag} "for tag in FeatureManager.get_tags_of_feature(self.feature_name)])
            full_text += f"\nFeature: {self.feature_name}\n" 
            if FeatureManager.get_feature_description(self.feature_name) != "":
                feature_description = FeatureManager.get_feature_description(self.feature_name)
                full_text += "\n" + textwrap.indent(textwrap.dedent(feature_description).strip(), "  ") + "\n"
            indent_count = 1

            if FeatureManager.get_background(self.feature_name) != None:
                full_text += FeatureManager.get_background(self.feature_name).full_text()

        if FeatureManager.get_tags_of_scenario(self.feature_name, self.scenario_name):
            full_text += "\n" + indent*indent_count + "".join([f"@{tag} "for tag in FeatureManager.get_tags_of_scenario(self.feature_name, self.scenario_name)])
        scenario_name = self.__replace_name_in_angle_brackets_to_example(self.scenario_name, iterate_count) if iterate_count != None else self.scenario_name
        full_text += "\n" + indent*indent_count + "Scenario Outline: " + scenario_name
        full_text += f" - Example #{iterate_count+1}\n" if iterate_count != None else "\n"

        for group in self.sequential_groups:
            for step in group.get_all_steps():
                if self.examples and iterate_count != None:
                    full_text += indent*(indent_count+1) + step.step + " " + self.__replace_name_in_angle_brackets_to_example(step.description, iterate_count) + "\n"
                else:
                    full_text += indent*(indent_count+1) + step.step + " " + step.description + "\n"
                full_text += indent*(indent_count+2) + "\"\"\"\n" + textwrap.indent(step.doc_string, indent*(indent_count+2)) + "\n" + indent*(indent_count+2) + "\"\"\"\n" if step.doc_string != "" else ""
                full_text += step.data_table.get_pretty_string(indent=indent*(indent_count+2)) if step.data_table is not None else ""

        return full_text
    
    def result_printout(self, iterate_count = None, color = True):
        full_text, indent, indent_count = "", "  ", 0

        if self.feature_name is not None:
            if FeatureManager.get_tags_of_feature(self.feature_name):
                full_text += "".join([f"@{tag} "for tag in FeatureManager.get_tags_of_feature(self.feature_name)])
            full_text += f"\n\033[1;34mFeature: {self.feature_name}\033[0m\n" 
            if FeatureManager.get_feature_description(self.feature_name) != "":
                feature_description = FeatureManager.get_feature_description(self.feature_name)
                full_text += "\n" + textwrap.indent(textwrap.dedent(feature_description).strip(), "  ") + "\n"
            indent_count = 1

            if FeatureManager.get_background(self.feature_name) != None:
                full_text += FeatureManager.get_background(self.feature_name).result_printout()

        if FeatureManager.get_tags_of_scenario(self.feature_name, self.scenario_name):
            full_text += "\n" + indent*indent_count + "".join([f"@{tag} "for tag in FeatureManager.get_tags_of_scenario(self.feature_name, self.scenario_name)])
        scenario_name = self.__replace_name_in_angle_brackets_to_example(self.scenario_name, iterate_count) if iterate_count != None else self.scenario_name
        full_text += "\n" + indent*indent_count + "\033[1;34mScenario Outline: " + scenario_name
        full_text += f" - Example #{iterate_count+1}\033[0m\n" if iterate_count != None else "\033[0m\n"

        for group in self.sequential_groups:
            for step in group.get_all_steps():
                if step.execution_result == Status.passed: color = "\033[0;32m"
                elif step.execution_result == Status.failed: color = "\033[0;31m"
                elif step.execution_result == Status.undefined: color = "\033[0;33m"
                else: color = "\033[90m"

                if self.has_examples() and iterate_count != None:
                    full_text += indent*(indent_count+1) + color + step.step + " " + self.__replace_name_in_angle_brackets_to_example(step.description, iterate_count) + "\033[0m\n"
                else:
                    full_text += indent*(indent_count+1) + color + step.step + " " + step.description + "\033[0m\n"
                full_text += indent*(indent_count+2) + "\"\"\"\n" + textwrap.indent(step.doc_string, indent*(indent_count+2)) + "\n" + indent*(indent_count+2) + "\"\"\"\n" if step.doc_string != "" else ""
                full_text += step.data_table.get_pretty_string(indent=indent*(indent_count+2)) if step.data_table is not None else ""
                if step.error_message != "" and step.execution_result != Status.undefined:
                    full_text += textwrap.indent(textwrap.dedent(step.error_message), indent*(indent_count+2))

        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return full_text if color else ansi_escape.sub('', full_text)
    
    def format_output_message(self, message, indent):
        return "".join([f"{indent}{line}\n" for line in message.split('\n')])
    
    def get_output_message(self):
        return self.captured_output if "captured_output" in dir(self) else ""
        
    def format_log_message(self, logs, indent):
        return "".join([f"{indent}{log}\n" for log in logs if log != ""])
    
    def get_log_message(self):
        return self.captured_logs if "captured_logs" in dir(self) else ""

    def execute(self, skip = None):
        if skip is not None:
            return
        if not self.has_examples():
            self.__execute()
        else:
            self.__add_example_variables_to_step_kwargs()
            iterate_count = self.__check_iterate_count()
        
            for i in range(iterate_count):
                self.__update_step_kwargs(i)
                self.__execute(i)
                self.__record_example_execution_result(i)
            self.__record_execution_result()
            # if self.example_error_log != "": raise RuntimeError(self.example_error_log)

    def __execute(self, iterate_count = None):
        runtime_error = None
        start_time = time.time()
        output_interceptor = OutputInterceptor()
        output_interceptor.start(FeatureManager.capture_output, FeatureManager.capture_output, FeatureManager.capture_log)

        try:
            scenario_context = self.initialize_scenario_context()
            self.__execute_background(scenario_context)
            self.__set_up(scenario_context)
            self.__execute_steps(scenario_context)
            self.__tear_down(scenario_context)
        except RuntimeError as e:
            runtime_error = e

        output_interceptor.stop()
        self.execution_time = time.time() - start_time
        
        indent = "    " if self.feature_name else "  "
        self.captured_output = self.format_output_message(output_interceptor.get_captured_output(), indent)
        self.captured_logs = self.format_log_message(output_interceptor.get_captured_logs(), indent)
        if FeatureManager.console_output:
            print("\n" + self.result_printout(iterate_count), end = "")
            if output_interceptor.get_captured_output() != "":
                print("\n    Captured Output:\n" + self.captured_output)
            # if output_interceptor.get_captured_error() != "":
            #     print("\n    Captured Error:\n" + self.format_output_message(output_interceptor.get_captured_error()))
            if output_interceptor.get_captured_logs():
                print("\n    Log Output:\n" + self.captured_logs)
        # if runtime_error is not None and iterate_count is None: raise runtime_error

    def __execute_background(self, scenario_context):
        if self.feature_name != None:
            background = FeatureManager.get_background(self.feature_name)
            if background != None:
                try:
                    background_context = background.execute()
                    scenario_context.__dict__ = {**scenario_context.__dict__, **background_context.__dict__}
                    self.__record_background_result(background)
                except RuntimeError as e:
                    self.execution_result = Status.failed
                    self.traceback_messages += background.traceback_messages
                    self.error_messages += background.error_messages
                    self.__record_background_result(background)
                    raise e
                
    def __record_background_result(self, background):
        self.background_execution_result = {}
        self.background_execution_result["execution_result"] = background.execution_result
        self.background_execution_result["execution_time"] = background.execution_time
        self.background_execution_result["error_messages"] = background.error_messages
        self.background_execution_result["traceback_messages"] = background.traceback_messages
        self.background_execution_result["steps"] = []
        for sequential_group in background.get_groups():
            for step in sequential_group.get_all_steps():
                self.background_execution_result["steps"].append(step)
            
    def __error_handling_from_steps(self, sequential_group, group_errors):
        if group_errors:
            traceback_messages, error_message = "", ""
            continue_after_failure_flag = True
            for traceback_message, exception in group_errors:
                traceback_messages += traceback_message
                error_message += f"    {exception.exc_type.__name__} from step: {exception.thread.name}"
                error_message += f",\n    error message: {exception.exc_value}\n\n" if str(exception.exc_value) != "" else "\n\n"
                
                for step in sequential_group.get_all_steps():
                    if step.description == exception.thread.name and step.continue_after_failure is not True:
                        continue_after_failure_flag = False
            
            self.traceback_messages += traceback_messages
            self.error_messages += error_message

            group_errors.clear()
            self.execution_result = Status.failed

            return continue_after_failure_flag
    
    def __set_up(self, scenario_context):
        traceback_message = ""
        if getattr(scenario_context, 'set_up', False):
            try:
                scenario_context.set_up()
            except Exception as e:
                error_message = f"    {type(e).__name__} from set_up\n\n"
                traceback_message += traceback.format_exc() + "\n"
                self.traceback_messages += traceback_message
                self.error_messages += error_message
    
    def __tear_down(self, scenario_context):
        traceback_message = ""
        if getattr(scenario_context, 'tear_down', False):
            try:
                scenario_context.tear_down()
            except Exception as e:
                self.execution_result = Status.failed
                error_message = f"    {type(e).__name__} from tear_down\n\n"
                traceback_message += traceback.format_exc() + "\n"
                self.traceback_messages += traceback_message
                self.error_messages += error_message
        
        if self.traceback_messages != "": raise RuntimeError(self.error_log())
        self.execution_result = Status.passed

    def __inject_doc_string_and_data_table_to_context(self, scenario_context, concurrent_steps):
        doc_strings, data_tables = {}, {}
        for step in concurrent_steps:
            if step.doc_string != "":
                doc_strings.update({step.method_name: step.doc_string})
            if step.data_table is not None:
                data_tables.update({step.method_name: step.data_table.to_list_of_dict()})
        scenario_context.__dict__.update({"text": doc_strings})
        scenario_context.__dict__.update({"table": data_tables})
        scenario_context.__dict__.update({"get_table": get_table})
        scenario_context.__dict__.update({"get_text": get_text})
        return scenario_context
    
    def __remove_doc_string_and_data_table_from_context(self, scenario_context):
        if "text" in scenario_context.__dict__: scenario_context.__dict__.pop("text")
        if "table" in scenario_context.__dict__: scenario_context.__dict__.pop("table")
        return scenario_context

    def __execute_steps(self, scenario_context):
        if self.traceback_messages == "" and self.error_messages == "":
            for sequential_group in self.sequential_groups:
                scenario_context = self.__inject_doc_string_and_data_table_to_context(scenario_context, sequential_group.get_all_steps())
                group_errors = sequential_group.run_all_steps(scenario_context)
                scenario_context = self.__remove_doc_string_and_data_table_from_context(scenario_context)

                continue_after_failure_flag = self.__error_handling_from_steps(sequential_group, group_errors)
                
                if continue_after_failure_flag is False:
                    self.__tear_down(scenario_context)

    def __check_iterate_count(self):
        if self.has_examples():
            iterate_count = len(self.examples)
            variable_count = len(self.examples[0])
            for example in self.examples[1:]:
                if len(example) != variable_count: raise Exception("Invalid examples count")

            return iterate_count

    def __update_step_kwargs(self, example_index):
        snake_case_key_to_origin_key = {}
        snake_case_keys = [key.replace(' ', '_') for key in self.examples[example_index].keys()]
        for key in self.examples[example_index].keys():
            snake_case_key_to_origin_key.update({key.replace(' ', '_'): key})

        for sequential_group in self.sequential_groups:
            for step in sequential_group.get_all_steps():
                for step_key in step.kwargs.keys():
                    if step_key in snake_case_keys:
                        step.kwargs[step_key] = self.examples[example_index][snake_case_key_to_origin_key[step_key]]

    def __record_example_execution_result(self, iterate_count):
        self.example_execution_result[iterate_count] = {}
        self.example_execution_result[iterate_count]["background"] = self.background_execution_result
        self.example_execution_result[iterate_count]["execution_result"] = self.execution_result
        self.example_execution_result[iterate_count]["execution_time"] = self.execution_time
        self.example_execution_result[iterate_count]["error_messages"] = self.error_messages
        self.example_execution_result[iterate_count]["traceback_messages"] = self.traceback_messages
        self.example_execution_result[iterate_count]["steps"] = []
        for sequential_group in self.sequential_groups:
            for step in sequential_group.get_all_steps():
                self.example_execution_result[iterate_count]["steps"].append(step)

        if self.traceback_messages != "":
            error_log = "\n\033[1;7m " + self.scenario_name + f" - Example #{iterate_count + 1} \033[0m\n" + self.error_log()
            self.example_error_log += error_log

        self.execution_result = Status.untested
        self.execution_time = None
        self.error_messages = ""
        self.traceback_messages = ""

    def __record_execution_result(self):
        self.execution_time = 0
        for _, result in self.example_execution_result.items():
            if result["execution_result"] != Status.passed: self.execution_result = Status.failed
            self.execution_time += result["execution_time"]
        if self.execution_result != Status.failed: self.execution_result = Status.passed

    def __replace_name_in_angle_brackets_to_example(self, step_description, iterate_count):
        example_variables = re.findall(r"<(.*?)>", step_description)
        if example_variables:
            for variable in example_variables:
                example = self.examples[iterate_count][variable].replace('\n', '\\n')
                step_description = step_description.replace(f"<{variable}>", "\033[1m"+example+"\033[22m")
        return step_description
    
    def error_log(self):
        return "\n\n" + self.traceback_messages + "\n\033[1;31mError(s) in the group:\n\n\033[0;31m" + self.error_messages + "\033[0m" if self.traceback_messages != "" else ""
        