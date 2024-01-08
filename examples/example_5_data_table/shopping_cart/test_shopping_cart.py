import unittest
from concurrentSpec.src.feature import Feature
from concurrentSpec.src.scenario import Scenario

class TestShoppingCart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Feature("Shopping Cart",
        """
        As a user
        I want to summarize my shopping cart contents
        So that I can know how much I should pay
        """)

    def test_checkout_shopping_cart(self):
        Scenario("Checkout shopping cart")\
        .Given("I have added the following items to my shopping cart:", """
            | Item Name | Price | Quantity |
            | Apple     | $1.00 | 2        |
            | Banana    | $0.50 | 3        |
        """)\
        .When("I click on the checkout button")\
        .Then("I should pay a total of $3.50")\
        .execute()

    def test_checkout_shopping_cart_with_coupons(self):
        Scenario("Checkout with a coupon")\
        .Given("I have added the following items to my shopping cart:", """
            | Item Name | Price | Quantity |
            | Apple     | $1.00 | 2        |
            | Banana    | $0.50 | 3        |
        """)\
        .And("the shopping cart has the following coupons:", """
            | Coupon Code | Discount Amount |
            | ABC123      | $2              |
            | DEF456      | $3              |
        """)\
        .When("I use the cheapest coupon")\
        .Then("I should pay a total of $1.5")\
        # .execute()

if __name__ == '__main__':
    unittest.main()