import sys
import unittest
sys.path.append("../../../")
from concurrentSpec.src.feature import Feature
from concurrentSpec.src.scenario import Scenario
from concurrentSpec.src.background import Background

class TestViewCartItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Feature("View Cart Items")
        Background()\
        .Given("I am a registered user of a shopping cart application")\
        .And("I have logged into my account")\
        
    def test_empty_cart(self):
        Scenario("Empty Cart")\
        .Given("the shopping cart is empty")\
        .When("I navigate to the cart page")\
        .Then("I should see a message indicating that the cart is empty")

if __name__ == '__main__':
    unittest.main()