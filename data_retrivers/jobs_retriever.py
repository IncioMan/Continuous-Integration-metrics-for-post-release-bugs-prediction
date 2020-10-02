import pprint
import pandas as pd
import pickle
from travis import get_jobs

OFFSET = 25500
DEST_FOLDER = "jobs"
BUILDS_CSV = "csv/allBuilds.csv"

if __name__ == "__main__":
    allBuilds = pd.read_csv(BUILDS_CSV, index_col=0)

    pp = pprint.PrettyPrinter(depth=6)
    current_jobs = []
    i = 0
    failed = 0
    for build_id in allBuilds.sort_values(by="id").id.unique():
        if i < OFFSET:
            i+=1
            continue
        jobs = get_jobs(build_id)
        if not jobs:
            print(f"Failed build {build_id}")
            failed+=1
        else:
            current_jobs = current_jobs + jobs
            i+=1
        if(i % 100 == 0):
            print(f"Downloaded jobs: {i}...")
            with open(f'{DEST_FOLDER}/jobs{i}.pkl', 'wb') as f:
                pickle.dump(current_jobs, f)
            current_jobs = []  
    print(i)