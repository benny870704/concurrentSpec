import unittest
import sys
sys.path.append("../")
from src.scenario import Scenario

class TestArgument(unittest.TestCase):

    def test_give_argument(self):
        scenario = Scenario("add operation")

        scenario.Given("I have a number", number1=1)\
                .execute()

    def test_use_argument(self):
        scenario = Scenario("add operation")

        scenario.Given("I have a number", number1=1)\
                .And("I have another number", number2=2)\
                \
                .When("I add the two numbers")\
                \
                .Then("The sum should be equal to", answer=3)\
                .execute()

    def test_list_argument(self):
        scenario = Scenario("add operation")

        scenario.Given("I have a set of numbers", numbers=[1, 2, 3, 4])\
                \
                .When("I add all the numbers")\
                \
                .Then("The sum should be equal to", answer=10)\
                .execute()

    def test_multiple_keyword_arguments_at_one_step(self):
        scenario = Scenario("add operation")

        scenario.Given("I have two numbers", number1=3, number2=4)\
                \
                .When("I add the two numbers")\
                \
                .Then("The sum should be equal to", answer=7)\
                .execute()

        

if __name__ == '__main__':
    unittest.main()
    