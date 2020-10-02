from jira import JIRA
import pickle

DEST_FOLDER = "pkl"

if __name__ == "__main__":
    jira = JIRA('https://jira.sonarsource.com/')    
    #download all issues
    size = 100
    initial = 0
    issue_tuples = []
    all_issues = []
    while True:
        start= initial*size
        issues = jira.search_issues('project=SONAR',  start,size)
        all_issues = all_issues + issues
        if len(issues) == 0:
            break
        initial += 1

    with open(f'{DEST_FOLDER}/issues.pkl', 'wb') as f:
            pickle.dump(all_issues, f)