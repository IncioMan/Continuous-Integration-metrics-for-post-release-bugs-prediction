import pprint
import pickle
import pandas as pd
import os
from travis import get_job_log
import glob
import re
from log_retriever import read_job_log, dump_job_log, joblog
from gradle_parser import gradle_metrics_extractor
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
pp = pprint.PrettyPrinter(depth=6)

#Regex
EXCEPTION_REGEX = "\.(.*)exception"

#Constants
OFFSET = 0
CSV_FOLDER = "csv"
JOBS_CSV = "csv/allJobs.csv"
LIMIT = 10
DEST_FOLDER = "../logs"
JOB_LOG_METRICS_COLUMNS = ["job_id", "errors", "warnings", "skipped", "lines", "words",\
    "exceptions", "total_tests", "passed", "failed", "skipped", "failed_tasks"]
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
    log_lower = log.lower()
    warnings = log_lower.count("[warning]")
    errors = log_lower.count("[error]")
    skipped = log_lower.count("skipped")
    exceptions = re.findall(EXCEPTION_REGEX, log)
    #TODO test = get_test_metrics(log)
    lines = len(log.split("\n"))
    words = len(log.split())
    if(re.search("welcome to gradle|gradle (\d).(\d)", log_lower)):
        total_tests, passed, failed, skipped, failed_tasks = gradle_metrics_extractor(log)
    elif("reactor summary" in log_lower):
        print("")
        #maven_metrics_extractor(log)
    else:
        print(f"Error {job_id}, neither gradle nor maven")
    return (job_id, errors, warnings, skipped, lines, words, exceptions, total_tests, passed, failed, skipped, failed_tasks)

if __name__ == "__main__":
    jobs = import_jobs()
    jobs_log_metrics = load_jobs_log_metrics()
    i = 0
    with ThreadPoolExecutor() as executor:
        futures = set()
        #for job_id in jobs[~jobs.id.isin(jobs_log_metrics.job_id)].sort_values(by="id").id.unique():
        for job_id in [407736419, 407736420, 407954660, 407954661, 407956398, 407956399,
       408184892, 408184893, 408422063, 408422064, 408632307, 408632308,
       409059270, 409059271, 409980375, 409980376, 410459884, 410459885,
       410673685, 410673686]:
            if len(futures) >= LIMIT:
                completed, futures = wait(futures, return_when=FIRST_COMPLETED)
            futures.add(executor.submit(joblogmetric, job_id))
            i += 1
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
    print("ciao")