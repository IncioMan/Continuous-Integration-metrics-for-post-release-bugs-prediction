import requests
import pprint
import pickle
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
pp = pprint.PrettyPrinter(depth=6)

_BASE_URL = "https://api.github.com/"

with open(".githubtoken", "r") as f:
    GITHUB_TOKEN = f.read()

headers = { \
    "Content-Type": "application/json", \
    "Accept": "application/json",
    "Authorization": "token {}".format(GITHUB_TOKEN)
}

def _request(method="get", endpoint="", headers=headers, **kwargs):
    """ Wrapper around requests.get and requests.post """

    methods = {
        "get": requests.get,
        "patch": requests.patch,
        "post": requests.post
    }

    if method in methods:
        request = methods[method]
    else:
        request = methods["get"]

    return request(_BASE_URL + endpoint, headers=headers, **kwargs)
   
def get_compare_tags(owner, repo, tag1, tag2):
    query = f"repos/{owner}/{repo}/compare/{tag1}...{tag2}"
    response = _request(endpoint=query)
    checkRateLimit(response)
    return response

def get_pull_request(owner, repo, pull_number):
    query = f"repos/{owner}/{repo}/pulls/{pull_number}"
    response = _request(endpoint=query)
    return response

def get_pull_request_commits(owner, repo, pull_number):
    query = f"repos/{owner}/{repo}/pulls/{pull_number}/commits?per_page=1000"
    response = _request(endpoint=query)
    checkRateLimit(response)
    return response

def get_pull_request_data(owner, repo, pull_number):
    response_pr = get_pull_request(owner, repo, pull_number)
    response_commits = get_pull_request_commits(owner, repo, pull_number)
    checkRateLimit(response_commits)
    checkRateLimit(response_pr)
    return (response_pr.json(), response_commits.json())

def checkRateLimit(response):
    error = "API rate limit exceeded"
    if response.status_code == 403:
        if error in response.text:
            raise Exception(error)

if __name__ == "__main1__":
    response = get_compare_tags("SonarSource", "sonarqube", "6.2", "6.2.1")
    #pp.pprint(response.json()["commits"])
    shas = []
    msgshas = []
    commits = response.json()["commits"]
    for commit in commits:
        shas.append(commit["sha"])
        msgshas.append((commit["commit"]["message"], commit["sha"]))
    pp.pprint(shas)

if __name__ == "__main1__":
    res = get_pull_request_data("SonarSource", "sonarqube", 1808)
    pp.pprint(res)

PR_OFFSET = 3201

#Pull requests retriver
if __name__ == "__main1__":
    with ThreadPoolExecutor() as executor:
        data = list()
        futures = set()
        for i in range(PR_OFFSET, 3251):
            futures.add(executor.submit(get_pull_request_data, "SonarSource", "sonarqube", i))
            if(i%50 == 0):
                completed, futures = wait(futures, return_when=ALL_COMPLETED)
                for future in completed:
                    data.append(future.result())
                futures = set()
                with open(f"pull_requests/pull_requests{i}.pkl", "wb") as f:
                    pickle.dump(data, f)
                data = list()
                print(f"Downloaded {i} pull requests...")

    if(i%50 != 0):
        #Handle the last ones
        completed, futures = wait(futures, return_when=ALL_COMPLETED)
        for future in completed:
            data.append(future.result())
        with open(f"pull_requests/pull_requests{i}.pkl", "wb") as f:
                pickle.dump(data, f)

if __name__ == "__main2__":
    tag_dict = {
        "5.4-M7": "5.4-M6",
        "5.4-M8": "5.4-M7",
        "6.3": "6.3.0.18800"
    }
    tagsDf = pd.read_csv("csv/tags.csv", index_col=0) 
    comparisons = []
    i = 0
    for index, row in tagsDf.sort_values(by=["Tag_number", "Date"]).iterrows():
        head_tag = row.Tag
        if head_tag in tag_dict:
            base_tag = tag_dict[row.Tag]
        elif i != 0:
            base_tag = previousTag
        if i != 0:
            response = get_compare_tags("SonarSource", "sonarqube", base_tag, head_tag)
            comparisons.append(response.json())
            print(f"Comparing {base_tag} and {head_tag}: {response.status_code}...")
        previousTag = row.Tag
        if(i%50 == 0):
            print(f"Downloaded {i} comparisons...")
        i += 1
    with open(f"pkl/compare_tags.pkl", "wb") as f:
        pickle.dump(comparisons, f)

if __name__ == "__main1__":
    import os.path
    from os import path
    import datetime
    import time

    tagsDf = pd.read_csv("csv/tags.csv", index_col=0)
    tagsDf.Date = pd.to_datetime(tagsDf.Date)
    tagsDf = tagsDf[tagsDf.Date > pd.to_datetime(datetime.date(2015,3,10))]

    BACKWARDS_TRIES = 10
    FORWARD_TRIES = 10
    folder = "pkl/compare_tags"

    #Load file with already tried combinations
    already_tried_tags_versions = []
    tried_combinations = ""
    if path.exists(f"{folder}/compare_tags_combination_log.txt"):
        with open(f"{folder}/compare_tags_combination_log.txt", "r") as a_file:
            for line in a_file:
                stripped_line = line.strip()
                tried_combinations = tried_combinations + stripped_line + "\n" 
                already_tried_tags_versions.append(stripped_line)

    comparisons = []
    with ThreadPoolExecutor() as executor:
        tags = list(tagsDf.sort_values(by=["Tag_number", "Date"]).Sha)
        futures = set()
        for i, head_tag in enumerate(tags):
            #Backwards
            start_index = 0 if i-BACKWARDS_TRIES < 0 else i-BACKWARDS_TRIES
            for j in range(start_index, i):
                if f"{tags[j]}:{head_tag}" in already_tried_tags_versions:
                    continue
                futures.add(executor.submit(get_compare_tags, "SonarSource", "sonarqube", tags[j], head_tag))  
                #print(f"Comparing {tags[j]} and {head_tag}...")
                tried_combinations = tried_combinations + f"{tags[j]}:{head_tag}\n"
            #Forward
            end_index = len(tags) if i+FORWARD_TRIES > len(tags) else i+FORWARD_TRIES
            if i == len(tags):
                continue
            for j in range(i+1, end_index):
                if f"{tags[j]}:{head_tag}" in already_tried_tags_versions:
                    continue
                futures.add(executor.submit(get_compare_tags, "SonarSource", "sonarqube", tags[j], head_tag))  
                #print(f"Comparing {tags[j]} and {head_tag}...")
                tried_combinations = tried_combinations + f"{tags[j]}:{head_tag}\n"
            completed, futures = wait(futures, return_when=ALL_COMPLETED)
            for future in completed:
                response = future.result()
                if response.status_code != 200:
                    if not "url" in response.json():
                        pp.pprint(response.json())
                        print(f"Failed call")
                        continue
                    else:
                        url = response.json()["url"]
                        print(f"Failed call with {response.status_code} code: {url}")
                        continue
                #empty commits
                response = response.json()
                response["commits"] = []
                comparisons.append(response)
            futures = set()
            
            if len(comparisons) == 0:
                continue
            
            time.sleep(1)
            with open(f"{folder}/compare_tags_combination_log.txt", "a") as f:
                f.write(tried_combinations)
                tried_combinations = ""   
            print(f"Saving {len(comparisons)} comparisons...")
            with open(f"{folder}/compare_tags_combination{i}.pkl", "wb") as f:
                pickle.dump(comparisons, f)
                comparisons = []

if __name__ == "__main__":
     response = get_compare_tags("SonarSource", "sonarqube", "0dc7f1ec", "87ca68d")
     print(response)