#!/usr/bin/env python

#############################################################################
# Copyright 2020 F4E / GTD-SIR Barcelona, Spain
##
# testrunner is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# testrunner is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with testrunner.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

import os
import argparse
from argparse import RawTextHelpFormatter
import subprocess as sp
import csv

SPRINKLER_WAITING_MESSAGE_TIME = [5.03, 5.05, 3.8]
behave_passed_times = 0
behave_failed_times = 0
dsl_passed_times = 0
dsl_failed_times = 0
behave_failed_numbers = []
dsl_failed_numbers = []
behave_sprinklers_passed_times = [0, 0, 0]
dsl_sprinklers_passed_times = [0, 0, 0]
RESULT_FILE_NAME = './testing_sprinkler_contoller_result.csv'


def worker_scenario(scenario_names, feature_files, output, number):
    """Runs a given scenario a single time"""
    cmd = ["behave", "--no-capture", "--no-color"]
    if scenario_names is not None:
        for i in range(len(scenario_names)):
            cmd = cmd + ["-n"] + [scenario_names[i]]
    elif feature_files is not None:
        for i in range(len(feature_files)):
            cmd = cmd + [feature_files[i]]
    else:
        print("Running whole testsuite\n")
    # if output is not None:
        # cmd = cmd + ["-o"] + [output]
    
    behave_completed_process = sp.run(cmd, capture_output=True)

    if behave_completed_process.returncode == 0:
        global behave_passed_times
        behave_passed_times += 1

    elif behave_completed_process.returncode == 1:
        global behave_failed_times
        behave_failed_times += 1
        global behave_failed_numbers
        behave_failed_numbers.append(number)

    process_output = behave_completed_process.stdout.decode('ascii')

    global behave_sprinklers_passed_times
    if "sprinkler A passed" in process_output:
        behave_sprinklers_passed_times[0] += 1
    if "sprinkler B passed" in process_output:
        behave_sprinklers_passed_times[1] += 1
    if "sprinkler C passed" in process_output:
        behave_sprinklers_passed_times[2] += 1
        
    print("behave passed times: ", behave_passed_times)
    print("behave failed times: ", behave_failed_times)
    print("behave sprinklers success times: ", behave_sprinklers_passed_times)

    print("\n\n\n")


def run_embedded_dsl(out, number):
    """Runs a given scenario a single time"""
    cmd = ["python3", "test_sprinkler.py"]
    dsl_completed_process = sp.run(cmd, capture_output=True)

    if out is not None:
        with open(out, 'w') as f:
            f.write(dsl_completed_process.stdout.decode('ascii'))

    if dsl_completed_process.returncode == 0:
        global dsl_passed_times
        dsl_passed_times += 1
    elif dsl_completed_process.returncode == 1:
        global dsl_failed_times
        dsl_failed_times += 1
        global dsl_failed_numbers
        dsl_failed_numbers.append(number)

    process_output = dsl_completed_process.stdout.decode('ascii')

    global dsl_sprinklers_passed_times
    if "sprinkler A passed" in process_output:
        dsl_sprinklers_passed_times[0] += 1
    if "sprinkler B passed" in process_output:
        dsl_sprinklers_passed_times[1] += 1
    if "sprinkler C passed" in process_output:
        dsl_sprinklers_passed_times[2] += 1

    print("dsl passed times: ", dsl_passed_times)
    print("dsl failed times: ", dsl_failed_times)
    print("dsl sprinklers success times: ", dsl_sprinklers_passed_times)

    print("\n\n\n")



def runner_scenario_x_times(repetitions, scenario_names, feature_files, out):
    """
    Runs 'repetitions' times some given behave scenarios, features, or 
    the whole testsuite.

    :param repetitions: (int) number of times that a given test scenario,
                        feature file, or whole test suite, shall be run
    :param scenario_names: (seq) list of scenario names to be run a given
                           'repetitions' times
    :param feature_files: (seq) list of feature-files to be run a given
                          'repetitions' times
    """
    if scenario_names is not None:
        to_test = scenario_names
    elif feature_files is not None:
        to_test = feature_files
    else:
        to_test = "testsuite"
    msg = ("\nRunning " + str(repetitions) + " times test(s):\n " 
           + str(to_test) + "\n")
    print(msg)
    if out:
        out_name = os.path.splitext(out)[0]
        ext = os.path.splitext(out)[1]
    for i in range(repetitions):
        print("Iteration number: " + str(i+1))
        behave_out = None
        dsl_out = None
        if out:
            behave_out = "behave_" + out_name + "-" + str(i) + ext
            dsl_out = "dsl_" + out_name + "-" + str(i) + ext
        worker_scenario(scenario_names, feature_files, behave_out, i+1)
        run_embedded_dsl(dsl_out, i+1)


def main():

    parser = argparse.ArgumentParser(
                 description="Test Runner allowing to run n test scenarios",
                 formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        "repetitions", type=int, nargs="?", default=1,
        help="Number of repetitions to run some given test/s\n"
        + "(default=1)")
    parser.add_argument(
        "-n", "--scenario-names", type=str, nargs="+", default=None,
        help="Name of the scenario/s to be run 'x' times\n"
             + "(default=None)")
    parser.add_argument(
        "-f", "--feature-files", type=str, nargs="+", default=None,
        help="Name of the behave feature-file/s to be run 'x' times\n"
             + "(default=None)")
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Write output on specified file instead of stdout\n"
             + "(default=None)")

    args = parser.parse_args()

    runner_scenario_x_times(args.repetitions, 
                            args.scenario_names, 
                            args.feature_files, 
                            args.output)

    global behave_passed_times
    global behave_failed_times
    global dsl_passed_times
    global dsl_failed_times

    with open(RESULT_FILE_NAME, 'a') as f:
        # create the csv writer        
        writer = csv.writer(f)
        header = ['received_message_time', 'assertion_timeout', 'behave_passed_times', 'behave_failed_times', 'dsl_passed_times', 'dsl_failed_times', 'behave_sprinklers_success_times', 'dsl_sprinklers_success_times']
        if os.path.getsize(RESULT_FILE_NAME) == 0:
            writer.writerow(header)

        writer.writerow([SPRINKLER_WAITING_MESSAGE_TIME, 5, behave_passed_times, behave_failed_times, dsl_passed_times, dsl_failed_times, behave_sprinklers_passed_times, dsl_sprinklers_passed_times])

    print("behave failed number: ", behave_failed_numbers)
    print("dsl failed number: ", dsl_failed_numbers)
    print("behave sprinklers success times: ", behave_sprinklers_passed_times)
    print("dsl sprinklers success times: ", dsl_sprinklers_passed_times)

if __name__ == "__main__":
    main()

