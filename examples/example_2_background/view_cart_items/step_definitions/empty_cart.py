class EmptyCart:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_the_shopping_cart_is_empty(self):
        raise NotImplementedError("given_the_shopping_cart_is_empty")

    def when_i_navigate_to_the_cart_page(self):
        raise NotImplementedError("when_i_navigate_to_the_cart_page")

    def then_i_should_see_a_message_indicating_that_the_cart_is_empty(self):
        raise NotImplementedError("then_i_should_see_a_message_indicating_that_the_cart_is_empty")

