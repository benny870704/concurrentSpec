import sys
import unittest
sys.path.append("../../../")
from concurrentSpec.src.feature import Feature
from concurrentSpec.src.scenario import Scenario

class TestTurnOnSensorCone(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        Feature("Turn on sensor cone")
        
    def test_cone_c_sends_a_registering_message_when_it_is_turned_on(self):
        Scenario(scenario_name="Turn on cone C")\
        \
        .Given("cone C is off")\
        .When("a worker turns on cone C at time T")\
        .Then("the power-on reset of cone C is successful")\
        .Then("the power-on self-test of cone C is successful")\
        .Then("cone C is operational")\
        .And("cone warning light is on")\
        .Then("a registering message from cone C is at the interface")\
        .execute()
    