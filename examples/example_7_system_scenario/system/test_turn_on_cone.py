import sys
sys.path.append("../../../../")
from concurrentSpec.src.system_scenario import SystemScenario
import unittest

class TestTurnOnCone(unittest.TestCase):
    def test_cone_warning_light_flashes_when_smart_cone_is_turned_on(self):
        SystemScenario(system_scenario_name = "Warning light flashes when cone C is turned on")\
            .select_scenario(domain_name = "cone", 
                             scenario_name = "Turn on cone C")\
            .select_scenario(domain_name = "work_site_computer",
                             scenario_name = "Register cone C")\
            .select_scenario(domain_name = "cone",
                             scenario_name = "Warning light flashes")\
            .Given("cone C connects to work site computer W")\
            .When("the worker turns on cone C")\
            .And("the current time is T")\
            .Then("a registering message is at the interface")\
            .Then("the response time is in T+1")\
            .Then("a flashing message is at the interface")\
            .Then("cone warning light flashes")\
            .Then("the response time is in T+2")\
            .execute()
