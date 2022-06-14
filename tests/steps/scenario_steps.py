class ScenarioSteps:

    def __init__(self):
        pass

    def given_process_a_is_running_at_8_00_am(self):
        raise NotImplementedError('given_process_a_is_running_at_8_00_am')

    def given_process_b_is_running(self):
        raise NotImplementedError('given_process_b_is_running')

    def then_some_outcomes(self):
        raise NotImplementedError('then_some_outcomes')

    def when_something_happens(self):
        raise NotImplementedError('when_something_happens')

    def given_a_precondition(self):
        raise NotImplementedError('given_a_precondition')

