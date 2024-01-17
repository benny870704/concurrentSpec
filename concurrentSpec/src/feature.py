import warnings

class __FeatureManager:
    def __init__(self):
        self.class_to_feature = {}
        self.class_to_scenario = {}
        self.tag_info = {}
        self.feature_dictionary = {}
        self.console_output = True
        self.capture_output = True
        self.capture_log = True

    def clear(self):
        self.class_to_feature.clear()
        self.class_to_scenario.clear()
        self.tag_info.clear()
        self.feature_dictionary.clear()

    def __check_feature_is_not_declared_more_than_one(self, class_name, feature_name):
        if class_name not in self.class_to_feature:
            self.class_to_feature.update({class_name: feature_name})
            if class_name not in self.tag_info: self.tag_info[class_name] = {}
        else:
            raise RuntimeError("Declare more than one feature in a file is not allowed.")

    def __check_scenario_is_in_its_feature(self, scenario) -> bool:
        if scenario.get_scenario_name() == "":
            return False
        else:
            for s in self.feature_dictionary[scenario.feature_name]["scenarios"]:
                if scenario.get_scenario_name() == s.get_scenario_name():
                    return True
            return False

    def __check_background_is_in_its_feature(self, background) -> bool:
        if self.get_background(background.get_feature_name()) is None:
            return False
        else:
            return background.get_background_name() == self.get_background(background.get_feature_name()).get_background_name()

    def get_features(self):
        return self.feature_dictionary
    
    def get_feature_name_from_class_name(self, class_name):
        return self.class_to_feature[class_name] if class_name in self.class_to_feature else None
    
    def get_feature_description(self, feature_name):
        return self.feature_dictionary[feature_name]["description"]
    
    def get_background(self, feature_name):
        return self.feature_dictionary[feature_name]["background"]
    
    def get_tags_of_feature(self, feature_name):
        feature_to_class = {value: key for key, value in self.class_to_feature.items()}
        class_name = feature_to_class[feature_name]
        return self.tag_info[class_name].get("tags", [])
    
    def get_tags_of_scenario(self, feature_name, scenario_name):
        feature_to_class = {value: key for key, value in self.class_to_feature.items()}
        scenario_to_class = {scenario_name: key for key, value in self.class_to_scenario.items() for scenario_name in value}
        class_name = ""
        if feature_name in feature_to_class:
            class_name = feature_to_class[feature_name]
        elif scenario_name in scenario_to_class:
            class_name = scenario_to_class[scenario_name]

        if class_name not in self.tag_info: return []
        for key, value in self.tag_info[class_name].items():
            if key != "tags" and scenario_name in value.get("scenario_names", []):
                return value.get("tags", [])
    
    def add_feature_tag(self, class_name, tag):
        if class_name in self.tag_info:
            if "tags" not in self.tag_info[class_name]:
                self.tag_info[class_name].update({"tags": [tag]})
            else:
                self.tag_info[class_name]["tags"].append(tag)
        else:
            self.tag_info[class_name] = {"tags": [tag]}

    def add_scenario_tag(self, class_name, method_name, tag):
        if class_name not in self.tag_info:
            self.tag_info[class_name] = {}
        if method_name in self.tag_info[class_name]:
            if "tags" not in self.tag_info[class_name][method_name]:
                self.tag_info[class_name][method_name].update({"tags": [tag]})
            else:
                self.tag_info[class_name][method_name]["tags"].append(tag)
        else:
            self.tag_info[class_name][method_name] = {}
            self.tag_info[class_name][method_name]["tags"] = [tag]

    def add_background(self, background, class_name):
        if class_name in self.class_to_feature:
            feature_name = self.class_to_feature[class_name]
            if self.__check_background_is_in_its_feature(background):
                warnings.warn(f"\033[1;93m[WARNING] Background: {background.get_background_name()} is already in Feature: {feature_name}\033[0m")
            else:
                self.feature_dictionary[feature_name]["background"] = background

    def add_scenario(self, scenario, class_name, method_name):
        if class_name in self.class_to_feature:
            feature_name = self.class_to_feature[class_name]
            if self.__check_scenario_is_in_its_feature(scenario):
                warnings.warn(f"\033[1;93m[WARNING] Scenario: {scenario.get_scenario_name()} is already in Feature: {feature_name}\033[0m")
            else:
                self.feature_dictionary[feature_name]["scenarios"].append(scenario)
        else:
            if class_name not in self.class_to_scenario:
                self.class_to_scenario[class_name] = [scenario.get_scenario_name()]
            else:
                self.class_to_scenario[class_name].append(scenario.get_scenario_name())
        
        if class_name not in self.tag_info: self.tag_info[class_name] = {}
        if method_name in self.tag_info[class_name]:
            if "scenario_names" not in self.tag_info[class_name][method_name]:
                self.tag_info[class_name][method_name]["scenario_names"] = [scenario.get_scenario_name()]
            else:
                self.tag_info[class_name][method_name]["scenario_names"].append(scenario.get_scenario_name())
        else:
            self.tag_info[class_name][method_name] = {}
            self.tag_info[class_name][method_name]["scenario_names"] = [scenario.get_scenario_name()]

    def add_feature(self, feature_name, feature_description, class_name, location):
        if feature_name in self.feature_dictionary:
            warnings.warn(f"\033[1;93m[WARNING] Feature: {feature_name} has already existed\033[0m", stacklevel=4)
        elif feature_name not in self.feature_dictionary:
            self.__check_feature_is_not_declared_more_than_one(class_name, feature_name)
            self.feature_dictionary[feature_name] = {"location": location, "description": feature_description, "scenarios": [], "background": None}
            

FeatureManager = __FeatureManager()

from .utils import get_where_the_function_is_called

def Feature(feature_name = "", feature_description = ""):
    class_name, location = get_where_the_function_is_called(stack_frame_count = 2)
    FeatureManager.add_feature(feature_name, feature_description, class_name, location)

