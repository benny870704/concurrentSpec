import io, re
import time
import logging
import textwrap
import traceback
from .utils import *
from .status import Status
from .feature import FeatureManager
from .step_container import StepContainer

class Scenario(StepContainer):
    def __init__(self, scenario_name="", step_definition_folder_path=None, groups=None):
        self.scenario_name = scenario_name
        self.traceback_messages, self.error_messages = "", ""
        self.background_execution_result = {}
        self.execution_result = Status.untested
        self.execution_time = None
        super().__init__(scenario_name, step_definition_folder_path, groups)

    def get_scenario_name(self):
        return self.scenario_name
    
    def result_printout(self, color=True):
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
        full_text += "\n" + indent*indent_count + "\033[1;34mScenario: " + self.scenario_name + "\033[0m\n"

        for group in self.sequential_groups:
            for step in group.get_all_steps():
                if step.execution_result == Status.passed: color = "\033[0;32m"
                elif step.execution_result == Status.failed: color = "\033[0;31m"
                elif step.execution_result == Status.undefined: color = "\033[0;33m"
                else: color = "\033[0m"
                full_text += indent*(indent_count+1) + color + step.step + " " + step.description + "\033[0m\n"
                full_text += indent*(indent_count+2) + "\"\"\"\n" + textwrap.indent(step.doc_string, indent*(indent_count+2)) + "\n" + indent*(indent_count+2) + "\"\"\"\n" if step.doc_string != "" else ""
                full_text += step.data_table.get_pretty_string(indent=indent*(indent_count+2)) if step.data_table is not None else ""

        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return full_text if color else ansi_escape.sub('', full_text)
    
    def captured_output_message(self):
        if "captured_output" in dir(self):
            return "".join([f"    {line}\n" for line in self.captured_output.getvalue().split('\n')])
        
    def captured_log_message(self):
        if "log_handler" in dir(self):
            return "".join([f"    {log}\n" for log in self.log_handler.logs if log != ""])

    def execute(self):
        runtime_error = None
        start_time = time.time()
        self.captured_output = io.StringIO()
        captured_error = io.StringIO()
        sys.stdout = self.captured_output
        sys.stderr = captured_error
        self.log_handler = self.__intercept_log_from_root_logger()

        try:
            scenario_context = self.initialize_scenario_context()
            self.__execute_background(scenario_context)
            self.__set_up(scenario_context)
            self.__execute_steps(scenario_context)
            self.__tear_down(scenario_context)
        except RuntimeError as e:
            runtime_error = e

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.__stop_intercept_log()
        self.execution_time = time.time() - start_time
        if FeatureManager.console_output:
            print("\n" + self.result_printout(), end = "")
            if self.captured_output.getvalue() != "":
                print("\n    Captured Output:\n" + self.captured_output_message())
            if self.log_handler.logs:
                print("\n    Log Output:\n" + self.captured_log_message())
        if runtime_error is not None: raise runtime_error

    def __intercept_log_from_root_logger(self):
        class CustomLogHandler(logging.Handler):
            def __init__(self):
                logging.Handler.__init__(self)
                self.logs = []

            def emit(self, record):
                msg = self.format(record)
                self.logs.append(msg)

        # Remove the default StreamHandler from the root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)

        # Create a custom log handler and add it to the root logger
        custom_handler = CustomLogHandler()
        logging.getLogger().addHandler(custom_handler)
        return custom_handler
    
    def __stop_intercept_log(self):
        logging.getLogger().addHandler(logging.StreamHandler())

    def __execute_background(self, scenario_context):
        if self.feature_name != None:
            background = FeatureManager.get_background(self.feature_name)
            if background != None:
                try:
                    background_context = background.execute()
                    self.__record_background_result(background)
                    scenario_context.__dict__ = {**scenario_context.__dict__, **background_context.__dict__}
                except RuntimeError as e:
                    self.__record_background_result(background)
                    self.execution_result = Status.failed
                    self.traceback_messages += background.traceback_messages
                    self.error_messages += background.error_messages
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
        doc_string_count, data_table_count = 0, 0
        for step in concurrent_steps:
            if step.doc_string != "": doc_string_count += 1
            if step.data_table is not None: data_table_count += 1
        if doc_string_count > 1 or data_table_count > 1: raise Exception("Do not support multiple doc string or data table in concurrent steps.")

        for step in concurrent_steps:
            if step.doc_string != "":
                scenario_context.__dict__.update({"text": step.doc_string})
            if step.data_table is not None:
                scenario_context.__dict__.update({"table": step.data_table.to_list_of_dict()})
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
    
    def error_log(self):
        return "\n\n" + self.traceback_messages + "\n\033[1;31mError(s) in the group:\n\n\033[0;31m" + self.error_messages + "\033[0m" if self.traceback_messages != "" else ""
