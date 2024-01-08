import unittest
from concurrentSpec.src.feature import Feature
from concurrentSpec.src.scenario import Scenario
from concurrentSpec.src.scenario_outline import ScenarioOutline
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
        ScenarioOutline("Remove item from cart")\
        \
        .Given("I am on the home page of an online store")\
        .Given("I have two items in my cart")\
        .When("I remove <some> items from my cart")\
        .Then("I should see <remaining> items in my cart")\
        .WithExamples("item count", """
            | some | remaining |
            | 2    | 0         |
        """)\
        .WithExamples("item count 2", """
            | some | remaining |
            | 1    | 1         |
        """)\
        .execute()

    def test_checkout_items(self):
        ScenarioOutline("Checkout items")\
        \
        .Given("There are <stock count> items of a product left in stock")\
        .And("I have added <some> items of it in my cart")\
        .When("I click on the checkout button")\
        .Then("I should see the message '<message>'")\
        .And("The product now only has <remaining> items left in stock")\
        .WithExamples("""
            | stock count | some |        message      | remaining |
            | 2           | 3    | Not enough stock    | 2         |
            | 1           | 1    | Checkout successful | 0         |
        """)\
        .execute()

if __name__ == '__main__':
    unittest.main()