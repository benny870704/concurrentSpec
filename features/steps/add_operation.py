class AddOperation:

    def __init__(self):
        pass

    def given_i_have_a_number(self, number1):
        self.number1 = number1

    def given_i_have_another_number(self, number2):
        self.number2 = number2

    def when_i_add_the_two_numbers(self):
        self.result = self.number1 + self.number2

    def then_the_sum_should_be_equal_to(self, answer):
        assert answer == self.result, f"expected: {answer}, got: {self.result}"
    
    def given_i_have_a_set_of_numbers(self, numbers):
        self.numbers = numbers

    def when_i_add_all_the_numbers(self):
        self.result = 0
        for number in self.numbers:
            self.result += number 
    
    def given_i_have_two_numbers(self, number1, number2):
        self.number1 = number1
        self.number2 = number2


