import pprint
import pickle
import pandas as pd
import os
from travis import get_job_log
import glob
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
pp = pprint.PrettyPrinter(depth=6)

OFFSET = 0
CSV_FOLDER = "csv"
JOBS_CSV = "csv/allJobs.csv"
LIMIT = 10
JOB_LOG_METRICS_COLUMNS = ["job_id", "errors", "warnings", "skipped", "lines", "words"]
JOB_LOG_METRICS_PATH = f"{CSV_FOLDER}/jobs_log_metrics.csv"

def joblog(job_id):
    #print(f"Retrieving log for job {job_id}")
    result = get_job_log(job_id)
    if not result:
        return None
    return result["content"]

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

def get_test_metrics(log):
    log.

def joblogmetric(job_id):
    log = joblog(job_id).lower()
    warnings = log.count("warning")
    errors = log.count("error")
    skipped = log.count("skipped")
    #TODO test = get_test_metrics(log)
    lines = len(log.split("\n"))
    words = len(log.split())
    return (job_id, errors, warnings, skipped, lines, words)

if __name__ == "__main__":
    jobs = import_jobs()
    jobs_log_metrics = load_jobs_log_metrics()
    i = 0
    with ThreadPoolExecutor() as executor:
        futures = set()
        for job_id in jobs[~jobs.id.isin(jobs_log_metrics.job_id)].sort_values(by="id").id.unique():
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
                i = 0
            if(i % 100 == 0):
                print(f"Sumbitted job logs: {i}...")
    print("ciao")