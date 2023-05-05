import sys
sys.path.append("../")
from .scenario import Scenario
from .execute_state import ExecuteState

class SelectedScenario:
    def __init__(self, scenario: Scenario):
        self.scenario: Scenario = scenario
        self.scenario_name: str = self.scenario.get_scenario_name()
        self.steps: list = [step for sequential_group in self.scenario.get_groups() for step in sequential_group.get_all_steps()]
        self.step_definition_instance = None
    
    def compare(self, selected_step)-> list:
        pending_steps = []
        selected_step_name = selected_step.description
        
        for step in self.steps:
            if step.executed == ExecuteState.NOT_EXECUTED and selected_step_name != step.description:
                pending_steps.append(step)
            elif step.executed == ExecuteState.NOT_EXECUTED and selected_step_name == step.description:
                self.__check_kwargs_is_matching(step, selected_step)
                self.__check_data_table_is_matching(step, selected_step)
                self.__check_doc_string_is_matching(step, selected_step)
                
                pending_steps.append(step)
                return pending_steps
            
        return []
    
    def __check_kwargs_is_matching(self, step, selected_step):
        if step.kwargs.keys() != selected_step.kwargs.keys():
            raise Exception("The kwargs passed by the system scenario need to correspond with the low level step completely.")
        else:
            step.kwargs = selected_step.kwargs
        
        if step.doc_string != selected_step.doc_string:
            raise Exception("The doc string passed by the system scenario need to correspond with the low level step completely.")
        else:
            step.doc_string = selected_step.doc_string
        
    def __check_data_table_is_matching(self, step, selected_step):
        if step.data_table is not None and selected_step.data_table is not None:
            if step.data_table.to_list() != selected_step.data_table.to_list():
                raise Exception("The data table passed by the system scenario need to correspond with the low level step completely.")
        elif (step.data_table is None) != (selected_step.data_table is None):
            raise Exception("The data table passed by the system scenario need to correspond with the low level step completely.")
        else:
            step.data_table = selected_step.data_table 
            
    def __check_doc_string_is_matching(self, step, selected_step):
        if step.doc_string != selected_step.doc_string:
            raise Exception("The doc string passed by the system scenario need to correspond with the low level step completely.")
        else:
            step.doc_string = selected_step.doc_string
            
    def get_all_given_sequential_groups(self):
        given_sequential_groups = []
        for sequential_group in self.scenario.get_groups():
            if sequential_group.get_all_steps()[0].lead_step == "Given":
                given_sequential_groups.append(sequential_group)
            else:
                break
            
        return given_sequential_groups
    
    def get_scenario_context(self):
        if self.step_definition_instance is None:
            self.step_definition_instance = self.scenario.initialize_scenario_context()
            return self.step_definition_instance
        else:
            return self.step_definition_instance
        
    def get_scenario_name(self):
        return self.scenario_name
    
    def get_steps(self):
        return self.steps