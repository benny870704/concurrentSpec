import re, traceback, threading
import shutil
from pathlib import Path
from anytree import PreOrderIter, Node
from concurrentSpec.src.feature import FeatureManager
from .system_scenario import SystemScenario
from .scenario import Scenario
from .execute_state import ExecuteState

class SystemScenarioOutline(SystemScenario):
    def __init__(self, system_scenario_name: str):
        FeatureManager.clear()
        FeatureManager.console_output = False
        self.error_log = ""
        self.system_scenario_name: str = system_scenario_name
        self.project_path: str = None
        self.system_scenario: Scenario = None
        self.system_context = None
        self.domain_name_and_scenario_name_tuple_to_selected_scenario: dict = {}
        self.step_order_tree_root = Node(name = "root")
        self.then_given_matching_groups = []
        self.then_when_matching_groups = []
        if "test_system_scenario" not in str(Path(traceback.extract_stack()[-2].filename)):
            self.add_project_path(str(Path(traceback.extract_stack()[-2].filename).parent.parent) + "/")
        
    def select_scenario_outline(self, domain_name: str, scenario_name: str):
        super().select_scenario(domain_name, scenario_name)
        
        return self
    
    def WithExamples(self, examples):
        self.examples = []           
        #* [{'x': '0.00', 'y': '0.00', 'z': '1.00'}, 
        #*  {'x': '0.00', 'y': '0.53', 'z': '0.92'},
        #*  {'x': '0.18', 'y': '1.06', 'z': '0.61'}]
        self.example_rows = [] 
        #* [['x',    'y',    'z'   ]\
        #*  ['0.00', '0.00', '1.00'],
        #*  ['0.00', '0.53', '0.92'],
        #*  ['0.18', '1.06', '0.61']]
    
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
    
    def __print_selected_step(self, iterate_count):
        terminal_width, _ = shutil.get_terminal_size()
        separator = '-' * (terminal_width - 1)
        print(separator)
        print(f"\n\033[1;40m System Scenario Outline #{iterate_count + 1}: {self.system_scenario_name}\033[0m")
        
        for step_node in PreOrderIter(self.step_order_tree_root):
            if hasattr(step_node, "step"):
                step = step_node.step
            else:
                continue
            print(f"\033[0;34m  " + step.step + "\033[0m " + self.__replace_name_in_angle_brackets_to_example(step, iterate_count))
            super()._print_data_table_and_doc_string_if_contain(step, "        ")
        print()
    
    def __replace_name_in_angle_brackets_to_example(self, step, iterate_count):
        step_description = step.description
        example_variables = re.findall(r"<(.*?)>", step_description)
        if example_variables:
            for variable in example_variables:
                example = self.examples[iterate_count].get(variable)
                if example is not None:
                    example.replace('\n', '\\n')
                    step_description = step_description.replace(f"<{variable}>", "\033[1m"+example+"\033[22m")
                else:
                    step.executed = ExecuteState.SKIP
        return step_description
    
    def execute(self):
        super()._create_scenario_in_system_domain()  
        iterate_count = self.__check_iterate_count()
        self.__add_example_variables_to_step_kwargs()
 
        for i in range(iterate_count):
            self.__print_selected_step(i)
            super()._set_up()
            self.__compare_and_execute_step(i)
            super()._tear_down()
            self.__print_execution_result(i)
            self.__refresh_executed_flag()

            if self.error_log != "": 
                print(self.error_log)
                self.error_log = ""
    
    def __refresh_executed_flag(self):
        for selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.values():
            for step in selected_scenario.get_steps():
                step.executed = ExecuteState.NOT_EXECUTED
        
        for step_node in PreOrderIter(self.step_order_tree_root):
            if hasattr(step_node, "step"):
                step_node.step.executed = ExecuteState.NOT_EXECUTED
    
    def __compare_and_execute_step(self, example_index):
        sequential_groups = []
        
        for step_node in PreOrderIter(self.step_order_tree_root):
            if hasattr(step_node, "step"):
                high_level_step_keyword = step_node.name
                step = step_node.step
            else:
                continue
            
            if step_node.name == "When":
                super()._bind_domain_environment_to_system_environment()
                self.__execute_all_internal_given_step(example_index)
                if self.error_log != "":
                    return
            
            super()._compare_step_with_selected_scenario(sequential_groups, step, high_level_step_keyword)
            self.__update_step_kwargs(example_index, sequential_groups)
            super()._bind_domain_environment_to_system_environment()
            
            if step_node.children == ():
                self.__execute_sequential_groups_in_outlinie(sequential_groups)
                sequential_groups = []
                if self.error_log != "":
                    return
    
    def __execute_all_internal_given_step(self, example_index):
        domain_occur_history = []
        domain_name_and_scenario_name_tuple_to_given_sequential_groups = {}
        thread_list = []
        for domain_name_and_scenario_name_tuple, selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.items():
            domain_name = domain_name_and_scenario_name_tuple[0]
            if domain_name in domain_occur_history:
                continue
            else:
                domain_occur_history.append(domain_name)
                given_sequential_groups = selected_scenario.get_all_given_sequential_groups()
                self.__update_step_kwargs(example_index, given_sequential_groups)
                domain_name_and_scenario_name_tuple_to_given_sequential_groups[domain_name_and_scenario_name_tuple] = given_sequential_groups
                
        all_scenario_context = self._get_all_scenario_context()
        
        for domain_name_and_scenario_name_tuple, given_sequential_groups in domain_name_and_scenario_name_tuple_to_given_sequential_groups.items():
            scenario_context = all_scenario_context.get(domain_name_and_scenario_name_tuple)
            
            thread_list.append(threading.Thread(target = self.__execute_sequential_groups_in_outlinie, args = (given_sequential_groups, scenario_context)))
        
        for thread in thread_list:
            thread.start()
            
        while thread_list:
            for t in thread_list[:]:
                if not t.is_alive():
                    t.join()
                    thread_list.remove(t)
    
    def __execute_sequential_groups_in_outlinie(self, sequential_groups: list, all_scenario_context = None):
        if all_scenario_context is None:
            all_scenario_context = super()._get_all_scenario_context()
            
        for sequential_group in sequential_groups:
            super()._inject_doc_string_and_data_table_to_context(sequential_group.get_all_steps())
            group_errors = sequential_group.run_all_steps(all_scenario_context)
            super()._remove_doc_string_and_data_table_from_context()
            
            step_to_domain_name_and_sceanrio_name = sequential_group.get_step_to_domain_name_and_scenario_name()
            executed_steps = sequential_group.get_all_steps()

            if group_errors:
                traceback_messages = ""
                error_message = ""
                continue_after_failure_flag = True
                for traceback_message, exception in group_errors:
                    traceback_messages += traceback_message
                    step_description = exception.thread.name
                    super()._mark_failed_step(step_description, executed_steps)
                    
                    error_message += f"    {exception.exc_type.__name__} from step: {exception.thread.name}"
                    error_message += f",\n    error message: {exception.exc_value}\n\n" if str(exception.exc_value) != "" else "\n\n\n"
                        
                    for step in sequential_group.get_all_steps():
                        if step.description == exception.thread.name and step.continue_after_failure is not True:
                            continue_after_failure_flag = False
                    
                    self.error_log += traceback_messages + "\n\033[1;91mError(s) in the group:\n\n\033[0;91m" + error_message + "\033[0m"

                    group_errors.clear()
                    
                    if not continue_after_failure_flag:
                        self._tear_down()
                        
                        super()._mark_step_as_executed(executed_steps, step_to_domain_name_and_sceanrio_name)
                        return
                    
            steps = sequential_group.get_all_steps()
            self._mark_step_as_executed(steps, step_to_domain_name_and_sceanrio_name)
    
    def __update_step_kwargs(self, example_index, sequential_groups):
        snake_case_key_to_origin_key = {}
        snake_case_keys = [key.replace(' ', '_') for key in self.examples[example_index].keys()]
        for key in self.examples[example_index].keys():
            snake_case_key_to_origin_key.update({key.replace(' ', '_'): key})

        for sequential_group in sequential_groups:
            for step in sequential_group.get_all_steps():
                for step_key in step.kwargs.keys():
                    if step_key not in snake_case_keys:
                        step.executed = ExecuteState.SKIP
                        # sequential_group.get_all_steps().remove(step)
                        # if len(sequential_group.get_all_steps()) == 0:
                            # sequential_groups.remove(sequential_group)
                    else:
                        step.kwargs[step_key] = self.examples[example_index][snake_case_key_to_origin_key[step_key]]
    
    def __check_iterate_count(self):
        if self.__has_examples():
            iterate_count = len(self.examples)
            variable_count = len(self.examples[0])
            for example in self.examples[1:]:
                if len(example) != variable_count: raise Exception("Invalid examples count")

            return iterate_count

    def __has_examples(self):
        return self.examples != None and self.examples != []

    def __add_example_variables_to_step_kwargs(self):
        for selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.values():
            for step in selected_scenario.get_steps():
                self.__add_variable_relationship_in_step_kwargs(step)
        
        for step_node in PreOrderIter(self.step_order_tree_root):
            if hasattr(step_node, "step"):
                self.__add_variable_relationship_in_step_kwargs(step_node.step)
    
    def __add_variable_relationship_in_step_kwargs(self, step):
        example_variables = re.findall(r"<(.*?)>", step.description)
        if example_variables:
            for variable in example_variables:
                variable_to_keyword = {variable.replace(' ', '_'): None}
                step.kwargs = {**step.kwargs, **variable_to_keyword}
                
    def __print_execution_result(self, iterate_count):
        print("\n\033[1;40m Execution Result: \033[0m")
        domain_name_and_scenario_name_tuple_to_steps = {}
        for domain_name_and_scenario_name_tuple, selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.items():
            domain_name_and_scenario_name_tuple_to_steps[domain_name_and_scenario_name_tuple] = selected_scenario.steps
        print(f"\033[1;7m System Scenario Outline: {self.system_scenario_name} \033[0m")
        
        system_domain_name = "system"
        
        for step_node in PreOrderIter(self.step_order_tree_root):
            find_in_selected_scenario = False
            if hasattr(step_node, "step"):
                for domain_name_and_scenario_name_tuple, steps in domain_name_and_scenario_name_tuple_to_steps.items():
                    domain_name = domain_name_and_scenario_name_tuple[0]
                    scenario_name = domain_name_and_scenario_name_tuple[1]
                    for step in steps:
                        if step_node.step.description == step.description and step_node.step.lead_step == step.lead_step:
                            step_name = self.__replace_name_in_angle_brackets_to_example(step, iterate_count)
                            if step.executed == ExecuteState.ERROR:
                                print(f"\033[1;91m \u2716 \033[0;91m[ {domain_name:<18} ] {step_node.name} {step_name} \033[0m")
                            elif step.executed == ExecuteState.EXECUTED:
                                print(f"\033[0;32m \u2714 [ {domain_name:<18} ] {step_node.name} {step_name} \033[0m")
                            elif step.executed == ExecuteState.SKIP:
                                print(f"\033[1;90m \u2013 \033[0;90m [ {domain_name:<18} ] {step_node.name} {step_name} \033[0m")
                            elif step.executed == ExecuteState.NOT_EXECUTED:
                                print(f"\033[1;33m ? \033[0;33m[ {domain_name:<18} ] {step_node.name} {step_name} \033[0m")
                            find_in_selected_scenario = True
                            super()._print_data_table_and_doc_string_if_contain(step, indent = "\t\t\t      ")
                            break
                    if find_in_selected_scenario:
                        break
                
                if find_in_selected_scenario is False:
                    step_name = self.__replace_name_in_angle_brackets_to_example(step_node.step, iterate_count)
                    if step_node.step.executed == ExecuteState.ERROR:
                        print(f"\033[1;91m \u2716 \033[0;91m[ {system_domain_name:<18} ] {step_node.name} {step_name} \033[0m")
                    elif step_node.step.executed == ExecuteState.EXECUTED:
                        print(f"\033[0;32m \u2714 [ {system_domain_name:<18} ] {step_node.name} {step_name} \033[0m")
                    elif step.executed == ExecuteState.SKIP:
                        print(f"\033[1;90m \u2013 \033[0;90m [ {system_domain_name:<18} ] {step_node.name} {step_name} \033[0m")
                    elif step_node.step.executed == ExecuteState.NOT_EXECUTED:
                        print(f"\033[1;33m ? \033[0;33m[ {system_domain_name:<18} ] {step_node.name} {step_name} \033[0m")
                    super()._print_data_table_and_doc_string_if_contain(step, indent = "\t\t\t      ")
        print()

        for domain_name_and_scenario_name_tuple, steps in domain_name_and_scenario_name_tuple_to_steps.items():
            domain_name = domain_name_and_scenario_name_tuple[0]
            scenario_name = domain_name_and_scenario_name_tuple[1]
            print(f"\033[1;7m {domain_name} scenario: {scenario_name} \033[0m")  
            for step in steps:
                step_name = self.__replace_name_in_angle_brackets_to_example(step, iterate_count)
                if step.executed == ExecuteState.ERROR:
                    print(f"\033[1;91m \u2716 \033[0;91m{step.step} {step_name} \033[0m")
                elif step.executed == ExecuteState.EXECUTED:
                    print(f"\033[0;32m \u2714 {step.step} {step_name} \033[0m")
                elif step.executed == ExecuteState.SKIP:
                    print(f"\033[1;90m \u2013\033[0;90m {step.step} {step_name} \033[0m")
                elif step.executed == ExecuteState.NOT_EXECUTED:
                    print(f"\033[1;33m ? \033[0;33m{step.step} {step_name} \033[0m")
                self._print_data_table_and_doc_string_if_contain(step, indent = "        ")
            print()
    