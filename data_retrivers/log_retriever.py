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
LIMIT = 500
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
    retval = []
    job_ids = file_data.split("\n")
    for x in job_ids:
        if x == "":
            continue
        retval.append(int(x))
    return retval

def zip_files(path, name):
    shutil.make_archive(name, 'zip', path)

def get_n_folder():
    zipfiles = glob.glob(f"{DEST_FOLDER}/*.zip")
    zipfiles = [fil for fil in zipfiles if not "_old" in fil]
    numbers = list(map(lambda x: int(re.search("/logs(\d*)\.zip", x)[1]), zipfiles))
    return max(numbers, default=0)

def zip_and_delete(n_folder, dest_folder):
    print(f"Zipping {n_folder}...")
    zip_files(f"{dest_folder}/logs{n_folder}", f"./{dest_folder}/logs{n_folder}")
    print(f"Done zipping {n_folder}...")
    shutil.rmtree(f"{dest_folder}/logs{n_folder}")
    print(f"Files removed from folder {n_folder}...")
    n_folder += 1
    if not os.path.exists(f"{dest_folder}/logs{n_folder}"):
        os.makedirs(f"{dest_folder}/logs{n_folder}")

if __name__ == "__main1__":
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
        jobs_left = jobsDf[~jobsDf.id.isin(retrievedIds)].sort_values(by="id").id.unique()
        print("Jobs left", len(jobs_left))
        for job_id in jobs_left:
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
                time.sleep(0.5)
            #Logging progress
            if(i % LIMIT == 0):
                print(f"Sumbitted job logs: {i}...")
            #Zipping and remving folder with log files
            if(i % LIMIT_ZIP == 0):
                zip_and_delete(n_folder, DEST_FOLDER)
                n_folder+=1
    zip_and_delete(n_folder, DEST_FOLDER)
    print(i)

def get_all_zip_number():
    zipfiles = glob.glob(f"logs/test/*.zip")
    numbers = list(map(lambda x: int(re.search("/logs(\d*)\.zip", x)[1]), zipfiles))
    return numbers

def unzip_logs(zip_number):
    folder_path = f"{DEST_FOLDER}/new{zip_number}"
    shutil.unpack_archive(f"logs/test/logs{zip_number}.zip", folder_path, "zip")
    return folder_path

def remove_duplicates(path, old_ids):
    new_ids = []
    logfiles = glob.glob(f"{path}/*.log")
    ids = list(map(lambda x: int(re.search("/(\d*)\.log", x)[1]), logfiles))
    for log_id in ids:
        if log_id in old_ids:
            os.remove(f"{path}/{log_id}.log")
        else:
            new_ids.append(log_id)
    return new_ids

def log_ids_retrieved(ids):
    with open(f"{DEST_FOLDER}/{RETRIEVED_LOGS_FILE}", "a") as f:
        for job_id in ids:
            f.write(f"{job_id}\n")

#utils to recover retrieved job_ids from a folder
if __name__ == "__main1__":
    retrieved_job_ids = get_retrieved_logs()
    log_ids = remove_duplicates(f"{DEST_FOLDER}/logs15", retrieved_job_ids)
    log_ids_retrieved(log_ids)

#utils to recover retrieved job_ids from a zip folder
if __name__ == "__main_1_":
    retrieved_job_ids = get_retrieved_logs()
    zip_numbers = get_all_zip_number()
    #zip_numbers = set(zip_numbers).difference({8,23,22,20,21,19,17,18,16,15,14,3,4,5,6,7,11,12})
    for zip_n in zip_numbers:
        print(f"Unique logs so far {len(retrieved_job_ids)}...")
        print(f"Unzipping logs from zip {zip_n}...")
        path_to_folder = unzip_logs(zip_n)
        new_ids = remove_duplicates(path_to_folder, retrieved_job_ids)
        retrieved_job_ids = retrieved_job_ids + new_ids
        log_ids_retrieved(new_ids)
        #print(f"Zipping the unique logs from zip {zip_n}...")
        #zip_files(path_to_folder, f"{DEST_FOLDER}/new{zip_n}")
        print(f"Removing unzipped logs from zip {zip_n}...")
        shutil.rmtree(path_to_folder)


if __name__ == "__main__":
    retrievedIds = get_retrieved_logs()
    jobsDf = pd.read_csv(JOBS_CSV, index_col=0)
    jobs_left = jobsDf[~jobsDf.id.isin(retrievedIds)].sort_values(by="id").id.unique()
    print(len(jobs_left))