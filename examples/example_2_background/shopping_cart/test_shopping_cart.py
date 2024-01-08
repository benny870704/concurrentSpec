import sys
import unittest
sys.path.append("../../../")
from concurrentSpec.src.feature import Feature
from concurrentSpec.src.scenario import Scenario
from concurrentSpec.src.background import Background

class TestShoppingCart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Feature("Shopping cart",
        """
        As a customer
        I want be able to add or remove items from my shopping cart
        So that I can decide what I want to buy
        """)
        Background()\
        .Given("I am on the home page of an online store")\
        .Given("I have two items in my cart")\

    def test_put_item_to_cart(self):
        Scenario("Put item to cart")\
        \
        .When("I put an item to my cart")\
        .Then("I should see three items in my cart")\
        .execute()

    def test_remove_item_from_cart(self):
        Scenario("Remove item from cart")\
        \
        .When("I removed an item from my cart")\
        .Then("I should see only one item in my cart")\
        .execute()

    # def test_remove_item_from_cart(self):
    #     Scenario("Remove item from cart")\
    #     \
    #     .When("I removed two item from my cart")\
    #     .Then("I should see only zero item in my cart")\
    #     .execute()

if __name__ == '__main__':
    unittest.main()