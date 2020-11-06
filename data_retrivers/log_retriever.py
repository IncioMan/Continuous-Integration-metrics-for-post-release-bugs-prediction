import pprint
import pickle
import pandas as pd
import os
from travis import get_job_log
import glob
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
pp = pprint.PrettyPrinter(depth=6)

#Constants
CSV_FOLDER = "csv"
DEST_FOLDER = "logs"
OFFSET = 0
DEST_FOLDER = "logs/test"
JOBS_CSV = f"{CSV_FOLDER}/allJobs.csv"
LIMIT = 100
RETRIEVED_LOGS_FILE = "retrived_logs.txt"
LIMIT_ZIP = 10000
###


def joblog(job_id):
    #print(f"Retrieving log for job {job_id}")
    result = get_job_log(job_id)
    if not result:
        return None
    return result["content"]

def dump_job_log(job_id, n_folder):
    #print(f"Retrieving log for job {job_id}")
    result = get_job_log(job_id)
    if not result:
        return None
    with open(f"{DEST_FOLDER}/logs{n_folder}/{job_id}.log", "w") as f:
        if(result["content"]):
            f.write(result["content"])
        else:
            f.write("null")
            print(job_id, " empty log")
        #print(f"Retrieved log for job {job_id}")
    return job_id

def read_job_log(job_id):
    with open(f"{DEST_FOLDER}/{job_id}.log", "r") as f:
        log = f.read()
        print(f"Retrieved log for job {job_id}")
    return log

def import_jobs():
    jobs = pd.read_csv(f"{CSV_FOLDER}/allJobs.csv", index_col=0)
    for datefield in ["started_at","created_at","finished_at","updated_at"]:
        jobs[f"{datefield}"] = pd.to_datetime(jobs[f"{datefield}"])
    return jobs

def get_retrieved_logs():
    PATH = f"{DEST_FOLDER}/{RETRIEVED_LOGS_FILE}"
    if not os.path.isfile(PATH):
        os.close(os.open(PATH, os.O_CREAT))
        return []
    with open(PATH, "r") as f:
        file_data = f.read()
    job_ids = file_data.split("\n")
    return job_ids

def zip_files(path, name):
    shutil.make_archive(name, 'zip', path)

def get_n_folder():
    zipfiles = glob.glob(f"{DEST_FOLDER}/*.zip")
    numbers = list(map(lambda x: int(re.search("/logs(\d*)\.zip", x)[1]), zipfiles))
    return max(numbers, default=0)

if __name__ == "__main__":
    retrievedIds = get_retrieved_logs()
    n_folder = get_n_folder() + 1
    if not os.path.exists(f"{DEST_FOLDER}/logs{n_folder}"):
        os.makedirs(f"{DEST_FOLDER}/logs{n_folder}")
    print(f"Already retrieved logs: {len(retrievedIds)}")
    jobsDf = pd.read_csv(JOBS_CSV, index_col=0)
    i = len(retrievedIds)
    failed = 0
    with ThreadPoolExecutor() as executor:
        futures = set()
        for job_id in jobsDf[~jobsDf.id.isin(retrievedIds)].sort_values(by="id").id.unique():
            if len(futures) >= LIMIT:
                completed, futures = wait(futures, return_when=FIRST_COMPLETED)
            futures.add(executor.submit(dump_job_log, job_id, n_folder))
            i += 1
            if(i % LIMIT == 0):
                completed, futures = wait(futures, return_when=ALL_COMPLETED)
                with open(f"{DEST_FOLDER}/{RETRIEVED_LOGS_FILE}", "a") as f:
                    for future in completed:
                        job_id_retrieved = future.result()
                        if(job_id_retrieved):
                            f.write(f"{job_id_retrieved}\n")
                time.sleep(5)
            #Logging progress
            if(i % 100 == 0):
                print(f"Sumbitted job logs: {i}...")
            #Zipping and remving folder with log files
            if(i % LIMIT_ZIP == 0):
                print(f"Zipping...")
                zip_files(f"{DEST_FOLDER}/logs{n_folder}", f"./{DEST_FOLDER}/logs{n_folder}")
                shutil.rmtree(f"{DEST_FOLDER}/logs{n_folder}")
                n_folder += 1
                if not os.path.exists(f"{DEST_FOLDER}/logs{n_folder}"):
                    os.makedirs(f"{DEST_FOLDER}/logs{n_folder}")
    print(i)


#utils to recover retrieved job_ids from a folder
if __name__ == "__main1__":
    jobs = glob.glob(f"{DEST_FOLDER}/logs1/*.log")
    numbers = list(map(lambda x: int(re.search("/(\d*)\.log", x)[1]), jobs))
    print(numbers)
    with open(f"{DEST_FOLDER}/{RETRIEVED_LOGS_FILE}", "a") as f:
        for job_id_retrieved in numbers:
            f.write(f"{job_id_retrieved}\n")