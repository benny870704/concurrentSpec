class AddItemToCart:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def when_i_add_an_item_to_my_cart(self):
        self.shopping_cart.add_item("guava")
    
    def then_i_should_see_three_items_in_my_cart(self):
        assert 3 == self.shopping_cart.get_items_count()

