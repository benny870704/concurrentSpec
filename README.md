# concurrentSpec
- put `scenario.py` in your project folder

## Scenario Usage
- Each scenario can be written under the Python `unittest` framework
- Remember to include `scenario` depending on the location you put
- Example:
    ```python
    class TestScheduledSprinkling(unittest.TestCase):
        
        def test_scheduled_sprinkling(self):
            scenario = Scenario("scheduled sprinkling")

            scenario.Given("water supply is normal")\
                    .And("timer is set to 4:00:00 am")\
                    \
                    .When("the time is 4:00:00 am")\
                    \
                    .Then("sprinkler A emits water no later than 4:00:05 am")\
                    .And("sprinkler B emits water no later than 4:00:05 am")\
                    .And("sprinkler C emits water no later than 4:00:05 am")\
                    .execute()
    ```
  - `scenario = Scenario("scheduled sprinkling")`: scenario initialization and scenario name
  - `Given()`, `When()`, `Then()`, `And()`, `But()`: step definition in the scenario
  - `execute()`: execute the scenario

- The example can be found in `features` folder
- To execute the example, type `cd features/`, `python -m unittest`
- The default step definition will generate to the path `<your_execution_path>/steps/<scenario_name>Steps.py`