import json
import os
import requests
from time import sleep
from urllib.parse import urlencode

headers = { \
    "Content-Type": "application/json", \
    "Accept": "application/vnd.travis-ci.2.1+json",
    "User-Agent": "CiData",
    #"Authorization": "token {}".format(os.environ["TRAVIS_TOKEN"])
}

_BASE_URL = "https://api.travis-ci.org/"
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

def get_builds(params = {}):
    """ Returns builds for a repository 
    see https://docs.travis-ci.com/api/#builds"""
    
    response = _request(endpoint="builds?{}".format(urlencode(params)))
    if response.status_code == 200:
        return response.json()

def get_repo(repo_identifier):
    """ Returns information about a repository 
    see https://docs.travis-ci.com/api/#repositories"""

    response = _request(endpoint="repos/{}".format(repo_identifier))
    if response.status_code == 200:
        return response.json()

if __name__ == "__main1__":
    import pprint
    import pickle
    pp = pprint.PrettyPrinter(depth=6)
    current_builds = []
    i = 0
    n_builds = 0
    initial_number = 11996
    while True:
        response = get_builds(params={"repository_id": "234484", "after_number": initial_number - 25*i})
        current_builds = current_builds + response["builds"]
        n_builds = n_builds + len(response["builds"])
        i+=1
        if(len(response["builds"])==0 or n_builds % 1000 == 0):
            print(f"Downloaded builds: {n_builds}...")
            with open(f'builds/v2/builds{n_builds}.pkl', 'wb') as f:
                pickle.dump(current_builds, f)
            if(len(response["builds"]) == 0):
                break
            current_builds = []   
    print(n_builds)

if __name__ == "__main1__":
    import pickle
    with open('builds/v2/builds11995.pkl', 'rb') as f:
        builds = pickle.load(f)
        print(len(builds))

if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter(depth=6)
    response = get_builds(params={"repository_id": "234484", "number": '112036'})
    pp.pprint(response['builds'])