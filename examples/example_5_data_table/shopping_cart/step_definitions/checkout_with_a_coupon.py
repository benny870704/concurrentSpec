from shopping_cart import ShoppingCart

class CheckoutWithACoupon:

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
    
    def given_the_shopping_cart_has_the_following_coupons_(self):
        self.discount = []
        for row in self.get_table():
            discount_amount = float(row["Discount Amount"].replace("$", ""))
            self.discount.append(discount_amount)

    def when_i_use_the_cheapest_coupon(self):
        self.total_price -= min(self.discount)

    def then_i_should_pay_a_total_of_1_5(self):
        assert self.total_price == 1.5

