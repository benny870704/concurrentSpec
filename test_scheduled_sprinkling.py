import unittest
from scenario import Scenario

class TestScheduledSprinkling(unittest.TestCase):
    def test_sprinklers(self):
        scenario = Scenario("scheduled sprinkling")

        scenario.Given("water supply is normal")\
                .And("timer is set to 4:00:00 am")\
                \
                .When("the time is 4:00:00 am")\
                \
                .Then("sprinkler A emits water no later than 4:00:05 am")\
                .And("sprinkler B emits water no later than 4:00:05 am")\
                .And("sprinkler C emits water no later than 4:00:05 am")\
                .execute()

if __name__ == '__main__':
    unittest.main()
    