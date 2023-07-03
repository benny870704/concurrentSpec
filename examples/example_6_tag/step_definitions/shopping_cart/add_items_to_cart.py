from example_6_tag.src.shopping_cart import ShoppingCart

class AddItemsToCart:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_i_am_on_the_home_page_of_an_online_store(self):
        self.shopping_cart = ShoppingCart()

    def given_i_search_for_the_following_items_(self):
        self.items = []
        for row in self.get_table():
            self.items.append(row["item"])

    def when_i_add_the_items_to_my_cart(self):
        for item in self.items:
            self.shopping_cart.add_item(item)
    
    def then_i_should_see_all_three_items_in_my_cart(self):
        items = self.shopping_cart.get_items()
        assert self.items[0] in items
        assert self.items[1] in items
        assert self.items[2] in items

