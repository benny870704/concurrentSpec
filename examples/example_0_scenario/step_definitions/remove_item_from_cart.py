from src.shopping_cart import ShoppingCart

class RemoveItemFromCart:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_i_am_on_the_home_page_of_an_online_store(self):
        self.shopping_cart = ShoppingCart()

    def given_i_have_two_items_in_my_cart(self):
        self.shopping_cart.add_item("apple")
        self.shopping_cart.add_item("banana")

    def when_i_removed_an_item_from_my_cart(self):
        self.shopping_cart.remove_item("apple")

    def then_i_should_see_only_one_item_in_my_cart(self):
        assert 1 == self.shopping_cart.get_items_count()

