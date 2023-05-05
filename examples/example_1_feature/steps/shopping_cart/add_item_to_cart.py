from example_1_feature.src.shopping_cart import ShoppingCart

class AddItemToCart:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_i_am_on_the_home_page_of_an_online_store(self):
        self.shopping_cart = ShoppingCart()

    def given_i_have_two_items_in_my_cart(self):
        self.shopping_cart.add_item("apple")
        self.shopping_cart.add_item("banana")

    def when_i_add_an_item_to_my_cart(self):
        self.shopping_cart.add_item("guava")
    
    def then_i_should_see_three_items_in_my_cart(self):
        assert 3 == self.shopping_cart.get_items_count()

