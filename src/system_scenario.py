import io, sys, unittest, traceback, threading
from pathlib import Path
from anytree import Node, PreOrderIter, RenderTree
from concurrentSpec.src.feature import FeatureManager, Feature
from .scenario import Scenario
from .step import Step
from .sequential_group import SequentialGroup
from .selected_scenario import SelectedScenario
from .execute_state import ExecuteState
from .custom_test_result import SilentTestResult

class SystemScenario:
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
        
    def add_project_path(self, project_path: str):
        self.project_path = project_path        

        return self
    
    def select_scenario(self, domain_name: str, scenario_name: str):
        sys.stdout.write("\033[?25l") 
        print(f"Selecting {domain_name} domain's scenario...", end="\r")
        sys.stderr = io.StringIO()
        self.__discover_all_scenario_under_specified_domain_by_unittest(domain_name = domain_name)
        sys.stderr = sys.__stderr__
        scenario = self.__find_scenario_by_domain_name_and_scenario_name(domain_name = domain_name, scenario_name = scenario_name)
        self.__save_scenario_as_selected_scenario(domain_name = domain_name, scenario_name = scenario_name, scenario = scenario)
        
        if self.__the_domain_has_been_selected_before((domain_name, scenario_name)):
            self.__construct_the_relationship_between_then_step_and_given_step(domain_name, scenario_name)
        
        if self.__current_domain_is_not_the_first_domain((domain_name, scenario_name)):
            self.__construct_the_relationship_between_then_step_and_when_step(domain_name, scenario_name)
        print("\033[K", end="")
        sys.stdout.write("\033[?25h")
        
        return self
    
    def __the_domain_has_been_selected_before(self, domain_name_and_scenairo_name):
        domain_names_and_scenario_names = self.__get_current_all_selected_domain_names_and_scenario_names()
        if domain_name_and_scenairo_name not in domain_names_and_scenario_names:
            return False
        else:
            current_domain_name = domain_name_and_scenairo_name[0]
            index = domain_names_and_scenario_names.index(domain_name_and_scenairo_name)
            if current_domain_name in [ domain_name for domain_name, _ in domain_names_and_scenario_names[:index]]: 
                return True
            else: 
                return False
    
    def __construct_the_relationship_between_then_step_and_given_step(self, domain_name: str, scenario_name: str):
        previous_domain_name_and_scenario_name: tuple = self.__get_the_previous_selected_scenario_under_same_domain((domain_name, scenario_name))
        previous_domain_name = previous_domain_name_and_scenario_name[0]
        previous_domain_steps = self.domain_name_and_scenario_name_tuple_to_selected_scenario.get(previous_domain_name_and_scenario_name).steps
        current_domain_steps = self.domain_name_and_scenario_name_tuple_to_selected_scenario.get((domain_name, scenario_name)).steps
        for current_domain_step in current_domain_steps:
            if current_domain_step.lead_step == "Given":
                if current_domain_step.description in [previous_domain_step.description for previous_domain_step in previous_domain_steps]:
                    self.then_given_matching_groups.append({(previous_domain_name, "Then", current_domain_step.description): current_domain_step})
                else:
                    raise Exception("Multiple scenarios with the same domain are present, where the \"Given\" statement of a later scenario must correspond to one of the \"Then\" statements in the System Scenario.")
    
    def __get_the_previous_selected_scenario_under_same_domain(self, domain_name_and_scenario_name_tuple):
        domain_names_and_scenario_names = self.__get_current_all_selected_domain_names_and_scenario_names()
        index = domain_names_and_scenario_names.index(domain_name_and_scenario_name_tuple)
        
        for selected_domain_name, selected_scenario_name in reversed(domain_names_and_scenario_names[:index]):
            if selected_domain_name == domain_name_and_scenario_name_tuple[0]:
                return (selected_domain_name, selected_scenario_name)
    
    def __current_domain_is_not_the_first_domain(self, domain_name_and_scenairo_name):
        domain_names_and_scenario_names = self.__get_current_all_selected_domain_names_and_scenario_names()
        
        return True if domain_names_and_scenario_names.index(domain_name_and_scenairo_name) != 0 else False
    
    def __get_current_all_selected_domain_names_and_scenario_names(self):
        return [domain_name_and_scenario_name for domain_name_and_scenario_name in self.domain_name_and_scenario_name_tuple_to_selected_scenario.keys()]
    
    def __construct_the_relationship_between_then_step_and_when_step(self, domain_name: str, scenario_name: str):
        previous_domain_name_and_scenario_name: tuple = self.__get_the_previous_domain((domain_name, scenario_name))
        previous_domain_name = previous_domain_name_and_scenario_name[0]
        previous_domain_steps = self.domain_name_and_scenario_name_tuple_to_selected_scenario.get(previous_domain_name_and_scenario_name).steps
        current_domain_steps = self.domain_name_and_scenario_name_tuple_to_selected_scenario.get((domain_name, scenario_name)).steps
        for current_domain_step in current_domain_steps:
            if current_domain_step.lead_step == "When":
                if current_domain_step.description in [previous_domain_step.description for previous_domain_step in previous_domain_steps]:
                    self.then_when_matching_groups.append({(previous_domain_name, "Then", current_domain_step.description): current_domain_step})
                else:
                    raise Exception("The \"When\" part in subsequent Scenarios must match the \"Then\" part mentioned in the System Scenario.")
        
    def __discover_all_scenario_under_specified_domain_by_unittest(self, domain_name: str):
        FeatureManager.clear()
        domain_path = self.project_path + domain_name + "/"
        suite = unittest.TestSuite()
        
        try:
            suite.addTest(unittest.defaultTestLoader.discover(domain_path, top_level_dir=self.project_path))
        except ImportError as e:
            raise Exception(f"\033[0;31mDomain path: \"{domain_path}\" should contain __init__.py\033[0m")

        if suite.countTestCases() == 0:
            raise Exception(f"\033[0;31mDomain path: \"{domain_path}\" doesn't have any test case\033[0m")
        
        unittest.TextTestRunner(resultclass=SilentTestResult).run(suite)
        
    def __find_scenario_by_domain_name_and_scenario_name(self, domain_name: str, scenario_name: str):
        features = FeatureManager.get_features()

        for _, feature_content in features.items():
            for scenario in feature_content["scenarios"]:
                if scenario_name == scenario.get_scenario_name():
                    return scenario
        
        raise Exception(f"Can not find scenario: {scenario_name} under domain: {domain_name}")
    
    def __save_scenario_as_selected_scenario(self, domain_name: str, scenario_name: str, scenario: Scenario):
        self.domain_name_and_scenario_name_tuple_to_selected_scenario[(domain_name, scenario_name)] = SelectedScenario(scenario)
        
    def Given(self, name: str, doc_string = "", data_table = None, **kwargs):
        given_step = Step(step = "Given", description = name, kwargs = kwargs, doc_string = doc_string, data_table = data_table)
        self.__insert_to_step_order_tree(name = "Given", parent = self.step_order_tree_root, step = given_step)
        
        return self
        
    def When(self, name: str, doc_string = "", data_table = None, **kwargs):
        when_step = Step(step = "When", description = name, kwargs = kwargs, doc_string = doc_string, data_table = data_table)
        self.__insert_to_step_order_tree(name = "When", parent = self.step_order_tree_root, step = when_step)
        
        return self
        
    def Then(self, name: str, doc_string = "", data_table = None, **kwargs):
        then_step = Step(step = "Then", description = name, kwargs = kwargs, doc_string = doc_string, data_table = data_table)
        self.__insert_to_step_order_tree(name = "Then", parent = self.step_order_tree_root, step = then_step)
        
        return self
        
    def And(self, name: str, doc_string = "", data_table = None, **kwargs):
        last_lead_step_node = self.__get_last_lead_step_node()
        and_step = Step(step = "And", description = name, kwargs = kwargs, doc_string = doc_string, data_table = data_table, lead_step = last_lead_step_node.step.step)
        self.__insert_to_step_order_tree(name = "And", parent = last_lead_step_node, step = and_step)
        
        return self
    
    def But(self, name: str, doc_string = "", data_table = None, **kwargs):
        last_lead_step_node = self.__get_last_lead_step_node()
        but_step = Step(step = "But", description = name, kwargs = kwargs, doc_string = doc_string, data_table = data_table, lead_step = last_lead_step_node.step.step)
        self.__insert_to_step_order_tree(name = "But", parent = last_lead_step_node, step = but_step)
        
        return self
        
    def __insert_to_step_order_tree(self, name:str, parent:Node, step:Step):
        Node(name = name, parent = parent, step = step)
        
    def __get_last_lead_step_node(self):
        return self.step_order_tree_root.children[-1]
    
    def execute(self):
        self.__print_selected_step()
        self._create_scenario_in_system_domain()
        self._set_up()
        self.__compare_and_execute_step()
        self._tear_down()
        self.__print_execution_result()
        
        if self.error_log != "":
            raise RuntimeError(self.error_log)
    
    def __print_selected_step(self):
        print(f"\n\033[1;40m System Scenario: {self.system_scenario_name} \033[0m")
        
        for step_node in PreOrderIter(self.step_order_tree_root):
            if hasattr(step_node, "step"):
                step = step_node.step
            else:
                continue
            print(f"\033[0;34m  {step.step}\033[0m {step.description}")
            self._print_data_table_and_doc_string_if_contain(step, "        ")
        print()

    def _create_scenario_in_system_domain(self):
        FeatureManager.clear()
        feature_name = "system scenario"
        step_definition_folder_path = self.project_path + "/system/" + "steps/"
        Feature(feature_name = feature_name)
        self.system_scenario = Scenario(scenario_name = self.system_scenario_name, 
                                        step_definition_folder_path = step_definition_folder_path)
        
    def _set_up(self):
        print("\033[1;40m Execution Log: \033[0m\n", end="")

        self.system_context = self.system_scenario.initialize_scenario_context()
        if getattr(self.system_context, 'set_up', False):  
            self.system_context.set_up()
    
    def __compare_and_execute_step(self):
        sequential_groups = []
        
        for step_node in PreOrderIter(self.step_order_tree_root):
            if hasattr(step_node, "step"):
                high_level_step_keyword = step_node.name
                step = step_node.step
            else:
                continue
            if step_node.name == "When":
                self._bind_domain_environment_to_system_environment()   
                self.__execute_all_internal_given_step()
                if self.error_log != "":
                    return
            
            self._compare_step_with_selected_scenario(sequential_groups, step, high_level_step_keyword)
            self._bind_domain_environment_to_system_environment()
            
            if step_node.children == ():
                self.__execute_sequential_groups(sequential_groups)
                sequential_groups = []
    
    def __execute_all_internal_given_step(self):
        domain_occur_history = []
        domain_name_and_scenario_name_tuple_to_given_sequential_groups = {}
        thread_list = []
        for domain_name_and_scenario_name_tuple, selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.items():
            domain_name = domain_name_and_scenario_name_tuple[0]
            if domain_name in domain_occur_history:
                continue
            else:
                domain_occur_history.append(domain_name)
                domain_name_and_scenario_name_tuple_to_given_sequential_groups[domain_name_and_scenario_name_tuple] = selected_scenario.get_all_given_sequential_groups()
        all_scenario_context = self._get_all_scenario_context()
        
        for domain_name_and_scenario_name_tuple, given_sequential_groups in domain_name_and_scenario_name_tuple_to_given_sequential_groups.items():
            scenario_context = all_scenario_context.get(domain_name_and_scenario_name_tuple)
            
            thread_list.append(threading.Thread(target = self.__execute_sequential_groups, args = (given_sequential_groups, scenario_context)))
        
        for thread in thread_list:
            thread.start()
            
        while thread_list:
            for t in thread_list[:]:
                if not t.is_alive():
                    t.join()
                    thread_list.remove(t)
        # return
    
    def _compare_step_with_selected_scenario(self, sequential_groups, selected_step, high_level_step_keyword):
        for domain_name_and_scenario_name, selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.items():
            steps = []
            domain_name = domain_name_and_scenario_name[0]
            scenario_name = domain_name_and_scenario_name[1]
            
            steps = selected_scenario.compare(selected_step)
            for pending_step in steps:
                if self.__step_is_not_added_into_sequential_group(pending_step, sequential_groups) and pending_step.executed == ExecuteState.NOT_EXECUTED:
                    if pending_step.description == selected_step.description:
                        self.__add_step_to_sequential_group_according_to_high_level_step(pending_step, domain_name, scenario_name, sequential_groups, high_level_step_keyword)
                    elif pending_step.description != selected_step.description:
                        self.__keep_up_with_the_progress(pending_step, domain_name, scenario_name, sequential_groups)
            if len(steps) != 0:
                return
        
        selected_step.write_function_to_file(self.system_scenario.step_definition_file_path, Path(self.system_scenario.step_definition_file_path).read_text())
        self.__add_step_to_sequential_group_according_to_high_level_step(selected_step, "system", self.system_scenario_name, sequential_groups, high_level_step_keyword)
        self.__update_system_context()
    
    def __step_is_not_added_into_sequential_group(self, step_need_to_check, sequential_groups):
        for sequential_group in sequential_groups:
            if step_need_to_check in [step for step in sequential_group.get_all_steps()]: return False
        else: return True
    
    def _bind_domain_environment_to_system_environment(self):
        system_data_members = self.system_context.__dict__
        for selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.values():
            selected_scenario.get_scenario_context().__dict__ = system_data_members

    def _get_all_scenario_context(self):
        all_scenario_context = {}
        all_scenario_context[("system", self.system_scenario_name)] = self.system_context
        for domain_name_and_scenario_name, selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.items():
            all_scenario_context[domain_name_and_scenario_name] = selected_scenario.get_scenario_context()
        
        return all_scenario_context
        
    def __execute_sequential_groups(self, sequential_groups: list, all_scenario_context = None):
        if all_scenario_context is None:
            all_scenario_context = self._get_all_scenario_context()
            
        for sequential_group in sequential_groups:
            self._inject_doc_string_and_data_table_to_context(sequential_group.get_all_steps())
            group_errors = sequential_group.run_all_steps(all_scenario_context)
            self._remove_doc_string_and_data_table_from_context()
            
            step_to_domain_name_and_sceanrio_name = sequential_group.get_step_to_domain_name_and_scenario_name()
            executed_steps = sequential_group.get_all_steps()

            if group_errors:
                traceback_messages = ""
                error_message = ""
                continue_after_failure_flag = True
                for traceback_message, exception in group_errors:
                    traceback_messages += traceback_message
                    step_description = exception.thread.name
                    self._mark_failed_step(step_description, executed_steps)
                    
                    error_message += f"    {exception.exc_type.__name__} from step: {exception.thread.name}"
                    error_message += f",\n    error message: {exception.exc_value}\n\n" if str(exception.exc_value) != "" else "\n\n\n"
                        
                    for step in sequential_group.get_all_steps():
                        if step.description == exception.thread.name and step.continue_after_failure is not True:
                            continue_after_failure_flag = False
                    
                    self.error_log += traceback_messages + "\n\033[1;31mError(s) in the group:\n\n\033[0;31m" + error_message + "\033[0m"

                    group_errors.clear()
                    
                    if not continue_after_failure_flag:
                        self._tear_down()
                        
                        self._mark_step_as_executed(executed_steps, step_to_domain_name_and_sceanrio_name)
                        self.__print_execution_result()
                        raise RuntimeError(self.error_log)
                    
            steps = sequential_group.get_all_steps()
            self._mark_step_as_executed(steps, step_to_domain_name_and_sceanrio_name)
    
    def _inject_doc_string_and_data_table_to_context(self, concurrent_steps):
        doc_string_count, data_table_count = 0, 0
        for step in concurrent_steps:
            if step.doc_string != "": doc_string_count += 1
            if step.data_table is not None: data_table_count += 1
        if doc_string_count > 1 or data_table_count > 1: raise Exception("Do not support multiple doc string or data table in concurrent steps.")

        for step in concurrent_steps:
            if step.doc_string != "":
                self.system_context.__dict__.update({"text": step.doc_string})
            if step.data_table is not None:
                self.system_context.__dict__.update({"table": step.data_table.to_list_of_dict()})
    
    def _remove_doc_string_and_data_table_from_context(self):
        if "text" in self.system_context.__dict__: self.system_context.__dict__.pop("text")
        if "table" in self.system_context.__dict__: self.system_context.__dict__.pop("table")
    
    def _mark_step_as_executed(self, steps, step_to_domain_name_and_sceanrio_name):
        for step in steps:
            if step.executed == ExecuteState.NOT_EXECUTED:
                step.executed = ExecuteState.EXECUTED
                if step_to_domain_name_and_sceanrio_name.get(step) is not None:
                    domain_name = step_to_domain_name_and_sceanrio_name[step][0]
                
                    for then_given_matching_group in self.then_given_matching_groups:
                        if then_given_matching_group.get((domain_name, step.lead_step, step.description)):
                            then_given_matching_group.get((domain_name, step.lead_step, step.description)).executed = ExecuteState.EXECUTED

                    for then_when_matching_group in self.then_when_matching_groups:
                        if then_when_matching_group.get((domain_name, step.lead_step, step.description)):
                            then_when_matching_group.get((domain_name, step.lead_step, step.description)).executed = ExecuteState.EXECUTED
            
    def _mark_failed_step(self, step_description, executed_steps):
        for executed_step in executed_steps:
            if step_description == executed_step.description and executed_step.executed == ExecuteState.NOT_EXECUTED:
                executed_step.executed = ExecuteState.ERROR
            
    def _tear_down(self):
        step_definition_instance = self.system_context
        if getattr(step_definition_instance, 'tear_down', False):  
            step_definition_instance.tear_down()
    
    def __print_execution_result(self):
        print("\n\033[1;40m Execution Result: \033[0m")
        domain_name_and_scenario_name_tuple_to_steps = {}
        for domain_name_and_scenario_name_tuple, selected_scenario in self.domain_name_and_scenario_name_tuple_to_selected_scenario.items():
            domain_name_and_scenario_name_tuple_to_steps[domain_name_and_scenario_name_tuple] = selected_scenario.steps
        print(f"\033[1;7m System Scenario: {self.system_scenario_name} \033[0m")
        
        system_domain_name = "system"
        
        for step_node in PreOrderIter(self.step_order_tree_root):
            find_in_selected_scenario = False
            if hasattr(step_node, "step"):
                for domain_name_and_scenario_name_tuple, steps in domain_name_and_scenario_name_tuple_to_steps.items():
                    domain_name = domain_name_and_scenario_name_tuple[0]
                    scenario_name = domain_name_and_scenario_name_tuple[1]
                    for step in steps:
                        if step_node.step.description == step.description and step_node.step.lead_step == step.lead_step:
                            if step.executed == ExecuteState.ERROR:
                                print(f"\033[1;91m \u2716 \033[0;91m[ {domain_name:<18} ] {step_node.name} {step.description} \033[0m")
                            elif step.executed == ExecuteState.EXECUTED:
                                print(f"\033[0;32m \u2714 [ {domain_name:<18} ] {step_node.name} {step.description} \033[0m")
                            elif step.executed == ExecuteState.NOT_EXECUTED:
                                print(f"\033[1;33m ? \033[0;33m[ {domain_name:<18} ] {step_node.name} {step.description} \033[0m")
                            find_in_selected_scenario = True
                            self._print_data_table_and_doc_string_if_contain(step, indent = "\t\t\t      ")
                            break
                    if find_in_selected_scenario:
                        break
                
                if find_in_selected_scenario is False:
                    if step_node.step.executed == ExecuteState.ERROR:
                        print(f"\033[1;91m \u2716 \033[0;91m[ {system_domain_name:<18} ] {step_node.name} {step_node.step.description} \033[0m")
                    elif step_node.step.executed == ExecuteState.EXECUTED:
                        print(f"\033[0;32m \u2714 [ {system_domain_name:<18} ] {step_node.name} {step_node.step.description} \033[0m")
                    elif step_node.step.executed == ExecuteState.NOT_EXECUTED:
                        print(f"\033[1;33m ? \033[0;33m[ {system_domain_name:<18} ] {step_node.name} {step_node.step.description} \033[0m")
                    self._print_data_table_and_doc_string_if_contain(step_node.step, indent = "\t\t\t      ")
        print()

        for domain_name_and_scenario_name_tuple, steps in domain_name_and_scenario_name_tuple_to_steps.items():
            domain_name = domain_name_and_scenario_name_tuple[0]
            scenario_name = domain_name_and_scenario_name_tuple[1]
            print(f"\033[1;7m {domain_name} scenario: {scenario_name} \033[0m")  
            for step in steps:
                if step.executed == ExecuteState.ERROR:
                    print(f"\033[1;91m \u2716 \033[0;91m{step.step} {step.description} \033[0m")
                elif step.executed == ExecuteState.EXECUTED:
                    print(f"\033[0;32m \u2714 {step.step} {step.description} \033[0m")
                elif step.executed == ExecuteState.NOT_EXECUTED:
                    print(f"\033[1;33m ? \033[0;33m{step.step} {step.description} \033[0m")
                self._print_data_table_and_doc_string_if_contain(step, indent = "        ")
            print()
    
    def _print_data_table_and_doc_string_if_contain(self, step, indent):
        if step.doc_string != "":
            print(indent + "\"\"\"") 
            lines = step.doc_string.split("\n")
            for line in lines:
                if indent == "\t\t\t      ":
                    print("\t\t      " + line)
                else:
                    print(line)
            print(indent + "\"\"\"")
            
        if step.data_table is not None: 
            print(step.data_table.get_pretty_string(indent = indent))
    
    def __add_step_to_sequential_group_according_to_high_level_step(self, step, domain_name, scenario_name, sequential_groups, high_level_step_keyword):
        all_steps = [step for sequential_group in sequential_groups for steps in sequential_group.get_all_steps()]
        if high_level_step_keyword in ["Given", "When", "Then"]:
            if self.___step_in_low_level_is_concurrent_step(step, all_steps):
                sequential_groups[-1].add_step(step, domain_name, scenario_name) 
            else:
                sequential_group = SequentialGroup()
                sequential_group.add_step(step, domain_name, scenario_name)
                sequential_groups.append(sequential_group)
        else:
            sequential_groups[-1].add_step(step, domain_name, scenario_name)

    def __update_system_context(self):
        new_system_context = self.system_scenario.initialize_scenario_context()
        data_members = self.system_context.__dict__
        new_system_context.__dict__ = data_members
        self.system_context = new_system_context

    def ___step_in_low_level_is_concurrent_step(self, step, steps):
        if step in steps:
            index = steps.index(step)
            return True if step.step in ["And", "But"] and steps[index - 1].step in ["Then", "And", "But"] else False
        else:
            return False
        
    def __keep_up_with_the_progress(self, step, domain_name, scenario_name, sequential_groups):
        if step.step == step.lead_step: #* Given/When/Then
            sequential_group = SequentialGroup()
            sequential_group.add_step(step, domain_name, scenario_name)
            sequential_groups.append(sequential_group)
        else: #* And/But
            sequential_groups[-1].add_step(step, domain_name, scenario_name)

    def __get_the_previous_domain(self, domain_name_and_scenario_name_tuple):
        domain_names_and_scenario_names = self.__get_current_all_selected_domain_names_and_scenario_names()
        index = domain_names_and_scenario_names.index(domain_name_and_scenario_name_tuple)
        
        return domain_names_and_scenario_names[index - 1]
    
    def get_system_scenario_name(self):
        return self.system_scenario_name
    
    def get_project_path(self):
        return self.project_path
    
    def get_selected_scenario(self, domain_name_and_scenario_name_tuple: tuple):
        return self.domain_name_and_scenario_name_tuple_to_selected_scenario.get(domain_name_and_scenario_name_tuple)
    
    def get_all_selected_scenarios(self):
        return self.domain_name_and_scenario_name_tuple_to_selected_scenario
    
    def get_node_from_step_order_tree_node(self, step_keyword:str, step_name: str):
        for node in PreOrderIter(self.step_order_tree_root):
            if hasattr(node, "step"):
                if node.step.step == step_keyword and node.step.description == step_name:
                    return node
    
    def print_tree_structure(self):
        print(RenderTree(self.step_order_tree_root).by_attr())
    