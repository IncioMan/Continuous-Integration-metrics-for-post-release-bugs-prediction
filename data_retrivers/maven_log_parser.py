
from log_retriever import read_job_log, joblog
import re


#Regex
GRADLE_TEST_C_F_S = "(\d*) tests completed, (\d*) failed, (\d*) skipped"
GRADLE_TEST_C_F = "(\d*) tests completed, (\d*) failed\n"
GRADLE_TEST_TOT_C_F_S = "Total tests run:(\d+), Failures: (\d+), Skips: (\d+)"
GRADLE_TEST_TOT_RESULTS_C_F_E_S = "Results:\\r\\n\[(.*)] \\r\\n\[(.*)] Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*)"
MAVEN_TEST_TOT_RESULTS_C_F_E_S_2 = "Results :\\r\\n\\r\\nTests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*)"
TEST_TASK_OUTCOME_REGEX = "Task :(.*):test (.*)"

def get_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(MAVEN_TEST_TOT_RESULTS_C_F_E_S_2, log)
    for res in allRes:
        total_tests += int(res[0])
        test_failed += int(res[1]) + int(res[2])
        test_skipped += int(res[3])

    allRes = re.findall(GRADLE_TEST_TOT_RESULTS_C_F_E_S, log)
    for res in allRes:
        total_tests += int(res[2])
        test_failed += int(res[3]) + int(res[4])
        test_skipped += int(res[5])

    allRes = re.findall(GRADLE_TEST_C_F, log)
    for res in allRes:
        total_tests += int(res[0])
        test_failed += int(res[1])

    allRes = re.findall(GRADLE_TEST_C_F_S, log)
    for res in allRes:
        total_tests += int(res[0])
        test_failed += int(res[1]) 
        test_skipped += int(res[2])
    
    allRes = re.findall(GRADLE_TEST_TOT_C_F_S, log)
    for res in allRes:
        total_tests += int(res[0])
        test_failed += int(res[1]) 
        test_skipped += int(res[2])
    
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