from ..status import Status
from ..feature import FeatureManager

class TestResultSummarizer:
    def __init__(self) -> None:
        self.feature_count = 0
        self.passed_feature_count = 0
        self.scenario_count = 0
        self.passed_scenario_count = 0
        self.step_count = 0
        self.passed_step_count = 0
        self.undefined_step_count = 0
        self.untested_step_count = 0
        self.failed_scenarios = []

    def summarize(self):
        self.feature_count = len(FeatureManager.get_features())

        for feature_name, feature in FeatureManager.get_features().items():
            scenario_count = 0
            passed_scenario_count = 0

            for scenario in feature["scenarios"]:
                if scenario.__class__.__name__ == "ScenarioOutline" and scenario.has_examples():
                    scenario_count += len(scenario.example_execution_result.items())
                    for count, result in scenario.example_execution_result.items():
                        background_result = result.get("background", None)
                        if background_result != None:
                            for step in background_result["steps"]:
                                self.step_count += 1
                                if step.execution_result == Status.passed: self.passed_step_count += 1
                                elif step.execution_result == Status.undefined: self.undefined_step_count += 1
                                elif step.execution_result == Status.untested: self.untested_step_count += 1

                        if result["execution_result"] == Status.passed:
                            passed_scenario_count += 1
                        for step in result["steps"]:
                            self.step_count += 1
                            if step.execution_result == Status.passed: self.passed_step_count += 1
                            elif step.execution_result == Status.undefined: self.undefined_step_count += 1
                            elif step.execution_result == Status.untested: self.untested_step_count += 1
                    if scenario.execution_result != Status.passed:
                        self.failed_scenarios.append(scenario)
                    
                else:
                    scenario_count += 1
                    if scenario.background_execution_result:
                        for step in scenario.background_execution_result["steps"]:
                            self.step_count += 1
                            if step.execution_result == Status.passed: self.passed_step_count += 1
                            elif step.execution_result == Status.undefined: self.undefined_step_count += 1
                            elif step.execution_result == Status.untested: self.untested_step_count += 1
                    
                    if scenario.execution_result == Status.passed:
                        passed_scenario_count += 1
                    else:
                        self.failed_scenarios.append(scenario)
                    
                    for sequential_group in scenario.get_groups():
                        for step in sequential_group.get_all_steps():
                            self.step_count += 1
                            if step.execution_result == Status.passed: self.passed_step_count += 1
                            elif step.execution_result == Status.undefined: self.undefined_step_count += 1
                            elif step.execution_result == Status.untested: self.untested_step_count += 1
            
            self.scenario_count += scenario_count
            self.passed_scenario_count += passed_scenario_count
            if scenario_count == passed_scenario_count:
                self.passed_feature_count += 1

    def get_summary_printout(self):
        if self.feature_count == 0: return "" 

        failed_scenario_summary = ""
        if self.failed_scenarios:
            failed_scenario_summary = "\nFailing scenarios:\n"
            for scenario in self.failed_scenarios:
                if scenario.__class__.__name__ == "ScenarioOutline" and scenario.has_examples():
                    for count, result in scenario.example_execution_result.items():
                        if result["execution_result"] != Status.passed:
                            failed_scenario_summary += f"  {scenario.location}  {scenario.get_scenario_name()} - Example #{count + 1}\n"
                else:
                    failed_scenario_summary += f"  {scenario.location}  {scenario.get_scenario_name()}\n"

        feature_result = f"{self.passed_feature_count} feature{'s' if self.passed_feature_count > 1 else ''} passed, {self.feature_count - self.passed_feature_count} failed\n"
        scenario_result = f"{self.passed_scenario_count} scenario{'s' if self.passed_scenario_count > 1 else ''} passed, {self.scenario_count - self.passed_scenario_count} failed\n"
        step_result = f"{self.passed_step_count} step{'s' if self.passed_step_count > 1 else ''} passed, {self.step_count - self.passed_step_count - self.undefined_step_count - self.untested_step_count} failed, {self.untested_step_count} skipped, {self.undefined_step_count} undefined\n"
        return failed_scenario_summary + "\n" + feature_result + scenario_result + step_result