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
        I want view my shopping cart contents
        So that I can see the items I want to purchase
        """)

    def test_view_shopping_cart_contents(self):
        Scenario("View shopping cart contents")\
        .Given("I am logged in to the shopping website")\
        .Given("I am on the shopping cart page")\
        .And("I have two items in my cart")\
        .When("I view my shopping cart contents")\
        .Then("I should see the following item descriptions:", """
            Apple: Fresh, Red Ruby variety, each weighing about 100g.
            Banana: Fresh, Green variety, each weighing about 150g.
        """).execute()

if __name__ == '__main__':
    unittest.main()