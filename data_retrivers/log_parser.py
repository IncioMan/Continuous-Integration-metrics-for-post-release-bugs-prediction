import pprint
import pickle
import pandas as pd
import os
from travis import get_job_log
import glob
import re
import random
import time
from log_retriever import read_job_log, dump_job_log, joblog
import gradle_log_parser, yarn_log_parser, maven_log_parser
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
pp = pprint.PrettyPrinter(depth=6)

#Regex
EXCEPTION_REGEX = "\.([A-Za-z0-9]+)Exception(\W{1,})"
ERRORS_CLASSES_REGEX = "\.([A-Za-z0-9]+)Error(\W{1,})"
PULL_REQUEST_OPEN_CANCELING_BUILD = "branch with open pull request, canceling the build"
BUILD_FAILURE_WHAT_WENT_WRONG = "\* What went wrong:\\r\\nExecution failed for task (.*)"

#Constants
OFFSET = 0
CSV_FOLDER = "csv"
JOBS_CSV = "csv/allJobs.csv"
LIMIT = 200
DEST_FOLDER = "../logs"
JOB_LOG_METRICS_COLUMNS = ["job_id", "build_target","build_tool", "build_canceled_open_pr_on_branch"
#, "errors", "warnings", "skipped_words", "lines", "words",\
    #"exceptions", "error_classes", "build_canceled_open_pr_on_branch", "tests_total", "tests_passed", "tests_failed", "tests_skipped", "failed_tasks"
    ]
JOB_LOG_METRICS_PATH = f"{CSV_FOLDER}/jobs_log_metrics.csv"
###

def import_jobs():
    jobs = pd.read_csv(f"{CSV_FOLDER}/allJobs.csv", index_col=0)
    for datefield in ["started_at","created_at","finished_at","updated_at"]:
        jobs[f"{datefield}"] = pd.to_datetime(jobs[f"{datefield}"])
    return jobs

def load_jobs_log_metrics():
    if(os.path.isfile(JOB_LOG_METRICS_PATH)):
        jobs_log_metrics = pd.read_csv(JOB_LOG_METRICS_PATH, index_col=0)
        return jobs_log_metrics
    else:
        return pd.DataFrame([], columns=JOB_LOG_METRICS_COLUMNS)

def joblogmetric(job_id):
    total_tests, passed, failed, skipped, failed_tasks = 0, 0, 0, 0, []
    log = joblog(job_id)
    if(not log):
        return (job_id, None, None)
        #, None, None, None, None, None, None, None, None, None, None, None, None)
    log_lower = log.lower()
    build_canceled_open_pr_on_branch = (PULL_REQUEST_OPEN_CANCELING_BUILD in log)
    warnings = log_lower.count("[warning]")
    errors = log_lower.count("[error]")
    skipped_words = log_lower.count("skipped")
    #exceptions = re.findall(EXCEPTION_REGEX, log)
    #exceptions = list(map(lambda x: x[0], exceptions))
    #error_classes = re.findall(ERRORS_CLASSES_REGEX, log)
    #error_classes = list(map(lambda x: x[0], error_classes))
    #TODO test = get_test_metrics(log)
    lines = len(log.split("\n"))
    words = len(log.split())
    build_tool = []
    build_target = ""
    #Define the target
    target = re.findall("TARGET=(.*)\\r", log)
    if(len(target) > 0):
        build_target = target[0]
    #Define the build parser
    if((build_target == "WEB_TESTS") or (build_target == "WEB")):
        if(":server:sonar-web:yarn" in log_lower):
            build_tool.append( "gradle")
            #total_tests, passed, failed, skipped, failed_tasks = maven_log_parser.get_metrics(log)
        if(("yarn run" in log_lower) or ("yarn validate"in log_lower)):
            build_tool.append("yarn")
            #total_tests, passed, failed, skipped = yarn_log_parser.get_metrics(log)
            warnings = log_lower.count("warning")
        if("mocha" in log_lower):
            build_tool.append( "mocha")
    else:
    #f(build_target == "BUILD"):
        if("reactor summary" in log_lower):
            build_tool.append("maven")
            #total_tests, passed, failed, skipped, failed_tasks = maven_log_parser.get_metrics(log)
        elif(re.search("welcome to gradle", log_lower)):
            build_tool.append( "gradle")
            #total_tests, passed, failed, skipped, failed_tasks = gradle_log_parser.get_metrics(log)
            if("yarn run" in log_lower):
                build_tool.append("yarn")
                #total_tests, passed, failed, skipped = yarn_log_parser.get_metrics(log)
                warnings = log_lower.count("warning")
    return (job_id, build_target, build_tool, build_canceled_open_pr_on_branch
    #, errors, warnings, skipped_words, lines, words,\
         #exceptions, error_classes, build_canceled_open_pr_on_branch, \
             #total_tests, passed, failed, skipped, failed_tasks
             )

if __name__ == "__main__":
    jobs = import_jobs()
    jobs_log_metrics = load_jobs_log_metrics()
    i = 0
    tot_count = 0
    with ThreadPoolExecutor() as executor:
        futures = set()
        #jobs = jobs[jobs.created_at > pd.to_datetime("2018-11-30 00:00:00+00:00")]
        job_ids = jobs[~jobs.id.isin(jobs_log_metrics.job_id)].sort_values(by="id").id.unique()
        for job_id in random.choices(job_ids, k=1000):
            if len(futures) >= LIMIT:
                completed, futures = wait(futures, return_when=FIRST_COMPLETED)
            futures.add(executor.submit(joblogmetric, job_id))
            i += 1
            tot_count+=1
            if(i == LIMIT):
                completed, futures = wait(futures, return_when=ALL_COMPLETED)
                tmp_data = []
                for future in completed:
                    response = future.result()
                    tmp_data.append(response)
                response_df = pd.DataFrame(tmp_data, columns = JOB_LOG_METRICS_COLUMNS)
                jobs_log_metrics = jobs_log_metrics.append(response_df, ignore_index=True)
                jobs_log_metrics.to_csv(JOB_LOG_METRICS_PATH)
                futures = set()
                print(f"Sumbitted job logs: {i}...")
                i = 0
                time.sleep(1)
            if(tot_count > 1000):
                break
    print("ciao")