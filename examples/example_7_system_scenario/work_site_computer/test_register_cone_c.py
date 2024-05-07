import sys
import unittest
sys.path.append("../../../")
from concurrentSpec.src.feature import Feature
from concurrentSpec.src.scenario import Scenario

class TestRegisterConeC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Feature("Register cone C")
        
    def test_work_site_computer_w_registers_cone_c(self):
        Scenario(scenario_name="Register cone C")\
        \
        .Given("work site computer W is operational")\
        .Given("cone C is not yet registered")\
        .When("a registering message from cone C is at the interface")\
        .Then("cone C becomes registered in the work site computer W")\
        .Then("a flashing message from work site computer W is at the interface")\
        .execute()
