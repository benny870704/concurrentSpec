# concurrentSpec
- put `scenario.py` in your project folder

## Scenario Usage
- Each scenario can be written under the Python `unittest` framework
- Remember to include `scenario` depending on the location
- The example can be found in `features` folder
- To execute the example, command `cd features`, `python -m unittest`
- The default step definition will generate to the path `<your_execution_path>/steps/<scenario_name>Steps.py`
  - It can give custom step definition file path in scenario initialization by `step_path=<path>`
    ```python 
    scenario = Scenario("add operation", step_path="./add_operation_steps/")
    ```

- Scenario Example:
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
  - default step definition ```<your_execution_path>/steps/<scenario_name>Steps.py)```:
    ```python
    class ScheduledSprinklingSteps:

      def __init__(self):
          pass

      def given_water_supply_is_normal(self):
          raise NotImplementedError('given_water_supply_is_normal')

      def given_timer_is_set_to_4_00_00_am(self):
          raise NotImplementedError('given_timer_is_set_to_4_00_00_am')

      def when_the_time_is_4_00_00_am(self):
          raise NotImplementedError('when_the_time_is_4_00_00_am')

      def then_sprinkler_a_emits_water_no_later_than_4_00_05_am(self):
          raise NotImplementedError('then_sprinkler_a_emits_water_no_later_than_4_00_05_am')

      def then_sprinkler_b_emits_water_no_later_than_4_00_05_am(self):
          raise NotImplementedError('then_sprinkler_b_emits_water_no_later_than_4_00_05_am')

      def then_sprinkler_c_emits_water_no_later_than_4_00_05_am(self):
          raise NotImplementedError('then_sprinkler_c_emits_water_no_later_than_4_00_05_am')
    ```

- Each step can give keyword arguments
  - Example:
    ```python
    scenario = Scenario("add operation")

    scenario.Given("I have two numbers", number1=3, number2=4)\
            \
            .When("I add the two numbers")\
            \
            .Then("The sum should be equal to", answer=7)\
            .execute()
    ```

    > **Warning**
    > 
    > It can not give arguments without keyword
    > 
    > Example:
    >   ```python
    >  scenario = Scenario("add operation")
    >
    >  scenario.Given("I have two numbers", 3, 4)
    >  ```

    - Step Definition:
    ```python
    class AddOperationSteps:

    def __init__(self):
        pass

    def given_i_have_two_numbers(self, number1, number2):
        raise NotImplementedError('given_i_have_two_numbers')

    def when_i_add_the_two_numbers(self):
        raise NotImplementedError('when_i_add_the_two_numbers')

    def then_the_sum_should_be_equal_to(self, answer):
        raise NotImplementedError('then_the_sum_should_be_equal_to')
        
    ```