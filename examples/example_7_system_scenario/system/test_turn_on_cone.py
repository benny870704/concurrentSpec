import sys
sys.path.append("../../../../")
from concurrentSpec.src.system_scenario import SystemScenario, SelectScenario
import unittest

class TestTurnOnCone(unittest.TestCase):
    
    @SelectScenario(domain_name = "cone", scenario_name = "Turn on cone C")
    @SelectScenario(domain_name = "work_site_computer", scenario_name = "Register cone C")
    @SelectScenario(domain_name = "cone", scenario_name = "Warning light flashes")
    def test_cone_warning_light_flashes_when_smart_cone_is_turned_on(self):
        SystemScenario(system_scenario_name = "Warning light flashes when cone C is turned on")\
        .Given("cone C is off")\
        .Given("work site computer W is operational")\
        .Given("cone C is not yet registered")\
        .When("a worker turns on cone C at time T")\
        .Then("a registering message from cone C is at the interface")\
        .Then("the response time is in T+1")\
        .Then("a flashing message from work site computer W is at the interface")\
        .Then("cone warning light flashes")\
        .Then("the response time is in T+2")\
        .execute()
