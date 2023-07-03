import re
import os, pathlib
from ..status import Status
from ..feature import FeatureManager
from ..scenario_outline import ScenarioOutline

# PASSED_SYMBOL = "✔️"
PASSED_SYMBOL = "✅"
FAILED_SYMBOL = "❌"
UNTESTED_SYMBOL = "⏹"
UNDEFINED_SYMBOL = "❓"

OUTPUT_FILE = "test_result/test_result.html"

def generate_test_result_in_html(output_file=None):
    print("generating html test result...")
    style = pathlib.Path(f"{os.path.dirname(__file__)}/test_result_html.css").read_text()
    template = pathlib.Path(os.path.join(os.path.dirname(__file__), "test_result_template.html")).read_text()
    template = re.sub(r'(?<=\n)\s*{{styles}}', style, template)
    template = re.sub(r'(?<=\n)\s*{{bar}}', add_bar(), template)
    template = re.sub(r'(?<=\n)\s*{{features_table}}', add_result_table(), template)
    template = re.sub(r'(?<=\n)\s*{{features}}', add_features(), template)
    
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(template)
    else:
        os.makedirs(f'test_result/', exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            f.write(template)
    print("done!")

def spaces(count):
    spaces = [" "]*count
    return "".join(spaces)

def encode_angle_brackets(string):
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    return string

def get_status_symbol(execution_result):
    if execution_result == Status.passed: return PASSED_SYMBOL
    elif execution_result == Status.failed: return FAILED_SYMBOL
    elif execution_result == Status.undefined: return UNDEFINED_SYMBOL
    elif execution_result == Status.untested: return UNTESTED_SYMBOL

def add_bar():
    passed_scenario_count = 0
    all_scenario_count = 0
    for feature_name, feature in FeatureManager.get_features().items():
        all_scenario_count += len(feature["scenarios"])
        for scenario in feature["scenarios"]:
            if scenario.execution_result == Status.passed: passed_scenario_count += 1

    passed_percent = round(round(passed_scenario_count/all_scenario_count, 2)*100)
    bar_text = f"""
      <div id="bar">
        <div class="green" style="width: {passed_percent}%;"></div>
        <div class="center-text green-center">{passed_scenario_count} PASSED</div>
        <div class="center-text red-center">{all_scenario_count - passed_scenario_count} FAILED</div>
      </div>

      <script>
        var greenPercent = {passed_percent};
        var greenCenterDiv = document.querySelector('.green-center');
        greenPercent > 0 ? greenCenterDiv.style.left = greenPercent/2 + '%' : greenCenterDiv.style.display = "none"
    
        var redPercent = 100 + greenPercent;
        var redCenterDiv = document.querySelector('.red-center');
        redPercent > 0 && greenPercent != 100 ? redCenterDiv.style.left = redPercent/2 + "%" : redCenterDiv.style.display = "none"
      </script>
    """
    
    return bar_text

def add_result_table():
    result_table = ""
    feature_id_count = 1
    for feature_name, feature in FeatureManager.get_features().items():
        scenario_count = len(feature["scenarios"])
        passed_scenario_count = 0
        for scenario in feature["scenarios"]:
            if scenario.execution_result == Status.passed: passed_scenario_count += 1

        result_table += add_table_raw(table_data = [feature_name, scenario_count, passed_scenario_count, scenario_count - passed_scenario_count], feature_id_count=feature_id_count)
        feature_id_count += 1

    return result_table

def add_table_raw(table_data: list, feature_id_count: int, type: str = "data"):
    table_raw = f"{spaces(10)}<tr>\n"
    data_type = "th" if type == "header" else "td"
    for index, data in enumerate(table_data):
        if index == 0:
            table_raw += f"{spaces(12)}<{data_type}><a href=\"#feature{feature_id_count}\">{data}</a></{data_type}>\n"
        else:
            table_raw += f"{spaces(12)}<{data_type}>{data}</{data_type}>\n"
    table_raw += f"{spaces(10)}</tr>\n"
    return table_raw

def add_background(background):
    space_count_standard = 14
    background_status = get_status_symbol(background.execution_result)
    background_text = f"{spaces(space_count_standard)}<li>\n{spaces(space_count_standard+2)}<h3 class=\"scenario-name\">"
    background_text += f"{background_status} Background: {background.get_background_name()}</h3>\n{spaces(space_count_standard+2)}<table class=\"steps\">\n"
    for group in background.get_groups():
        for step in group.get_all_steps():
            step_status = get_status_symbol(step.execution_result)

            background_text += f"{spaces(space_count_standard+4)}<tr>\n"
            background_text += f"{spaces(space_count_standard+6)}<td>{step_status}</td>\n"
            background_text += f"{spaces(space_count_standard+6)}<td><strong>{step.step}</strong></td>\n"
            background_text += f"{spaces(space_count_standard+6)}<td>{encode_angle_brackets(step.description)}</td>\n"

            if step.execution_result == Status.failed:
                background_text += f"{spaces(space_count_standard+4)}</tr>\n"
                background_text += f"{spaces(space_count_standard+4)}<tr>\n"
                background_text += f"{spaces(space_count_standard+6)}<td></td>\n"
                background_text += f"{spaces(space_count_standard+6)}<td colspan=\"2\"><div class=\"traceback-message-block\"><div class=\"traceback-message\">"
                background_text += background.traceback_messages.strip().replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;") + "</div></div></td>\n"
            
            background_text += f"{spaces(space_count_standard+4)}</tr>\n"

    background_text += f"{spaces(space_count_standard+2)}</table>\n{spaces(space_count_standard)}</li>\n"
    return background_text

def add_scenario(feature_name, scenario):
    scenario_text = ""

    for group in scenario.get_groups():
        for step in group.get_all_steps():

            scenario_text += f"""
                  <tr>
                    <td>{get_status_symbol(step.execution_result)}</td>
                    <td><strong>{step.step}</strong></td>
                    <td>{encode_angle_brackets(step.description)}</td>
                  </tr>
            """.rstrip(' ')

            if step.execution_result == Status.failed:
                traceback_messages = scenario.traceback_messages.strip().replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")
                scenario_text += f"""
                  <tr>
                    <td></td>
                    <td colspan=\"2\">
                      <div class=\"traceback-message-block\">
                        <div class=\"traceback-message\">{traceback_messages}
                        </div>
                      </div>
                    </td>
                  </tr>
                """.rstrip(' ')

            if step.doc_string != "":
                scenario_text += add_doc_string(step)

            if step.data_table is not None:
                scenario_text += add_data_table(step)
    
    if isinstance(scenario, ScenarioOutline) and scenario.has_examples():
        scenario_text += add_examples(scenario)

    tags_text = "".join([f"                <span class=\"tag\">@{tag}</span>\n" for tag in FeatureManager.get_tags_of_scenario(feature_name, scenario.get_scenario_name())])
    scenario_text = f"""
              <li>
                {tags_text.lstrip()}
                <h3 class=\"scenario-name\">{get_status_symbol(scenario.execution_result)} Scenario{' Outline' if isinstance(scenario, ScenarioOutline) else ''}: {scenario.get_scenario_name()}</h3>
                <table class=\"steps\">{scenario_text}
                </table>
              </li>
    """

    return scenario_text

def add_doc_string(step):
    css_class = "doc-string"
    doc_string = step.doc_string.strip(' ')
    doc_string = doc_string.replace('\n        ', '\n')
    if doc_string.startswith('\n'): doc_string = doc_string.lstrip('\n')
    doc_string = doc_string.replace('\n', '<br>\n')
    doc_string = doc_string.replace(' ', '&nbsp;')

    doc_string_text = f"""
                  <tr>
                    <td></td>
                    <td colspan=\"2\">
                      <p class={css_class}>\"\"\"<br>{doc_string}\"\"\"<br></p>
                    </td>
                  </tr>
    """

    return doc_string_text.rstrip(' ')

def add_data_table(step):
    data_table = ""
    for row in step.data_table.to_list():
        data_table += f"{spaces(24)}<tr>\n"
        for element in row:
            data_table += f"{spaces(26)}<td>{element}</td>\n"
        data_table += f"{spaces(26)}<td></td>\n{spaces(24)}</tr>\n"

    data_table_text = f"""
                  <tr>
                    <td></td>
                    <td colspan=\"2\">
                      <table class=data-table>\n{data_table.rstrip()}
                      </table>
                    </td>
                  </tr>
    """

    return data_table_text

def add_examples(scenario):
    space_count_standard = 18
    example_table_class = "example-table"
    example_text = f"{spaces(space_count_standard)}<tr>\n{spaces(space_count_standard+2)}<td></td>\n{spaces(space_count_standard+2)}<td><strong>Examples: </strong></td>\n{spaces(space_count_standard+2)}<td></td>\n{spaces(space_count_standard)}</tr>\n"
    example_text += f"{spaces(space_count_standard)}<tr>\n{spaces(space_count_standard+2)}<td colspan=\"3\">\n{spaces(space_count_standard+4)}<table class=\"{example_table_class}\">\n"
    
    for index, row in enumerate(scenario.example_rows):
        if index == 0:
            example_text += f"{spaces(space_count_standard+6)}<tr>\n"
            example_text += f"{spaces(space_count_standard+8)}<td></td>\n"
            for variable in row:
                example_text += f"{spaces(space_count_standard+8)}<td class=\"example-table-header\">{variable.replace(' ', '&nbsp;')}</td>\n"

            example_text += f"{spaces(space_count_standard+8)}<td></td>\n"
            example_text += f"{spaces(space_count_standard+6)}</tr>\n"
        else:
            example_status = scenario.example_execution_result[index-1]["execution_result"]
            example_traceback_messages = scenario.example_execution_result[index-1]["traceback_messages"].strip().replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")
            example_status_symbol = get_status_symbol(example_status)
            
            example_text += f"{spaces(space_count_standard+6)}<tr>\n"
            example_text += f"{spaces(space_count_standard+8)}<td>{example_status_symbol}</td>\n"
        
            for variable in row:
                example_text += f"{spaces(space_count_standard+8)}<td>{variable.replace(' ', '&nbsp;')}</td>\n"

            example_text += f"{spaces(space_count_standard+8)}<td></td>\n"
            example_text += f"{spaces(space_count_standard+6)}</tr>\n"
        
            if example_status == Status.failed:
                example_text += f"{spaces(space_count_standard+6)}<tr class=\"example-traceback-message-row\">\n"
                example_text += f"{spaces(space_count_standard+8)}<td></td>\n"
                example_text += f"{spaces(space_count_standard+8)}<td colspan=\"{len(row)+1}\">\n"
                example_text += f"{spaces(space_count_standard+10)}<div class=\"traceback-message-block\"><div class=\"traceback-message\">\n"
                example_text += example_traceback_messages + f"\n{spaces(space_count_standard+10)}</div></div>\n{spaces(space_count_standard+8)}</td>\n"
                example_text += f"{spaces(space_count_standard+6)}</tr>\n"

    example_text += f"{spaces(space_count_standard+4)}</table>\n{spaces(space_count_standard+2)}</td>\n{spaces(space_count_standard)}</tr>\n"
    
    return example_text

def add_features():
    feature_id_count = 1
    features_text = ""
    for feature_name, feature in FeatureManager.get_features().items():
        symbol = get_status_symbol(Status.passed)
        for scenario in feature["scenarios"]:
            if scenario.execution_result == Status.failed:
                symbol = get_status_symbol(Status.failed)
        
        features_text += add_feature(feature_name, feature, symbol, feature_id_count)
        feature_id_count += 1
    return features_text

def add_feature(feature_name, feature, status, feature_id_count):
    feature_report_default_status = ""
    background_text = add_background(feature["background"]) if feature["background"] != None else ""
    scenario_text = "".join([add_scenario(feature_name, scenario) for scenario in feature["scenarios"]])
    tags_text = "".join([f"          <span class=\"tag\">@{tag}</span>\n" for tag in FeatureManager.get_tags_of_feature(feature_name)])

    feature_text = f"""
        <li>
          {tags_text.lstrip()}
          <details {feature_report_default_status}>
          <summary class=\"feature_title\" id=\"feature{feature_id_count}\">{status} Feature: {feature_name}</summary>
          <div class=\"test-result\">
            <ul class=\"scenario-list\">\n{background_text}{scenario_text}
            </ul>
          </div>
          </details>
        </li>
    """

    return feature_text
