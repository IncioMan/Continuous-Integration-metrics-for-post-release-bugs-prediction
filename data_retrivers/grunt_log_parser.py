#74270524
"""[32m>> [39m[1m[42mTOTAL: tested 1 platforms, 0/142 tests failed[0m"""


from log_retriever import read_job_log, joblog
import re


#Regex
TEST_F_T = "TOTAL(.*) (\d*)\/(\d*) tests failed"

def get_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(TEST_F_T, log)
    for res in allRes:
        test_failed += int(res[1])
        total_tests += int(res[2])
        test_passed+= total_tests - test_failed

    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = get_test_results(log)
    return total, passed, failed, skipped

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(82530546)
    print(get_metrics(log))