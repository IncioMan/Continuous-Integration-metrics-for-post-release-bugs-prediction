import requests
import pprint
pp = pprint.PrettyPrinter(depth=6)

_BASE_URL = "https://api.github.com/"
GITHUB_TOKEN = "f8f52658ba126656a20398edf8e1bce05fc089cc"

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

if __name__ == "__main__":
    response = get_compare_tags("SonarSource", "sonarqube", "6.2", "6.2.1")
    #pp.pprint(response.json()["commits"])
    shas = []
    for commit in response.json()["commits"]:
        shas.append(commit["commit"]["tree"]["sha"])
    print(shas)