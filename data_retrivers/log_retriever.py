import pprint
import pickle
import pandas as pd
import os
from travis import get_job_log
import glob
import re
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
pp = pprint.PrettyPrinter(depth=6)

#Constants
CSV_FOLDER = "csv"
DEST_FOLDER = "logs"
###


def joblog(job_id):
    #print(f"Retrieving log for job {job_id}")
    result = get_job_log(job_id)
    if not result:
        return None
    return result["content"]

def dump_job_log(job_id):
    print(f"Retrieving log for job {job_id}")
    #print(f"Retrieving log for job {job_id}")
    result = get_job_log(job_id)
    if not result:
        return False
    with open(f"{DEST_FOLDER}/{job_id}.log", "w") as f:
        f.write(result["content"])
        print(f"Retrieved log for job {job_id}")
        #print(f"Retrieved log for job {job_id}")
    return True

def read_job_log(job_id):
    with open(f"{DEST_FOLDER}/{job_id}.log", "r") as f:
        log = f.read()
        print(f"Retrieved log for job {job_id}")
    return log