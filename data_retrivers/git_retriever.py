import requests
import pprint
import pickle
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
pp = pprint.PrettyPrinter(depth=6)

_BASE_URL = "https://api.github.com/"
GITHUB_TOKEN = "e0776a1059e8702da7e1ee7ad3facd806374bd07"

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
    return response

def get_pull_request(owner, repo, pull_number):
    query = f"repos/{owner}/{repo}/pulls/{pull_number}"
    response = _request(endpoint=query)
    return response

def get_pull_request_commits(owner, repo, pull_number):
    query = f"repos/{owner}/{repo}/pulls/{pull_number}/commits?per_page=1000"
    response = _request(endpoint=query)
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

PR_OFFSET = 1401

#Pull requests retriver
if __name__ == "__main__":
    with ThreadPoolExecutor() as executor:
        data = list()
        futures = set()
        for i in range(PR_OFFSET, 3250):
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

    #Handle the last ones
    completed, futures = wait(futures, return_when=ALL_COMPLETED)
    for future in completed:
        data.append(future.result())
    with open(f"pull_requests/pull_requests{i}.pkl", "wb") as f:
            pickle.dump(data, f)
    """shas = []
    msgshas = []
    for commit in response:
        shas.append(commit["sha"])
        msgshas.append((commit["commit"]["message"], commit["sha"]))
    pp.pprint(shas)"""