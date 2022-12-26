import unittest
import sys
sys.path.append("../")
from src.scenario import Scenario

class TestLiftEmergency(unittest.TestCase):

    def test_lift_emergency(self):
        Scenario("emergency braking and warning over normal requests")\
        .Given("an outstanding request for lift to visit a floor")\
        .When("an emergency has been detected")\
        .Then("lift is stopped at nearest floor in direction of travel")\
        .And("emergency indicator should be turned on", continue_after_failure=True)\
        .And("request should be canceled", continue_after_failure=True)\
        .Then("lift doors should be open within 5 seconds")\
        .execute()

if __name__ == '__main__':
    unittest.main()