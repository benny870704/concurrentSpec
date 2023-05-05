class TearDownShouldBeExecuted:

    def given_a_web_browser_is_on_the_google_page(self):
        pass

    def when_the_search_phrase_panda_is_entered(self):
        pass

    def then_results_for_panda_are_shown(self):
        pass
    
    def then_results_for_capybara_are_shown(self):
        raise Exception("Capybara Not Exist")
    
    def tear_down(self):
        print("Tear Down Executed")

