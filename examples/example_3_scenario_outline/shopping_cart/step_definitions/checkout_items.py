class CheckoutItems:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_there_are_stock_count_items_of_a_product_left_in_stock(self, stock_count:int):
        self.stock_count = stock_count

    def given_i_have_added_some_items_of_it_in_my_cart(self, some:int):
        self.added_count = some

    def when_i_click_on_the_checkout_button(self):
        self.checkout_message = ""
        if self.added_count > self.stock_count:
            self.checkout_message = "Not enough stock"
        else:
            self.checkout_message = "Checkout successful"
            self.stock_count -= self.added_count

    def then_i_should_see_the_message_message_(self, message:str):
        assert message == self.checkout_message

    def then_the_product_now_only_has_remaining_items_left_in_stock(self, remaining:int):
        assert remaining == self.stock_count

