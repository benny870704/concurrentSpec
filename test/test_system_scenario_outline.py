import sys, unittest
sys.path.append("../")
from concurrentSpec.src.feature import FeatureManager
from src.system_scenario_outline import SystemScenarioOutline

@unittest.skip("")
class TestSystemScenarioOutline(unittest.TestCase):
    def setUp(self):
        self.project_path = "../examples/exploratoryTool/smart_cone_v2/"
        self.system_scenario_name = "Test System Scenario Outline"
        self.system_scenario = SystemScenarioOutline(self.system_scenario_name)\
                                .add_project_path(self.project_path)
    
    def tearDown(self):
        FeatureManager.clear()
        
    def test_create_system_scenario_and_add_project_path(self):
        self.assertEqual(self.system_scenario_name, self.system_scenario.get_system_scenario_name())
        self.assertEqual(self.project_path, self.system_scenario.get_project_path())
    
    def test_select_scenario_outline(self):
        domain_name = "mock_sensor_cone"
        scenario_name = "Tilt cone C"
        self.system_scenario.SelectScenarioOutline(domain_name = domain_name, scenario_name = scenario_name)
        
        selected_scenario = self.system_scenario.get_selected_scenario((domain_name, scenario_name))
        
        self.assertEqual(scenario_name, selected_scenario.get_scenario_name())
        self.assertTrue(len(selected_scenario.get_steps()) > 0)
        
    def test_given(self):
        domain_name = "mock_sensor_cone"
        scenario_name = "Tilt cone C"
        self.system_scenario.SelectScenario(domain_name = domain_name, scenario_name = scenario_name)\
                            .Given("cone C is operational")
        
        node = self.system_scenario.get_node_from_step_order_tree_node("Given", "cone C is operational")
        
        self.assertEqual("Given", node.step.step)
        self.assertEqual("cone C is operational", node.step.description)
        
    def test_when(self):
        domain_name = "mock_sensor_cone"
        scenario_name = "Tilt cone C"
        self.system_scenario.SelectScenario(domain_name = domain_name, scenario_name = scenario_name)\
                            .When("cone C is tilted <angle> angles")
        
        node = self.system_scenario.get_node_from_step_order_tree_node("When", "cone C is tilted <angle> angles")

        self.assertEqual("When", node.step.step)
        self.assertEqual("cone C is tilted <angle> angles", node.step.description)
    
    def test_then(self):
        domain_name = "mock_sensor_cone"
        scenario_name = "Tilt cone C"
        self.system_scenario.SelectScenario(domain_name = domain_name, scenario_name = scenario_name)\
                            .Then("the acceleration message with <x> <y> <z> is at the interface I_CW")
        
        node = self.system_scenario.get_node_from_step_order_tree_node("Then", "the acceleration message with <x> <y> <z> is at the interface I_CW")
        
        self.assertEqual("Then", node.step.step)
        self.assertEqual("the acceleration message with <x> <y> <z> is at the interface I_CW", node.step.description)
        
    def test_and(self):
        cone_domain_name = "mock_sensor_cone"
        cone_scenario_name = "Tilt cone C"
        wsc_domain_name = "work_site_computer"
        wsc_scenario_name = "Determine cone C state"
        
        self.system_scenario.SelectScenario(domain_name = cone_domain_name, scenario_name = cone_scenario_name)\
                            .SelectScenario(domain_name = wsc_domain_name, scenario_name = wsc_scenario_name )\
                            .Given("cone C is operational")\
                            .And("work site computer W is operational")\
        
        node = self.system_scenario.get_node_from_step_order_tree_node("Given", "cone C is operational")
        and_node = node.children[-1]
        
        self.assertEqual("Given", node.step.step)
        self.assertEqual("cone C is operational", node.step.description)
        self.assertEqual("And", and_node.step.step)
        self.assertEqual("work site computer W is operational", and_node.step.description)
        
    def test_but(self):
        cone_domain_name = "mock_sensor_cone"
        cone_scenario_name = "Tilt cone C"
        wsc_domain_name = "work_site_computer"
        wsc_scenario_name = "Determine cone C state"
        
        self.system_scenario.SelectScenario(domain_name = cone_domain_name, scenario_name = cone_scenario_name)\
                            .SelectScenario(domain_name = wsc_domain_name, scenario_name = wsc_scenario_name )\
                            .Given("cone C is operational")\
                            .But("work site computer W is operational")\
        
        node = self.system_scenario.get_node_from_step_order_tree_node("Given", "cone C is operational")
        and_node = node.children[-1]
        
        self.assertEqual("Given", node.step.step)
        self.assertEqual("cone C is operational", node.step.description)
        self.assertEqual("But", and_node.step.step)
        self.assertEqual("work site computer W is operational", and_node.step.description)
        
    def test_full_structure(self):
        s = SystemScenarioOutline(system_scenario_name = "Warning when cone tilt cone")\
            .add_project_path("../examples/exploratoryTool/smart_cone_v2/")\
            .SelectScenarioOutline(domain_name = "mock_sensor_cone", scenario_name = "Tilt cone C")\
            .SelectScenarioOutline(domain_name = "work_site_computer", scenario_name = "Determine cone C state")\
            .SelectScenarioOutline(domain_name = "mock_sensor_cone", scenario_name = "Change warning light color")\
            .Given("cone C connects to work site computer W at interface I_CW")\
            .Given("cone C is operational")\
            .And("work site computer W is operational")\
            .When("cone C is tilted <angle> angles")\
            .And("the current time is T")\
            .Then("the acceleration message with <x> <y> <z> is at the interface I_CW")\
            .Then("the acceleration is determined as <cone state>")\
            .Then("the response time is in T+0.2")\
            .Then("buzzer is <buzzer state>")\
            .And("the color message with <color> is at the interface I_CW")\
            .Then("the response time is in T+0.3")\
            .Then("warning light is <color>")\
            .Then("the response time is in T+0.5")\
                
        s.print_tree_structure()
        
    def test_with_examples(self):
        SystemScenarioOutline(system_scenario_name = "Warning when cone tilt cone")\
            .add_project_path("../examples/exploratoryTool/smart_cone_v2/")\
            .SelectScenarioOutline(domain_name = "mock_sensor_cone", scenario_name = "Tilt cone C")\
            .SelectScenarioOutline(domain_name = "work_site_computer", scenario_name = "Determine cone C state")\
            .SelectScenarioOutline(domain_name = "mock_sensor_cone", scenario_name = "Change warning light color")\
            .Given("cone C connects to work site computer W at interface I_CW")\
            .Given("cone C is operational")\
            .And("work site computer W is operational")\
            .When("cone C is tilted <angle> angles")\
            .And("the current time is T")\
            .Then("the acceleration message with <x> <y> <z> is at the interface I_CW")\
            .Then("the acceleration is determined as <cone state>")\
            .Then("the response time is in T+0.2")\
            .Then("buzzer is <buzzer state>")\
            .And("the color message with <color> is at the interface I_CW")\
            .Then("the response time is in T+0.3")\
            .Then("warning light is <color>")\
            .Then("the response time is in T+0.5")\
            .WithExamples("""
                |angle|x   |y   |z   |cone state|buzzer state|color |
                |0     |0.00|0.00|1.00|normal    |off         |yellow|
                |30    |0.00|0.53|0.92|normal    |off         |yellow|
                |60    |0.18|1.06|0.61|fallen    |on          |red   |
                |90    |1.00|0.00|0.00|fallen    |on          |red   |
            """)
    
    def test_execute(self):
        SystemScenarioOutline(system_scenario_name = "Warning when tilt cone")\
            .add_project_path("../examples/exploratoryTool/smart_cone_v2/")\
            .SelectScenarioOutline(domain_name = "mock_sensor_cone", scenario_name = "Tilt cone C")\
            .SelectScenarioOutline(domain_name = "work_site_computer", scenario_name = "Determine cone C state")\
            .SelectScenarioOutline(domain_name = "mock_sensor_cone", scenario_name = "Change warning light color")\
            .Given("cone C connects to work site computer W at interface I_CW")\
            .Given("cone C is operational")\
            .And("work site computer W is operational")\
            .When("cone C is tilted <angle> angles")\
            .And("the current time is T")\
            .Then("the acceleration message with x: <x> y: <y> z: <z> is at the interface I_CW")\
            .Then("the acceleration is determined as <cone state>")\
            .Then("the response time is in T+0.2")\
            .Then("buzzer is <buzzer state>")\
            .And("the color message with <color> is at the interface I_CW")\
            .Then("the response time is in T+0.3")\
            .Then("warning light is <color>")\
            .Then("the response time is in T+0.5")\
            .WithExamples("""
                |angle|x   |y   |z   |cone state|buzzer state|color |
                |0     |0.00|0.00|1.00|normal    |mute       |yellow|
                |30    |0.00|0.53|0.92|normal    |mute       |yellow|
                |60    |0.18|1.06|0.61|fallen    |warning    |red   |
                |90    |1.00|0.00|0.00|fallen    |warning    |red   |
            """)\
            .execute()
            
    def test_execute_and_skip_low_level_step_when_example_not_match(self):
        SystemScenarioOutline(system_scenario_name = "Warning when tilt cone")\
            .add_project_path("../examples/exploratoryTool/smart_cone_v2/")\
            .SelectScenarioOutline(domain_name = "mock_sensor_cone", scenario_name = "Tilt cone C")\
            .SelectScenarioOutline(domain_name = "work_site_computer", scenario_name = "Determine cone C state")\
            .SelectScenarioOutline(domain_name = "mock_sensor_cone", scenario_name = "Change warning light color")\
            .Given("cone C connects to work site computer W at interface I_CW")\
            .When("cone C is tilted <angle> angles")\
            .And("the current time is T")\
            .Then("the acceleration message with x: <x> y: <y> z: <z> is at the interface I_CW")\
            .Then("the response time is in T+0.2")\
            .Then("buzzer is <buzzer state>")\
            .And("the color message with <color> is at the interface I_CW")\
            .Then("the response time is in T+0.3")\
            .Then("warning light is <color>")\
            .Then("the response time is in T+0.5")\
            .WithExamples("""
                |angle|x   |y   |z   |buzzer state|color |
                |0     |0.00|0.00|1.00|mute       |yellow|
                |30    |0.00|0.53|0.92|mute       |yellow|
                |60    |0.18|1.06|0.61|warning    |red   |
                |90    |1.00|0.00|0.00|warning    |red   |
            """)\
            .execute()
            
            # .Given("cone C is operational")\
            # .And("work site computer W is operational")\