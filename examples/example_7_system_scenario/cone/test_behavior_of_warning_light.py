import sys
import unittest
sys.path.append("../../../")
from concurrentSpec.src.feature import Feature
from concurrentSpec.src.scenario import Scenario

class TestBehaviorOfWarningLight(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        Feature("Behavior of warning light")
        
    def test_warning_light_flashes_when_it_receives_a_flashing_message(self):
        Scenario(scenario_name = "Warning light flashes")\
        \
        .Given("cone C is operational")\
        .When("a flashing message is at the interface")\
        .Then("cone warning light flashes")\
        .execute()
        
        