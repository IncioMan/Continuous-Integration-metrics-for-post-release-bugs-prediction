
from multiprocessing import Pool, Queue
import git
import pandas as pd
git = git.Git("../../sonarqube/")

def find_git_commit(row):
    res = git.log("--all", f"--grep={row} ")
    if res != "":
        return row
    return None

if __name__ == "__main__":
    issues_df = pd.read_csv(f"../csv/issues.csv", index_col=0)
    issues_df.edition = issues_df.edition.replace(" ", "Empty value").fillna("Empty value")
    pool = Pool()  # Create a multiprocessing Pool
    #tuples_to_ = list(issues_df[issues_df.edition.isna()].head(10)[["issue_key"]].to_records(index=False))
    tuples_to_ = issues_df[issues_df.edition == "Empty value"].issue_key.values
    res = pool.map(find_git_commit, tuples_to_)
    keys = [key for key in res if key != None]
    community_issues = issues_df[issues_df.issue_key.isin(keys)]
    print(len(community_issues))
    community_issues.to_csv(f"../csv/community_issues_from_git.csv")
    exit()