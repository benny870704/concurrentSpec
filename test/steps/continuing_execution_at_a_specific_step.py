class ContinuingExecutionAtASpecificStep:

    def __init__(self):
        pass

    def given_some_precondition(self):
        pass

    def when_an_event_happens(self):
        pass

    def then_the_step_is_true(self):
        assert True

    def then_the_step_fails_but_it_adds_a_tag_to_continue_execution(self):
        assert False

    def then_the_step_should_be_executed_and_it_fails(self):
        assert False

