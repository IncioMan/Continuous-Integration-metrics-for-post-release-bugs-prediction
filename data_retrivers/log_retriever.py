import pprint
import pickle
import pandas as pd
import os
from travis import get_job_log
import glob
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
pp = pprint.PrettyPrinter(depth=6)

OFFSET = 0
DEST_FOLDER = "logs"
JOBS_CSV = "csv/allJobs.csv"
LIMIT = 100

def joblog(job_id):
    print(f"Retrieving log for job {job_id}")
    result = get_job_log(job_id)
    if not result:
        return False
    with open(f"{DEST_FOLDER}/{job_id}.log", "w") as f:
        f.write(result["content"])
        print(f"Retrieved log for job {job_id}")
    return True

if __name__ == "__main__":
    retrievedLogs = glob.glob(f"{DEST_FOLDER}/*.log")
    retrievedIds = list(map(lambda x: int(os.path.basename(x).replace(".log", "")), retrievedLogs))
    jobsDf = pd.read_csv(JOBS_CSV, index_col=0)
    i = 0
    failed = 0
    with ThreadPoolExecutor() as executor:
        futures = set()
        for job_id in jobsDf[~jobsDf.id.isin(retrievedIds)].sort_values(by="id").id.unique():
            if i < OFFSET:
                i+=1
                continue
            if len(futures) >= LIMIT:
                completed, futures = wait(futures, return_when=FIRST_COMPLETED)
            futures.add(executor.submit(joblog, job_id))
            i += 1
            if(i % 100 == 0):
                print(f"Sumbitted job logs: {i}...")
    print(i)