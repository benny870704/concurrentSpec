from shopping_cart import ShoppingCart

class Background:
    
    def given_i_am_on_the_home_page_of_an_online_store(self):
        self.shopping_cart = ShoppingCart()

    def given_i_have_two_items_in_my_cart(self):
        self.shopping_cart.add_item("apple")
        self.shopping_cart.add_item("banana")

