from shopping_cart import ShoppingCart

class ViewShoppingCartContents:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    # def given_i_have_two_items_in_my_cart(self):
    #     self.shopping_cart = ShoppingCart()
    #     self.shopping_cart.add_item("Apple", "Fresh, Red Ruby variety, each weighing about 100g.")
    #     self.shopping_cart.add_item("Banana", "Fresh, Green variety, each weighing about 150g.")

    def given_i_have_the_following_two_items_in_my_cart_(self):
        self.shopping_cart = ShoppingCart()
        for row in self.get_table():
            self.shopping_cart.add_item(row["item"], row["description"])
    
    def when_i_view_my_shopping_cart_contents(self):
        self.items_info = self.shopping_cart.items_info()

    def then_i_should_see_the_following_item_descriptions_(self):
        assert self.items_info == self.get_text() + "\n"

