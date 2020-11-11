import pprint
import pickle
import pandas as pd
import os
from travis import get_job_log
import glob
import re
import random
import time
import concurrent.futures
import shutil
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
from multiprocessing import Lock, Process, Queue, current_process, cpu_count

import queue
import sys
from log_retriever import read_job_log, dump_job_log, joblog
import gradle_log_parser, yarn_log_parser, maven_log_parser, grunt_log_parser, mocha_log_parser
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
LIMIT = 100
DEST_FOLDER = "../logs"
JOB_LOG_METRICS_COLUMNS = ["job_id", "build_target","build_tool", "build_canceled_open_pr_on_branch"\
, "errors", "failures", "suspected_words", "warnings", "skipped_words", "lines", "words",\
    "exceptions", "error_classes", "tests_total", "tests_passed", "tests_failed", "tests_skipped", "failed_tasks"
    ]
LOCAL_WORKING_FOLDER = "local_log_parsing"
JOB_LOG_METRICS_PATH = f"{CSV_FOLDER}/jobs_log_metrics_final.csv"
JOB_LOG_METRICS_LOCAL_PARSING_PATH = f"{LOCAL_WORKING_FOLDER}/jobs_log_metrics_final.csv"
tmp_folder_name = f"{LOCAL_WORKING_FOLDER}/tmp_logs_to_parse"
###

def import_jobs():
    jobs = pd.read_csv(f"{CSV_FOLDER}/allJobs.csv", index_col=0)
    for datefield in ["started_at","created_at","finished_at","updated_at"]:
        jobs[f"{datefield}"] = pd.to_datetime(jobs[f"{datefield}"])
    return jobs

def load_jobs_log_metrics(path):
    if(os.path.isfile(path)):
        jobs_log_metrics = pd.read_csv(path, index_col=0)
        return jobs_log_metrics
    else:
        return pd.DataFrame([], columns=JOB_LOG_METRICS_COLUMNS)

def count_suspected_words(log, log_lower):
    return log_lower.count("illegal") + log_lower.count("unknown") +\
         log_lower.count("cannot") + log_lower.count("problem") + \
             log_lower.count("unable to") +\
             len(re.findall("\/(.*).sh: line\ (\d*):", log))

def joblogmetric(job_id, log=None):
    total_tests, passed, failed, skipped, failed_tasks = 0, 0, 0, 0, []
    if(not log):
        log = joblog(job_id)
    if(not log):
        return (job_id, None, None, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    log_lower = log.lower()
    build_canceled_open_pr_on_branch = (PULL_REQUEST_OPEN_CANCELING_BUILD in log)
    warnings = log_lower.count("warning")
    errors = log_lower.count("error")
    failures = log_lower.count("failure") + log_lower.count("failed")
    suspected_words = count_suspected_words(log, log_lower)
    skipped_words = log_lower.count("skipped")
    exceptions = re.findall(EXCEPTION_REGEX, log)
    exceptions = list(map(lambda x: x[0], exceptions))
    error_classes = re.findall(ERRORS_CLASSES_REGEX, log)
    error_classes = list(map(lambda x: x[0], error_classes))
    #TODO test = get_test_metrics(log)
    lines = len(log.split("\n"))
    words = len(log.split())
    build_tool = []
    build_target = ""
    #Define the target
    target = re.findall("TARGET=([^\\n\\r]*)", log)
    if(len(target) > 0):
        build_target = target[0]
    #Define the build parser
    #if((build_target == "WEB_TESTS") or (build_target == "WEB")):
    if(("yarn test" in log_lower) or ("yarn run" in log_lower) or ("yarn validate"in log_lower)):
        build_tool.append("yarn")
        tot, test_pass, fail, skip = yarn_log_parser.get_metrics(log)
        total_tests += tot
        passed += test_pass
        failed += fail
        skipped += skip
    if("mocha " in log_lower):
        build_tool.append( "mocha")
        tot, test_pass, fail, skip = mocha_log_parser.get_metrics(log)
        total_tests += tot
        passed += test_pass
        failed += fail
        skipped += skip
    if(re.search("node\ ([a-zA-Z]*?)(\/){0,1}([a-zA-Z]*?).js", log_lower)):
        build_tool.append("node")
        tot, test_pass, fail, skip = yarn_log_parser.get_metrics(log)
        total_tests += tot
        passed += test_pass
        failed += fail
        skipped += skip
    if("jest " in log_lower):
        build_tool.append("jest")
        if(not "yarn" in build_tool):
            tot, test_pass, fail, skip = yarn_log_parser.get_metrics(log)
            total_tests += tot
            passed += test_pass
            failed += fail
            skipped += skip
    if("grunt test" in log_lower):
        build_tool.append("grunt")
        tot, test_pass, fail, skip = grunt_log_parser.get_metrics(log)
        total_tests += tot
        passed += test_pass
        failed += fail
        skipped += skip
    #else:
    #f(build_target == "BUILD"):
    if(("reactor summary" in log_lower) or ("reactor build order" in log_lower)):
        build_tool.append("maven")
        tot, test_pass, fail, skip, failed_tasks = maven_log_parser.get_metrics(log)
        total_tests += tot
        passed += test_pass
        failed += fail
        skipped += skip
    elif(("welcome to gradle" in log_lower) or (":server:sonar-web:yarn" in log_lower)):
        build_tool.append( "gradle") 
        tot, test_pass, fail, skip, failed_tasks = gradle_log_parser.get_metrics(log)
        total_tests += tot
        passed += test_pass
        failed += fail
        skipped += skip
    return (job_id, build_target, build_tool, build_canceled_open_pr_on_branch, errors, failures, \
        suspected_words, warnings, skipped_words, lines, words,\
        exceptions, error_classes,\
        total_tests, passed, failed, skipped, failed_tasks
             )

def create_logs_folder(working_dir):
    if not os.path.exists(f"{working_dir}/tmp_logs_to_parse"):
        os.makedirs(f"{working_dir}/tmp_logs_to_parse")
    return f"{working_dir}/tmp_logs_to_parse"

def get_analysed_zip_number(zip_folder):
    if not os.path.exists(f"{zip_folder}/analysed_zip_numbers.txt"):
        return []
    else:
        numbers = []
        with(open(f"{zip_folder}/analysed_zip_numbers.txt", "r")) as f:
            for num in f.read().split("\n"):
                if num == '':
                    continue
                numbers.append(int(num))
        return numbers

def unzip_logs(zip_number, zip_folder, dest_folder):
    #remove files from old unzipping and start fresh
    for log_file in glob.iglob(os.path.join(dest_folder, '*.log')):
        os.remove(log_file)
    shutil.unpack_archive(f"{zip_folder}/logs{zip_number}.zip", dest_folder, "zip")

def get_all_zip_number(folder):
    zipfiles = glob.glob(f"{folder}/*.zip")
    zipfiles = [fil for fil in zipfiles if not "_old" in fil]
    numbers = list(map(lambda x: int(re.search("/logs(\d*)\.zip", x)[1]), zipfiles))
    return numbers

def zip_file_analysed(zip_number, working_dir):
    if not os.path.exists(f"{working_dir}/analysed_zip_numbers.txt"):
        with(open(f"{working_dir}/analysed_zip_numbers.txt", "w")) as f:
            f.write(f"{zip_number}\n")
    else:
        with(open(f"{working_dir}/analysed_zip_numbers.txt", "a")) as f:
            f.write(f"{zip_number}\n")

#Main to parse logs from Travis apis
def parse_logs_from_travis_server(job_ids_to_parse, path_to_csv_results):
    jobs_log_metrics = load_jobs_log_metrics(path_to_csv_results)
    i = 0
    tot_count = 0
    with ThreadPoolExecutor() as executor:
        futures = set() 
        job_ids = list(set(job_ids_to_parse).difference(set(jobs.id.unique())))
        for job_id in job_ids:
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
                futures = set()
                print(f"Sumbitted job logs: {i}...")
                i = 0
                time.sleep(5)
    jobs_log_metrics.to_csv(path_to_csv_results)
    print("Done")

"""def multithread_parsing(job_ids, jobs_log_metrics, logs_folder, parallel_limit):
    i = 0
    tmp_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = set()
        for job_id in job_ids:
            with(open(f"{logs_folder}/{job_id}.log", "r")) as f:
                log = f.read()
                futures.add(executor.submit(joblogmetric, job_id, log)) 
        for future in concurrent.futures.as_completed(futures):
            response = future.result()
            tmp_data.append(response)
        response_df = pd.DataFrame(tmp_data, columns = JOB_LOG_METRICS_COLUMNS)
        jobs_log_metrics = jobs_log_metrics.append(response_df, ignore_index=True)
        print(f"Sumbitted job logs: {len(job_ids)}...")
    return jobs_log_metrics"""

def parse_log(queue_job_ids, queue_job_results, logs_folder):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            job_id = queue_job_ids.get_nowait()
        except queue.Empty:
            break
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            i = 0
            with(open(f"{logs_folder}/{job_id}.log", "r")) as f:
                log = f.read()
            results = joblogmetric(job_id, log)
            queue_job_results.put(results)

def multiprocess_parsing(job_ids, logs_folder, log_progress=False):
    number_of_task = 10
    number_of_processes = int(cpu_count()/2)
    queue_job_ids = Queue()
    queue_job_results = Queue()
    processes = []

    for i in job_ids:
        queue_job_ids.put(i)

    # creating processes
    for w in range(number_of_processes):
        p = Process(target=parse_log, args=(queue_job_ids, queue_job_results, logs_folder))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join(100)

    # print the output
    results = []
    while not queue_job_results.empty():
        results.append(queue_job_results.get())
    if log_progress:
        print(f"Parsed logs for {len(job_ids)} jobs...")
    return results

def singleprocess_parsing(job_ids, jobs_log_metrics, logs_folder, log_progress=False):
    tmp_data = []
    for job_id in job_ids:
        with(open(f"{logs_folder}/{job_id}.log", "r")) as f:
            log = f.read()
            response = joblogmetric(job_id, log)
            tmp_data.append(response)
    if log_progress:
        print(f"Parsed logs for {len(job_ids)} jobs...")
    return tmp_data
def divide_chunks(l, n): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

"""if __name__ == "__main1__":
    jobs_log_metrics = pd.read_csv(JOB_LOG_METRICS_LOCAL_PARSING_PATH, index_col=0)
    print(len(jobs_log_metrics))
    jobs_log_metrics_copy = pd.read_csv(f"{LOCAL_WORKING_FOLDER}/jobs_log_metrics_final_copy.csv", index_col=0)
    print(len(jobs_log_metrics_copy))
    jobs_log_metrics = jobs_log_metrics.append(jobs_log_metrics_copy, ignore_index=True)
    print(len(jobs_log_metrics.drop_duplicates()))
    jobs_log_metrics.drop_duplicates().to_csv(JOB_LOG_METRICS_LOCAL_PARSING_PATH)"""

def parse_logs_from_local_zips(job_ids_to_parse, zip_folder, path_to_csv_results):
    print(f"Results will be available in {path_to_csv_results}")
    jobs_log_metrics = load_jobs_log_metrics(path_to_csv_results)
    dir_with_logs = create_logs_folder(zip_folder)
    zip_numbers = get_all_zip_number(zip_folder)
    analysed_zip_numbers = get_analysed_zip_number(zip_folder)
    missing_zip_numbers = list(set(zip_numbers).difference(set(analysed_zip_numbers)))
    for zip_number in missing_zip_numbers:
        print("Analysing zip file", zip_number)
        unzip_logs(zip_number, zip_folder, dir_with_logs)
        log_files = glob.glob(f"{dir_with_logs}/*.log")
        job_ids = list(map(lambda x: int(re.search("/(\d*)\.log", x)[1]), log_files))
        print(f"Logs in this zip folder {len(job_ids)}...")
        #process only logs which have not been parsed before and are in list to parse
        job_ids = list(set(job_ids).difference(set(jobs_log_metrics.job_id)).intersection(job_ids_to_parse))
        print(f"Logs to parse in this zip folder {len(job_ids)}...")
        print(f"Logs left to parse {len(set(job_ids_to_parse).difference(jobs_log_metrics.job_id))}...")
        #divide in batches of N jobs
        job_batches = list(divide_chunks(job_ids, 100)) 
        #
        analysed_from_zip = 0
        for i, batch in enumerate(job_batches):
            print(f"Processing batch {i} of zip {zip_number}, analyzed from zip {analysed_from_zip}")
            results = multiprocess_parsing(batch, dir_with_logs)
            new_parsed_metrics = pd.DataFrame(results, columns = JOB_LOG_METRICS_COLUMNS)
            analysed_from_zip += len(new_parsed_metrics)
            print("new_parsed_metrics", len(new_parsed_metrics))
            print("jobs_log_metrics", len(jobs_log_metrics))
            jobs_log_metrics = jobs_log_metrics.append(new_parsed_metrics, ignore_index=True)
            print("jobs_log_metrics",len(jobs_log_metrics))
            jobs_log_metrics.to_csv(path_to_csv_results)
        #
        jobs_log_metrics.to_csv(path_to_csv_results)
        print("Saved parsing results..")
        zip_file_analysed(zip_number, zip_folder)
        print("Done analysing zip file", zip_number)
        for log_id in job_ids:
                os.remove(f"{dir_with_logs}/{log_id}.log")
        print("Removed log files")
    shutil.rmtree(dir_with_logs)
    print("Removed log folder")

if __name__ == "__main__":
    x = "1"
    #from local zip files all jobs ids
    if x == "1":
        jobs = import_jobs()
        parse_logs_from_local_zips(list(jobs.id.unique()), "logs/test", JOB_LOG_METRICS_LOCAL_PARSING_PATH)
    #from local zip files only jobs ids specified in the file
    if x == "2":
        job_ids_to_parse = []
        with open("job_ids_to_parse.txt", "r") as f:
            text = f.read()
        for job_id in text.split("\n"):
            if job_id == "":
                continue
            job_ids_to_parse.append(int(job_id))
        parse_logs_from_local_zips(job_ids_to_parse, "logs/test", JOB_LOG_METRICS_LOCAL_PARSING_PATH)
    #from server all jobs ids
    if x == "3":
        jobs = import_jobs()
        parse_logs_from_travis_server(list(jobs.id.unique), JOB_LOG_METRICS_LOCAL_PARSING_PATH) 
    #from server only jobs ids specified in the file  
    if x == "4":
        job_ids_to_parse = []
        with open("job_ids_to_parse.txt", "r") as f:
            text = f.read()
        for job_id in text.split("\n"):
            if job_id == "":
                continue
            job_ids_to_parse.append(int(job_id))
        parse_logs_from_travis_server(list(jobs.id.unique), JOB_LOG_METRICS_LOCAL_PARSING_PATH)