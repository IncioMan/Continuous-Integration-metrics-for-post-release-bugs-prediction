#93314119
"""[92m [0m[32m 159 passing[0m[90m (2s)[0m
[36m [0m[36m 12 pending[0m
[31m  1 failing[0m"""


from log_retriever import read_job_log, joblog
import re


#Regex
TEST_PASSED = "(\d*) passing"
TEST_PENDING = "\[(\d*)m ([(\d*)]{1,}) pending"
TEST_FAILED = "(\d*) failing"

def get_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(TEST_PASSED, log)
    for res in allRes:
        test_passed += int(res)
    
    allRes = re.findall(TEST_FAILED, log)
    for res in allRes:
        test_failed += int(res)

    allRes = re.findall(TEST_PENDING, log)
    for res in allRes:
        test_skipped += int(res[1])

    total_tests = test_passed + test_failed + test_skipped
    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = get_test_results(log)
    return total, passed, failed, skipped

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(93314119)
    print(get_metrics(log))