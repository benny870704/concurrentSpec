import unittest
import sys
sys.path.append("../")
from src.scenario import Scenario

class TestScheduledSprinklingWithSimulation(unittest.TestCase):
    
    def test_scheduled_sprinkling(self):
        Scenario("scheduled sprinkling with simulation")\
        .Given("three sprinklers A, B, and C")\
        .Given("the scheduled time is set to 4:00:00 am")\
        .When("the time is 4:00:00 am")\
        .Then("sprinkler A should emit water within 5 seconds")\
        .And("sprinkler B should emit water within 5 seconds")\
        .And("sprinkler C should emit water within 5 seconds")\
        .execute()

if __name__ == '__main__':
    unittest.main()