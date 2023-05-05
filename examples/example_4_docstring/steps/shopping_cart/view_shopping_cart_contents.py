from example_4_docstring.src.shopping_cart import ShoppingCart

class ViewShoppingCartContents:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_i_am_logged_in_to_the_shopping_website(self):
        pass

    def given_i_am_on_the_shopping_cart_page(self):
        self.shopping_cart = ShoppingCart()

    def given_i_have_two_items_in_my_cart(self):
        self.shopping_cart.add_item("Apple", "Fresh, Red Ruby variety, each weighing about 100g.")
        self.shopping_cart.add_item("Banana", "Fresh, Green variety, each weighing about 150g.")
    
    def when_i_view_my_shopping_cart_contents(self):
        self.items_info = self.shopping_cart.items_info()

    def then_i_should_see_the_following_item_descriptions_(self):
        assert self.items_info == self.text + "\n"


