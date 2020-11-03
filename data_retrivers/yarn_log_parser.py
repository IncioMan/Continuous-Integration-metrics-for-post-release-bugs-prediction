"""Test Suites: 370 passed, 370 total
Tests:       4 skipped, 1050 passed, 1054 total
Tests:       28 passed, 28 total
Snapshots:   830 passed, 830 total
Time:        67.988s
Ran all test suites.
Done in 99.84s."""


from log_retriever import read_job_log, joblog
import re


#Regex
TEST_REGEX_D_P_T = "Tests:(\ *)(\d*) skipped, (\d*) passed, (\d*) total"
TEST_REGEX_P_T = "Tests:(\ *)(\d*) passed, (\d*) total"

def get_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(TEST_REGEX_D_P_T, log)
    for res in allRes:
        test_skipped += int(res[1])
        test_passed += int(res[2])
        total_tests += int(res[3])
        test_failed += total_tests - test_passed - test_skipped

    allRes = re.findall(TEST_REGEX_P_T, log)
    for res in allRes:
        test_skipped += 0
        test_passed += int(res[1])
        total_tests += int(res[2])
        test_failed += total_tests - test_passed - test_skipped
    
    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = get_test_results(log)
    return total, passed, failed, skipped

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(407954661)
    print(get_metrics(log))