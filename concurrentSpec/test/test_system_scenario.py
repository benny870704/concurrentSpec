import sys, unittest
sys.path.append("../")
from concurrentSpec.src.feature import FeatureManager
from src.system_scenario import SystemScenario

@unittest.skip("")
class TestSystemScenario(unittest.TestCase):
    def setUp(self):
        self.project_path = "../examples/exploratoryTool/smart_cone_v2/"
        self.system_scenario_name = "Test System Scenario"
        self.system_scenario = SystemScenario(self.system_scenario_name)\
                                .add_project_path(self.project_path)
    
    def tearDown(self):
        FeatureManager.clear()
        
    def test_create_system_scenario_and_add_project_path(self):
        self.assertEqual(self.system_scenario_name, self.system_scenario.get_system_scenario_name())
        self.assertEqual(self.project_path, self.system_scenario.get_project_path())

    def test_select_scenario(self):
        domain_name = "mock_sensor_cone"
        scenario_name = "Turn on cone C"
        self.system_scenario.SelectScenario(domain_name = domain_name, scenario_name = scenario_name)
        
        selected_scenario = self.system_scenario.get_selected_scenario((domain_name, scenario_name))
        
        self.assertEqual(scenario_name, selected_scenario.get_scenario_name())
        self.assertTrue(len(selected_scenario.get_steps()) > 0)
        
    def test_given(self):
        domain_name = "mock_sensor_cone"
        scenario_name = "Turn on cone C"
        self.system_scenario.SelectScenario(domain_name = domain_name, scenario_name = scenario_name)\
                            .Given("cone C is off")
        
        node = self.system_scenario.get_node_from_step_order_tree_node("Given", "cone C is off")
        
        self.assertEqual("Given", node.step.step)
        self.assertEqual("cone C is off", node.step.description)
        
    def test_when(self):
        domain_name = "mock_sensor_cone"
        scenario_name = "Turn on cone C"
        self.system_scenario.SelectScenario(domain_name = domain_name, scenario_name = scenario_name)\
                            .When("the worker turns on cone C")
        
        node = self.system_scenario.get_node_from_step_order_tree_node("When", "the worker turns on cone C")

        self.assertEqual("When", node.step.step)
        self.assertEqual("the worker turns on cone C", node.step.description)
        
    def test_then(self):
        domain_name = "mock_sensor_cone"
        scenario_name = "Turn on cone C"
        self.system_scenario.SelectScenario(domain_name = domain_name, scenario_name = scenario_name)\
                            .Then("a registering message is at the interface I_CW")
        
        node = self.system_scenario.get_node_from_step_order_tree_node("Then", "a registering message is at the interface I_CW")
        
        self.assertEqual("Then", node.step.step)
        self.assertEqual("a registering message is at the interface I_CW", node.step.description)
        
    def test_and(self):
        cone_domain_name = "mock_sensor_cone"
        cone_scenario_name = "Turn on cone C"
        wsc_domain_name = "work_site_computer"
        wsc_scenario_name = "Register cone C"
        
        self.system_scenario.SelectScenario(domain_name = cone_domain_name, scenario_name = cone_scenario_name)\
                            .SelectScenario(domain_name = wsc_domain_name, scenario_name = wsc_scenario_name )\
                            .Given("cone C is off")\
                            .And("work site computer W is operational")\
        
        node = self.system_scenario.get_node_from_step_order_tree_node("Given", "cone C is off")
        and_node = node.children[-1]
        
        self.assertEqual("Given", node.step.step)
        self.assertEqual("cone C is off", node.step.description)
        self.assertEqual("And", and_node.step.step)
        self.assertEqual("work site computer W is operational", and_node.step.description)
        
    def test_but(self):
        cone_domain_name = "mock_sensor_cone"
        cone_scenario_name = "Turn on cone C"
        wsc_domain_name = "work_site_computer"
        wsc_scenario_name = "Register cone C"
        
        self.system_scenario.SelectScenario(domain_name = cone_domain_name, scenario_name = cone_scenario_name)\
                            .SelectScenario(domain_name = wsc_domain_name, scenario_name = wsc_scenario_name )\
                            .Given("cone C is off")\
                            .But("work site computer W is operational")\
        
        node = self.system_scenario.get_node_from_step_order_tree_node("Given", "cone C is off")
        and_node = node.children[-1]
        
        self.assertEqual("Given", node.step.step)
        self.assertEqual("cone C is off", node.step.description)
        self.assertEqual("But", and_node.step.step)
        self.assertEqual("work site computer W is operational", and_node.step.description)
        
    def test_full_structure(self):
        s = SystemScenario(system_scenario_name = "Warning light flashes when cone C is turned on")\
            .add_project_path("../examples/exploratoryTool/smart_cone_v2/")\
            .SelectScenario(domain_name = "mock_sensor_cone", 
                             scenario_name = "Turn on cone C")\
            .SelectScenario(domain_name = "work_site_computer",
                             scenario_name = "Register cone C")\
            .SelectScenario(domain_name = "mock_sensor_cone",
                             scenario_name = "Warning light flashes")\
            .Given("cone C connects to work site computer W at interface I_CW")\
            .Given("cone C is off")\
            .And("work site computer W is operational")\
            .When("the worker turns on cone C")\
            .Then("cone C is operational")\
            .Then("a registering message is at the interface I_CW")\
            .Then("a flashing message is at the interface I_CW")\
            .Then("cone warning light flashes")\
        
        s.print_tree_structure()
    
    def test_execute(self):
        SystemScenario(system_scenario_name = "Warning light flashes when cone C is turned on")\
            .add_project_path("../examples/exploratoryTool/smart_cone_v2/")\
            .SelectScenario(domain_name = "mock_sensor_cone", 
                             scenario_name = "Turn on cone C")\
            .SelectScenario(domain_name = "work_site_computer",
                             scenario_name = "Register cone C")\
            .SelectScenario(domain_name = "mock_sensor_cone",
                             scenario_name = "Warning light flashes")\
            .Given("cone C connects to work site computer W at interface I_CW")\
            .When("the worker turns on cone C")\
            .Then("a registering message is at the interface I_CW")\
            .Then("cone C becomes registered in the work site computer W")\
            .Then("a flashing message is at the interface I_CW")\
            .Then("cone warning light flashes")\
            .execute()
            
            # .Given("cone C is off")\
            # .And("work site computer W is operational")\