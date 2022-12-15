import unittest
import sys
sys.path.append("../")
from src.scenario import Scenario

class TestLiftEmergency(unittest.TestCase):

    def test_lift_emergency(self):
        scenario = Scenario("emergency braking and warning over normal requests")
        
        scenario.Given("an outstanding request for the lift to visit a floor")\
                .When("an emergency has been detected")\
                .Then("the lift is stopped at the nearest floor in the direction of travel")\
                .And("the emergency indicator should be turned on", continue_after_failure=True)\
                .And("the request should be canceled", continue_after_failure=True)\
                .Then("the lift doors should be open within 5 seconds")\
                .execute()

if __name__ == '__main__':
    unittest.main()