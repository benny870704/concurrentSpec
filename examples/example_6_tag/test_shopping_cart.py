import sys
import unittest
sys.path.append("../../")
from src.tag import tag
from src.feature import Feature
from src.scenario import Scenario

@tag("shopping_cart")
class TestShoppingCart(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Feature("Shopping cart",
        """
        As a user
        I want be able to add items to a shopping cart
        So that I can buy whatever I want
        """)

    @tag("item")
    def test_add_item_to_cart(self):
        Scenario("Add items to cart")\
        \
        .Given("I am on the home page of an online store")\
        .And("I search for the following items:", """
            |  item  |
            | apple  |
            | orange |
            | banana |
        """)\
        .When("I add the items to my cart")\
        .Then("I should see all three items in my cart")\
        .execute()

    @tag("item")
    @tag("wip")
    def test_remove_item_from_cart(self):
        Scenario("Remove item from cart")\
        \
        .Given("I am on the home page of an online store")\
        .And("I have the following items in my cart:", """
            |  item  |
            | apple  |
            | orange |
            | banana |
        """)\
        .When("I removed the <orange> from my cart")\
        .Then("I should see only two items in my cart")\
        .execute()

if __name__ == '__main__':
    unittest.main()