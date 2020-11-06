#74270524
"""[32m>> [39m[1m[42mTOTAL: tested 1 platforms, 0/142 tests failed[0m"""
#62977969
"""PASS Coding Rules :: List Actions :: Deactivate (6 tests)
Test file: src/test/js/coding-rules-page-quality-profile-facet.js
PASS coding-rules-page-quality-profile-facet (6 tests)
PASS Coding Rules :: Facets :: Language (NaN test)
PASS 21 tests executed in 11.88s, 21 passed, 0 failed, 0 dubious, 0 skipped.
Unsafe JavaScript attempt to access frame with URL about:blank from frame with URL file:///home/travis/build/SonarSource/sonarqube/server/sonar-web/node_modules/casperjs/bin/bootstrap.js. Domains, protocols and ports must match."""


from log_retriever import read_job_log, joblog
import re


#Regex
TEST_F_T = "TOTAL(.*) (\d*)\/(\d*) tests failed"
TEST_T_P_F_D_S = "PASS\ (\d*) tests executed\ in\ (.*)\ (\d*) passed,\ (\d*) failed,\ (\d*)\ dubious,\ (\d*)\ skipped"

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

    allRes = re.findall(TEST_T_P_F_D_S, log)
    for res in allRes:
        total_tests += int(res[0])
        test_passed+= int(res[2])
        test_failed += int(res[3])
        test_skipped += int(res[4])

    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = get_test_results(log)
    return total, passed, failed, skipped

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(62977969)
    print(get_metrics(log))