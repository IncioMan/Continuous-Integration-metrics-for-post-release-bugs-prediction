
from log_retriever import read_job_log, joblog
import re

#casper tests 58559541
"""FAIL 76 tests executed in 38.507s, 74 passed, 2 failed, 0 dubious, 0 skipped."""

#one test failed 152744497
"""Results :

Failed tests: 
  MigrationStepModuleTest.verify_count_of_added_MigrationStep_types:32 expected:<13[5]> but was:<13[2]>

Tests run: 1246, Failures: 1, Errors: 0, Skipped: 0"""

#Test errored
"""Results :

Tests in error: 
  CommonRulesTest.setUp:38 Â» BuildFailure status=1 build=[com.sonar.orchestrator...
  IssueWorkflowTest.issue_is_closed_as_removed_when_rule_is_disabled:38 Â» BuildFailure

Tests run: 3, Failures: 0, Errors: 2, Skipped: 0"""

#with log info
"""[INFO] Results:
[INFO] 
[ERROR] Failures: 
[ERROR]   DaoModuleTest.verify_count_of_added_components:32 expected:<[49]> but was:<[50]>
[INFO] 
[ERROR] Tests run: 1190, Failures: 1, Errors: 0, Skipped: 0"""


#Regex
GRADLE_TEST_C_F_S = "(\d*) tests completed, (\d*) failed, (\d*) skipped"
GRADLE_TEST_C_F = "(\d*) tests completed, (\d*) failed\n"
GRADLE_TEST_TOT_C_F_S = "Total tests run:(\d+), Failures: (\d+), Skips: (\d+)"
GRADLE_TEST_TOT_RESULTS_C_F_E_S = "Results:\\r\\n\[(.*)] \\r\\n\[(.*)] Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*)"
MAVEN_TEST_TOT_RESULTS_C_F_E_S_2 = "Results :\\r\\n\\r\\nTests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*)"
MAVEN_TEST_TOT_RESULTS_C_F_E_S_FAILED_TEST = "Results :((.*\\r\\n){,10})Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*)"
TEST_TASK_OUTCOME_REGEX = "Task :(.*):test (.*)"
CASPER_TESTS = "([a-zA-z0-0]+) (\d*)\ tests\ executed(.*) (\d*)\ passed, (\d*)\ failed,\ (\d*)\ dubious,\ (\d*)\ skipped"
MAVEN_RESULTS_C_F_E_S = "Results(\ ){,1}:(((.*)\\n){,100})(.*)Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*)"

def get_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(MAVEN_RESULTS_C_F_E_S, log)
    for res in allRes:
        total_tests += int(res[5])
        test_failed += int(res[6]) + int(res[7])
        test_skipped += int(res[8])
        test_passed = total_tests - test_skipped - test_failed

    allRes = re.findall(CASPER_TESTS, log)
    for res in allRes:
        total_tests += int(res[1])
        test_passed += int(res[3])
        test_failed += int(res[4]) 
        test_skipped += int(res[6])
    
    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = get_test_results(log)
    allRes = re.findall(TEST_TASK_OUTCOME_REGEX, log)
    failed_tasks = []
    for test_task in allRes:
        if(test_task == "FAILED"):
            failed_tasks.append(test_task)
    return total, passed, failed, skipped, failed_tasks

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(407956398)
    get_metrics(log)