# concurrentSpec

![example workflow](https://github.com/benny870704/concurrentSpec/actions/workflows/tests.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Welcome to `concurrentSpec`, a Python-based Behavior-Driven Development (BDD) tool developed to support the execution of concurrent steps.

## Section
- [Installation](#installation)
- [Scenario Usage](#scenario-usage)
- [Running Example Scenario Without Installation](#running-example-scenario-without-installation)
- [Running Example Scenarios of Showing Features](#running-example-scenarios-of-showing-features)
- [Concurrency](#concurrency)
- [Keyword Arguments](#keyword-arguments)
- [Continue After Failure](#continue-after-failure)
- [System Scenario](#system-scenario)

### Installation
Download the latest [release]() and install it.
```shell
pip install concurrentSpec-${VERSION}.tar.gz
```

### Scenario Usage
Create a directory called "features/scheduled_sprinkling", and create a file called "test_scheduled_sprinkling.py" in that directory.

```python
# FILE: features/scheduled_sprinkling/test_scheduled_sprinkling.py
import unittest
from concurrentSpec import Feature, Scenario

class TestScheduledSprinkling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Feature("Scheduled Sprinkling")
    
    def test_scheduled_sprinkling(self):
        Scenario("scheduled sprinkling")\
        .Given("three sprinklers A, B, and C")\
        .Given("the scheduled time is set to 4:00:00 am")\
        .When("the time is 4:00:00 am")\
        .Then("sprinkler A should emit water within 5 seconds")\
        .And("sprinkler B should emit water within 5 seconds")\
        .And("sprinkler C should emit water within 5 seconds")\
        .execute()
```

Run concurrentSpec:
```shell
$ cd features/
$ concurrentSpec
```

After running, the following file were generated automatically:
```python
# FILE: features/scheduled_sprinkling/step_definitions/scheduled_sprinkling.py
class ScheduledSprinkling:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_three_sprinklers_a_b_and_c(self):
        raise NotImplementedError('given_three_sprinklers_a_b_and_c')

    def given_the_scheduled_time_is_set_to_4_00_00_am(self):
        raise NotImplementedError('given_the_scheduled_time_is_set_to_4_00_00_am')

    def when_the_time_is_4_00_00_am(self):
        raise NotImplementedError('when_the_time_is_4_00_00_am')

    def then_sprinkler_a_should_emit_water_within_5_seconds(self):
        raise NotImplementedError('then_sprinkler_a_should_emit_water_within_5_seconds')

    def then_sprinkler_b_should_emit_water_within_5_seconds(self):
        raise NotImplementedError('then_sprinkler_b_should_emit_water_within_5_seconds')

    def then_sprinkler_c_should_emit_water_within_5_seconds(self):
        raise NotImplementedError('then_sprinkler_c_should_emit_water_within_5_seconds')
```

Replace `NotImplementedError` to `pass` and run again:
```
Feature: Scheduled Sprinkling

  Scenario: scheduled sprinkling
    Given three sprinklers A, B, and C
    Given the scheduled time is set to 4:00:00 am
    When the time is 4:00:00 am
    Then sprinkler A should emit water within 5 seconds
    And sprinkler B should emit water within 5 seconds
    And sprinkler C should emit water within 5 seconds

1 feature    : Passed 1, Failed 0
1 scenario   : Passed 1, Failed 0
6 steps      : Passed 6, Failed 0, Skipped 0, Undefined 0
```

### Running Example Scenario Without Installation
Download this repository, open terminal and change directory to where the repository is.
- `cd features/`
    - run `python3 test_scheduled_sprinkling.py` for sprinkler example
    - run `python3 test_lift_emergency.py` for lift example
    - run `python3 -m unittest` to see all examples


### Running Example Scenarios of Showing Features
Download this repository, open terminal and change directory to where the repository is.
```shell
$ cd {repository_location}/examples/
```

There are 6 examples showing features of concurrentSpec.
```shell
# Feature
$ concurrentSpec -p example_1_feature/

# Background
$ concurrentSpec -p example_2_background/

# Scenario Outline
$ concurrentSpec -p example_3_scenario_outline/

# Docstring
$ concurrentSpec -p example_4_docstring/

# Data Table
$ concurrentSpec -p example_5_data_table/

# Tag with Tag Expressions v2
$ concurrentSpec -p example_6_tag/ -t "item and wip"
```

### Concurrency
As the example in the section [Scenario Usage](#scenario-usage), we want to verify three sprinklers emitting water at the same time instead of step by step. In `concurrentSpec`, we can use `And` or `But` as concurrent steps.



### Notes
- Each scenario can be written under the Python `unittest` framework
- Remember to include `scenario` depending on the location
- The example can be found in `features` folder
- The default step definition will generate to the path `<your_execution_path>/steps/<scenario_name>.py`
  - It can give custom step definition file path in scenario initialization by `step_path=<path>`
    ```python 
    Scenario("add operation", step_path="./add_operation_steps/")
    ```

- Scenario Example:
    ```python
    class TestScheduledSprinkling(unittest.TestCase):
    
    def test_scheduled_sprinkling(self):
        Scenario("scheduled sprinkling")\
        .Given("three sprinklers A, B, and C")\
        .Given("the scheduled time is set to 4:00:00 am")\
        .When("the time is 4:00:00 am")\
        .Then("sprinkler A should emit water within 5 seconds")\
        .And("sprinkler B should emit water within 5 seconds")\
        .And("sprinkler C should emit water within 5 seconds")\
        .execute()
    ```
  - `Scenario("scheduled sprinkling")`: scenario initialization and scenario name
  - `Given()`, `When()`, `Then()`, `And()`, `But()`: step definition in the scenario
  - `execute()`: execute the scenario
  - default step definition ```<your_execution_path>/steps/<scenario_name>.py)```:
    ```python
    class ScheduledSprinkling:

      def __init__(self):
          pass

      def given_three_sprinklers_a_b_and_c(self):
          raise NotImplementedError('given_three_sprinklers_a_b_and_c')

      def given_the_scheduled_time_is_set_to_4_00_00_am(self):
          raise NotImplementedError('given_the_scheduled_time_is_set_to_4_00_00_am')

      def when_the_time_is_4_00_00_am(self):
          raise NotImplementedError('when_the_time_is_4_00_00_am')

      def then_sprinkler_a_should_emit_water_within_5_seconds(self):
          raise NotImplementedError('then_sprinkler_a_should_emit_water_within_5_seconds')

      def then_sprinkler_b_should_emit_water_within_5_seconds(self):
          raise NotImplementedError('then_sprinkler_b_should_emit_water_within_5_seconds')

      def then_sprinkler_c_should_emit_water_within_5_seconds(self):
          raise NotImplementedError('then_sprinkler_c_should_emit_water_within_5_seconds')
    ```

### Keyword Arguments
- Each step can give keyword arguments
  - Example:
    ```python
    Scenario("add operation")\
    .Given("I have two numbers", number1=3, number2=4)\
    .When("I add the two numbers")\
    .Then("The sum should be equal to", answer=7)\
    .execute()
    ```

    > **Warning**
    > 
    > It can not give arguments without keyword
    > 
    > Example:
    >   ```python
    >  Scenario("add operation")\
    >  .Given("I have two numbers", 3, 4)
    >  ```

    - Step Definition:
    ```python
    class AddOperation:

    def __init__(self):
        pass

    def given_i_have_two_numbers(self, number1, number2):
        raise NotImplementedError('given_i_have_two_numbers')

    def when_i_add_the_two_numbers(self):
        raise NotImplementedError('when_i_add_the_two_numbers')

    def then_the_sum_should_be_equal_to(self, answer):
        raise NotImplementedError('then_the_sum_should_be_equal_to')
        
    ```

### Continue After Failure 
- The default value of `continue_after_failure` is `False`.
- Only steps in **Then** group can set `continue_after_failure` as `True`; otherwise it will be ignored.
- If `continue_after_failure` is `true`, the scenario will continue the execution no matter the step failed or not.
    - Example:
    ```python
    Scenario("emergency braking and warning over normal requests")\
    .Given("an outstanding request for lift to visit a floor")\
    .When("an emergency has been detected")\
    .Then("lift is stopped at nearest floor in direction of travel")\
    .And("emergency indicator should be turned on", continue_after_failure=True)\
    .And("request should be canceled", continue_after_failure=True)\
    .Then("lift doors should be open within 5 seconds")\
    .execute()
    ```

## System Scenario
- Run Example: 
  - `cd examples/example_7_system_scenario/system`
  - `python3 -m unittest`