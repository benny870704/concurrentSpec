from example_5_data_table.src.shopping_cart import ShoppingCart

class Checkout:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_i_have_added_the_following_items_to_my_shopping_cart_(self):
        self.shopping_cart = ShoppingCart()
        self.total_price = 0
        for row in self.get_table():
            self.shopping_cart.add_item(row["Item Name"])
            self.total_price += float(row["Price"].replace("$", "")) * int(row["Quantity"])

    def when_i_click_on_the_checkout_button(self):
        pass

    def then_i_should_pay_a_total_of_3_50(self):
        assert self.total_price == 3.5

