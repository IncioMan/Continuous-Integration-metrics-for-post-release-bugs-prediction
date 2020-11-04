"""Test Suites: 370 passed, 370 total
Tests:       4 skipped, 1050 passed, 1054 total
Tests:       28 passed, 28 total
Snapshots:   830 passed, 830 total
Time:        67.988s
Ran all test suites.
Done in 99.84s."""

"""Test Suites: 187 passed, 187 total
Tests:       1 skipped, 579 passed, 580 total
Snapshots:   429 passed, 429 total
Time:        285.168s
Ran all test suites.
Done in 339.53s."""

#185464744
"""[1m[32m â€º [39m[22m[1m[32m259 tests passed[39m[22m (259 total in 61 test suites, 25 snapshots, run time 38.11s)
[2K[1GDone in 39.56s."""


from log_retriever import read_job_log, joblog
import re


#Regex
TEST_REGEX_D_P_T = "Tests:(\ *)(\d*) skipped, (\d*) passed, (\d*) total"
TEST_REGEX_P_T = "Tests:(\ *)(\d*) passed, (\d*) total"
TEST_REGEX_FORMAT_2_P_T = "Tests:(\ *)\\x1b\[(\d*)m\\x1b\[(\d*)m\\x1b\[(\d*)m(\d*) passed\\x1b\[(\d*)m\\x1b\[(\d*)m(\d*), (\d*) total"
TEST_REGEX_P_T_2 = "(\d*) tests passed(.*)\((\d*) total"
FORMAT_2 = "\\x1b\[(\d*)mTests"

def test_parser_format2(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(TEST_REGEX_FORMAT_2_P_T, log)
    for res in allRes:
        test_passed += int(res[4])
        total_tests += int(res[8])
        test_failed += total_tests - test_passed

    return total_tests, test_passed, test_failed, test_skipped

def get_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(TEST_REGEX_P_T_2, log)
    for res in allRes:
        test_passed += int(res[0])
        total_tests += int(res[2])
        test_failed += total_tests - test_passed
    
    if(total_tests > 0):
        return total_tests, test_passed, test_failed, test_skipped

    allRes = re.findall(TEST_REGEX_D_P_T, log)
    for res in allRes:
        test_skipped += int(res[1])
        test_passed += int(res[2])
        total_tests += int(res[3])
        test_failed += total_tests - test_passed - test_skipped

    if(total_tests > 0):
        return total_tests, test_passed, test_failed, test_skipped

    allRes = re.findall(TEST_REGEX_P_T, log)
    for res in allRes:
        test_skipped += 0
        test_passed += int(res[1])
        total_tests += int(res[2])
        test_failed += total_tests - test_passed - test_skipped

    if(total_tests > 0):
        return total_tests, test_passed, test_failed, test_skipped

    allRes = re.findall(TEST_REGEX_FORMAT_2_P_T, log)
    for res in allRes:
        test_passed += int(res[4])
        total_tests += int(res[8])
        test_failed += total_tests - test_passed
    
    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = get_test_results(log)
    return total, passed, failed, skipped

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(185464744)
    print(get_metrics(log))