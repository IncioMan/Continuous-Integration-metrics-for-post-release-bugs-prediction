
from log_retriever import read_job_log, joblog
import re

"""org.sonar.server.plugins.ServerExtensionInstallerTest > fail_when_detecting_ldap_auth_plugin FAILED
    java.lang.AssertionError: 
    Expected: (an instance of org.sonar.api.utils.MessageException and exception with message a string containing "Plugins 'LDAP' are no longer compatible with SonarQube")
         but: exception with message a string containing "Plugins 'LDAP' are no longer compatible with SonarQube" message was "Plugins 'LDAP' are no more compatible with SonarQube"
    Stacktrace was: Plugins 'LDAP' are no more compatible with SonarQube

3555 tests completed, 4 failed

> Task :server:sonar-server-common:test FAILED

FAILURE: Build failed with an exception."""


#Regex
GRADLE_TEST_C_F_S = "(\d*) tests completed, (\d*) failed, (\d*) skipped"
GRADLE_TEST_C_F = "(\d*) tests completed, (\d*) failed\\r\\n"
GRADLE_TEST_TOT_C_F_S = "Total tests run:(\d+), Failures: (\d+), Skips: (\d+)"
GRADLE_TEST_TOT_RESULTS_C_F_E_S = "Results:\\r\\n\[(.*)] \\r\\n\[(.*)] Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*)"
TASK_OUTCOME_REGEX = "Task :(.*) (.*)\\r\\n"

def gradle_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(GRADLE_TEST_TOT_RESULTS_C_F_E_S, log)
    for res in allRes:
        total_tests += int(res[2])
        test_failed += int(res[3]) + int(res[4])
        test_skipped += int(res[5])
        test_passed += total_tests - test_failed - test_skipped

    allRes = re.findall(GRADLE_TEST_C_F, log)
    for res in allRes:
        total_tests += int(res[0])
        test_failed += int(res[1])
        test_passed += total_tests - test_failed

    allRes = re.findall(GRADLE_TEST_C_F_S, log)
    for res in allRes:
        total_tests += int(res[0])
        test_failed += int(res[1]) 
        test_skipped += int(res[2])
        test_passed += total_tests - test_failed - test_skipped
    
    allRes = re.findall(GRADLE_TEST_TOT_C_F_S, log)
    for res in allRes:
        total_tests += int(res[0])
        test_failed += int(res[1]) 
        test_skipped += int(res[2])
        test_passed += total_tests - test_failed - test_skipped
    
    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = gradle_test_results(log)
    allRes = re.findall(TASK_OUTCOME_REGEX, log)
    failed_tasks = []
    for test_task in allRes:
        if(test_task[1] == "FAILED"):
            failed_tasks.append(test_task[0])
    return total, passed, failed, skipped, failed_tasks

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(547362230)
    print(get_metrics(log))