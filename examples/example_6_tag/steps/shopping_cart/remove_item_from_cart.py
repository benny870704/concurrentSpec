from example_6_tag.src.shopping_cart import ShoppingCart

class RemoveItemFromCart:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_i_am_on_the_home_page_of_an_online_store(self):
        self.shopping_cart = ShoppingCart()
    
    def given_i_have_the_following_items_in_my_cart_(self):
        for row in self.table:
            self.shopping_cart.add_item(row["item"])

    def when_i_removed_the_orange_from_my_cart(self):
        self.shopping_cart.remove_item("orange")

    def then_i_should_see_only_two_items_in_my_cart(self):
        assert 2 == self.shopping_cart.get_items_count()

