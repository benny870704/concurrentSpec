import time
import textwrap
import traceback
from .utils import *
from .status import Status
from .step_container import StepContainer

class Background(StepContainer):
    def __init__(self, background_name="", step_definition_folder_path=None, groups=None):
        self.background_name = background_name
        self.traceback_messages, self.error_messages = "", ""
        self.set_up_error = ""
        self.execution_result = Status.untested
        self.execution_time = None
        super().__init__(background_name, step_definition_folder_path, groups)

    def get_background_name(self):
        return self.background_name
    
    def full_text(self):
        full_text, indent = "", "  "

        full_text += "\n" + indent + "Background: " + self.background_name + "\n"

        for group in self.sequential_groups:
            for step in group.get_all_steps():
                full_text += indent*2 + step.step + " " + step.description + "\n"
                full_text += indent*3 + "\"\"\"\n" + step.doc_string + "\n" + indent*3 + "\"\"\"\n" if step.doc_string != "" else ""
                full_text += step.data_table.get_pretty_string(indent=indent*3) if step.data_table is not None else ""
        return full_text
    
    def result_printout(self):
        full_text, indent = "", "  "

        if self.set_up_error != "": full_text += "\n" + indent + self.set_up_error
        full_text += "\n" + indent + "\033[1;34mBackground: " + self.background_name + "\033[0m\n"

        for group in self.sequential_groups:
            for step in group.get_all_steps():
                if step.execution_result == Status.passed: color = "\033[0;32m"
                elif step.execution_result == Status.failed: color = "\033[0;31m"
                elif step.execution_result == Status.undefined: color = "\033[0;33m"
                else: color = "\033[90m"
                full_text += indent*2 + color + step.step + " " + step.description + "\033[0m\n"
                full_text += indent*3 + "\"\"\"\n" + step.doc_string + "\n" + indent*3 + "\"\"\"\n" if step.doc_string != "" else ""
                full_text += step.data_table.get_pretty_string(indent=indent*3) if step.data_table is not None else ""
                if step.error_message != "": full_text += textwrap.indent(textwrap.dedent(step.error_message), indent*3)

        return full_text

    def execute(self):
        self.reset()
        start_time = time.time()

        try:
            background_context = self.initialize_scenario_context()
            self.__set_up(background_context)
            self.__execute_steps(background_context)
            self.execution_time = time.time() - start_time
        except RuntimeError as e:
            self.execution_time = time.time() - start_time
            raise e

        return background_context
    
    def __execute_steps(self, background_context):
        if self.traceback_messages == "" and self.error_messages == "":
            for sequential_group in self.sequential_groups:
                group_errors = sequential_group.run_all_steps(background_context)

                continue_after_failure_flag = self.__error_handling_from_steps(sequential_group, group_errors)
                
                if continue_after_failure_flag is False:
                    raise RuntimeError(self.error_log())
            self.execution_result = Status.passed
    
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
    
    def __set_up(self, background_context):
        traceback_message = ""
        if getattr(background_context, 'set_up', False):
            try:
                background_context.set_up()
            except Exception as e:
                error_message = f"    {type(e).__name__} from set_up\n"
                self.set_up_error = f"\033[0;31mHOOK-ERROR in Background set_up: {type(e).__name__}: {e}\033[0m\n"
                traceback_message += traceback.format_exc() + "\n"
                self.traceback_messages += traceback_message
                self.error_messages += error_message
                self.execution_result = Status.failed
                raise RuntimeError(e)
            
    def reset(self):
        self.execution_result = Status.untested
        self.execution_time = None
        self.traceback_messages = ""
        self.error_messages = ""
        self.set_up_error = ""
    
    def error_log(self):
        return "\n\n" + self.traceback_messages + "\n\033[1;31mError(s) in the group:\n\n\033[0;31m" + self.error_messages + "\033[0m" if self.traceback_messages != "" else ""
    