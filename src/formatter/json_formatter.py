import json
from ..status import Status
from ..feature import FeatureManager

class JsonFormatter:
    def __init__(self) -> None:
        self.result_in_json = []

    def format_result(self, pretty=False):
        for feature_name, feature in FeatureManager.get_features().items():
            elements = self.format_elements_in_feature(feature_name, feature)
            feature_status = self.__check_feature_execution_result(elements)
            self.result_in_json.append({
                "keyword": "Feature",
                "name": feature_name,
                "description": feature["description"],
                "location": feature["location"],
                "tags": FeatureManager.get_tags_of_feature(feature_name),
                "status": feature_status,
                "elements": elements
            })
        return json.dumps(self.result_in_json) if not pretty else json.dumps(self.result_in_json, indent=2)

    def format_elements_in_feature(self, feature_name, feature):
        elements = []

        if feature.get("background") != None:
            steps = []
            background = feature.get("background")
            for sequential_group in background.get_groups():
                for step in sequential_group.get_all_steps():
                    steps.append(self.format_step(step))

            elements.append({
                "type": "background",
                "keyword": background.__class__.__name__,
                "name": background.get_background_name(),
                "steps": steps,
                "status": background.execution_result.name
            })

        for scenario in feature.get("scenarios"):
            steps = []
            for sequential_group in scenario.get_groups():
                for step in sequential_group.get_all_steps():
                    steps.append(self.format_step(step))

            if scenario.__class__.__name__ == "ScenarioOutline" and scenario.has_examples():
                for count, result in scenario.example_execution_result.items():
                    elements.append({
                        "type": "scenario",
                        "keyword": scenario.__class__.__name__,
                        "name": scenario.get_scenario_name() + f" - Example #{count+1}",
                        "location": scenario.location,
                        "tags": FeatureManager.get_tags_of_scenario(feature_name, scenario.get_scenario_name()),
                        "steps": [self.format_step(step) for step in result["steps"]],
                        "status": result["execution_result"].name,
                    })
            else:
                elements.append({
                    "type": "scenario",
                    "keyword": scenario.__class__.__name__,
                    "name": scenario.get_scenario_name(),
                    "location": scenario.location,
                    "tags": FeatureManager.get_tags_of_scenario(feature_name, scenario.get_scenario_name()),
                    "steps": steps,
                    "status": scenario.execution_result.name,
                })

        return elements

    def format_step(self, step):
        step_in_json = {
            "keyword": step.step,
            "step_type": step.lead_step,
            "name": step.description,
            "location": step.location,
        }
        if step.doc_string != "": step_in_json.update({"text": step.doc_string})
        if step.data_table != None: step_in_json.update({"table": step.data_table.to_list_of_key_to_values()})

        result_in_step = {"status": step.execution_result.name, "duration": step.execution_time}
        if step.execution_result == Status.failed: result_in_step.update({"error_message": step.error_message.split('\n')})
        step_in_json.update(result_in_step)
        return step_in_json
    
    def __check_feature_execution_result(self, elements):
        for element in elements:
            if element["status"] != Status.passed: return element["status"]
        return Status.passed.name