import sys
import unittest
sys.path.append("../../")
from src.feature import Feature
from src.scenario import Scenario
from src.background import Background

class TestShoppingCart(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Feature("Shopping cart")
        Background()\
        .Given("I am on the home page of an online store")\
        .Given("I have two items in my cart")\

    def test_add_item_to_cart(self):
        Scenario("Add item to cart")\
        \
        .When("I add an item to my cart")\
        .Then("I should see three items in my cart")\
        .execute()

    def test_remove_item_from_cart(self):
        Scenario("Remove item from cart")\
        \
        .When("I removed an item from my cart")\
        .Then("I should see only one item in my cart")\
        .execute()

if __name__ == '__main__':
    unittest.main()