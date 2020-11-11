
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
CASPER_TESTS = "([a-zA-z0-0]+) (\d*)\ tests\ executed(.*) (\d*)\ passed, (\d*)\ failed,\ (\d*)\ dubious,\ (\d*)\ skipped"
MAVEN_RESULTS_C_F_E_S = "Results(\ ){,1}:(((.*?)\\n)*?)Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*)"

def get_test_results(log):
    total_tests = 0
    test_passed = 0
    test_skipped = 0
    test_failed = 0

    allRes = re.findall(MAVEN_RESULTS_C_F_E_S, log)
    for res in allRes:
        test_passed += int(res[4])
        test_failed += int(res[5]) + int(res[6])
        test_skipped += int(res[7])
        total_tests = test_passed + test_skipped + test_failed

    allRes = re.findall(CASPER_TESTS, log)
    for res in allRes:
        total_tests += int(res[1])
        test_passed += int(res[3])
        test_failed += int(res[4]) 
        test_skipped += int(res[6])
    
    return total_tests, test_passed, test_failed, test_skipped


def get_metrics(log):
    total, passed, failed, skipped = get_test_results(log)
    return total, passed, failed, skipped, []

if __name__ == "__main__":
    #dump_job_log(728138257)
    log = joblog(129114106)
    #log = "processing request: The target server failed to respond\n2015.09.25 18:21:17 INFO  Retrying request\n2015.09.25 18:21:17 INFO  I/O exception (org.apache.http.NoHttpResponseException) caught when processing request: The target server failed to respond\n2015.09.25 18:21:17 INFO  Retrying request\n2015.09.25 18:21:17 INFO  I/O exception (org.apache.http.NoHttpResponseException) caught when processing request: The target server failed to respond\n2015.09.25 18:21:17 INFO  Retrying request\n2015.09.25 18:21:19 INFO  I/O exception (org.apache.http.NoHttpResponseException) caught when processing request: The target server failed to respond\n2015.09.25 18:21:19 INFO  Retrying request\n2015.09.25 18:21:19 INFO  I/O exception (org.apache.http.NoHttpResponseException) caught when processing request: The target server failed to respond\n2015.09.25 18:21:19 INFO  Retrying request\n2015.09.25 18:21:19 INFO  I/O exception (org.apache.http.NoHttpResponseException) caught when processing request: The target server failed to respond\n2015.09.25 18:21:19 INFO  Retrying request\n\nResults :\n\nTests run: 54, Failures: 0, Errors: 0, Skipped: 0\n\n[INFO] \n[INFO] --- maven-jar-plugin:2.6:jar (default-jar) @ it-tests ---\n[WARNING] JAR will be empty - no content was marked for inclusion!\n[INFO] Building jar: /home/travis/build/SonarSource/sonarqube/it/it-tests/target/it-tests-5.2-SNAPSHOT.jar\n[INFO] \n[INFO] --- maven-source-plugin:2.4:jar-no-fork (attach-sources) @ it-tests ---\n[INFO] Skipping source per configuration.\n[INFO] \n[INFO] --- animal-sniffer-maven-plugin:1.14:check (enforce-java-api-compatibility) @ it-test"
    #log = "Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.131 sec - in org.sonar.db.component.ComponentLinkDaoTest\r\n\r\nResults :\r\n\r\nTests in error: \r\n  RoleDaoTest.count_user_twice_when_user_and_group_permission:222 » Persistence ...\r\n  RoleDaoTest.count_users_with_one_permission_when_the_last_one_is_in_a_group:199 » Persistence\r\n  RoleDaoTest.count_users_with_one_specific_permission:181 » Persistence \r\n### Er...\r\n\r\nTests run: 463, Failures: 0, Errors: 3, Skipped: 23\r\n\r\n[INFO] ------------------------------------------------------------------------\r\n[INFO] Reactor Summary:\r\n[INFO] \r\n[INFO] SonarQube .......................................... SUCCESS [  4.423 s]\r\n[INFO] S"
    print(get_metrics(log))