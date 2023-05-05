import sys
import unittest
sys.path.append("../../")
from src.feature import Feature
from src.scenario import Scenario

class TestShoppingCart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Feature("Shopping Cart",
        """
        As a user
        I want to summarize my shopping cart contents
        So that I can know how much I should pay
        """)

    def test_view_shopping_cart_contents(self):
        Scenario("Checkout")\
        .Given("I have added the following items to my shopping cart:", """
            | Item Name | Price | Quantity |
            | Apple     | $1.00 | 2        |
            | Banana    | $0.50 | 3        |
        """)\
        .When("I click on the checkout button")\
        .Then("I should pay a total of $3.50")\
        .execute()

if __name__ == '__main__':
    unittest.main()