from src.shopping_cart import ShoppingCart

class Background:

    def set_up(self):
        pass

    def given_i_am_on_the_home_page_of_an_online_store(self):
        self.shopping_cart = ShoppingCart()

    def given_i_search_for_the_following_items_(self):
        self.items = []
        for row in self.table:
            self.items.append(row["item"])

    def given_i_add_the_items_to_my_cart(self):
        for item in self.items:
            self.shopping_cart.add_item(item)

