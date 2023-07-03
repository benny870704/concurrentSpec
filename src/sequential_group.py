import time, threading, traceback, inspect
from .status import Status
from .execute_state import ExecuteState

GLOBAL_ERROR = []

def __excepthook__(args):
    traceback_message = traceback.format_exc() + "\n"

    global GLOBAL_ERROR
    GLOBAL_ERROR.append((traceback_message, args))

threading.excepthook = __excepthook__

class SequentialGroup:
    def __init__(self):
        self.concurrent_steps = []
        self.step_to_domain_name_and_scenario_name = {}
        self.execution_result = Status.untested

    def __repr__(self):
        return f"SequentialGroup {self.concurrent_steps}"

    def add_step(self, step, domain_name = None, scenario_name = None):
        self.concurrent_steps.append(step)
        if domain_name is not None:
            self.step_to_domain_name_and_scenario_name[step] = (domain_name, scenario_name)
            
    def get_all_steps(self):
        return self.concurrent_steps
    
    def get_lead_step_type(self):
        return self.concurrent_steps[0].step
    
    def get_step_to_domain_name_and_scenario_name(self):
        return self.step_to_domain_name_and_scenario_name
    
    def run_all_steps(self, scenario_context):
        global GLOBAL_ERROR

        thread_list = []
        if isinstance(scenario_context, dict):
            for step, domain_name_and_scenario_name in self.step_to_domain_name_and_scenario_name.items():
                if step.executed != ExecuteState.SKIP:
                    step_method = getattr(scenario_context[domain_name_and_scenario_name], step.method_name)
                    params = inspect.signature(step_method).parameters
                    self.__transfer_params_type_in_kwargs(params, step.kwargs)
                    thread_list.append(threading.Thread(target=step_method, name=step.description, kwargs=step.kwargs))
                    step.execution_time = time.time()
        else:
            for step in self.concurrent_steps:
                if step.executed != ExecuteState.SKIP:
                    step_method = getattr(scenario_context, step.method_name)
                    params = inspect.signature(step_method).parameters
                    self.__transfer_params_type_in_kwargs(params, step.kwargs)
                    thread_list.append(threading.Thread(target=step_method, name=step.description, kwargs=step.kwargs))
                    step.execution_time = time.time()
        
        for t in thread_list:
            t.start()

        while thread_list:
            for t in thread_list[:]:
                if not t.is_alive():
                    t.join()
                    thread_list.remove(t)
                    self.__record_step_execution_result(t.name)

        if self.execution_result != Status.failed: self.execution_result = Status.passed

        return GLOBAL_ERROR
    
    def __transfer_params_type_in_kwargs(self, expected_params, kwargs):
        for key in kwargs.keys():
            if key in expected_params.keys():
                type = expected_params.get(key).annotation
                if type == int: kwargs[key] = int(kwargs[key])
                elif type == float: kwargs[key] = float(kwargs[key])
        
    def __record_step_execution_result(self, step_description):
        step_description_to_exception = {}
        step_description_to_exception_type = {}
        if GLOBAL_ERROR:
            exception_messages = list(zip(*GLOBAL_ERROR))[0]
            exceptions = list(zip(*GLOBAL_ERROR))[1]
            for index, e in enumerate(exceptions):
                step_description_to_exception.update({e.thread.name: exception_messages[index]})
                step_description_to_exception_type.update({e.thread.name: e.exc_type.__name__})
        
        for step in self.concurrent_steps:
            if step.description == step_description:
                step.execution_time = time.time() - step.execution_time
                if step_description in step_description_to_exception_type.keys():
                    step.execution_result = Status.undefined if step_description_to_exception_type[step_description] == "NotImplementedError" else Status.failed
                    step.error_message = step_description_to_exception[step_description]
                    self.execution_result = Status.failed
                else:
                    step.execution_result = Status.passed