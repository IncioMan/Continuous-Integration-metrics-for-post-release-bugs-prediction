
from log_retriever import read_job_log, joblog
import re


#Regex
JEST_TESTS = "(\d*) tests passed(.*)\((\d*) total"

def jest_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(JEST_TESTS, log)
    for res in allRes:
        total_tests += int(res[2])
        test_passed += int(res[0])
        test_failed += total_tests - test_passed
    
    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = jest_test_results(log)
    return total, passed, failed, skipped

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(407956398)
    print(get_metrics(log))