import pandas as pd
import pickle
import json
import seaborn as sns
import pprint
import numpy as np
import math

def get_builds_from_commits(_commits):
    _build_ids = jobs[jobs.commitsha.isin(_commits)].buildid
    return builds[(builds.id.isin(_build_ids))]

def get_builds_from_ids(_builds, _build_ids):
    return _builds[(_builds.id.isin(_build_ids))]

def get_commits_from_comparison_row(row, commitsDf):
    _x = commitsDf
    return _x[(_x.from_tag == row.from_tag) & (_x.to_tag == row.to_tag)].commitsha

def detect_build_bursts(_builds, gap_size, burst_size, states):
    print(len(_builds))
    positive_count = 0
    negative_count = 0
    n_bursts = 0
    burst_sizes = []
    i = 0
    for index, row in _builds.sort_values(by="started_at").iterrows():
        i+=1
        if((i == len(_builds)) | (not (row.state in states))):
            negative_count+=1
            if(negative_count == gap_size):
                if(positive_count >= burst_size):
                    n_bursts+=1
                    burst_sizes.append(positive_count)
                negative_count = 0
                positive_count = 0
        if(row.state in states):
            positive_count+=1
    return n_bursts, burst_sizes

def build_burst_metrics(row):
    gap_size = 1
    burst_size = 2
    states = ["errored","failed","canceled"]
    
    _commits = get_commits_from_comparison_row(row, tags_iterative_pr_commits)
    _builds = get_builds_from_commits(_commits)
    _builds = builds_commitref[builds_commitref.id.isin(_builds.id)]
    data=[]
    for commitref in _builds.commitref.unique():
        _ref_builds = _builds[_builds.commitref==commitref]
        data.append(detect_build_bursts(_ref_builds, gap_size, burst_size, states))
    bursts = np.array([])
    bursts_size = np.array([])
    for d in data:
        bursts = np.append(bursts,d[0])
        for v in d[1]:
            bursts_size = np.append(bursts_size,v) 
    return (bursts.mean(), bursts_size.mean())

if __name__ == "__main__":

    csv_folder = "csv"

    tags_comparison = pd.read_csv(f"{csv_folder}/tags_comparison_final_updated_no_rc_and_milestones.csv", index_col=0)
    tags_comparison.from_commit_date = pd.to_datetime(tags_comparison.from_commit_date)
    tags_comparison.to_commit_date = pd.to_datetime(tags_comparison.to_commit_date)
    tags_comparison.from_author_date = pd.to_datetime(tags_comparison.from_author_date)
    tags_comparison.to_author_date = pd.to_datetime(tags_comparison.to_author_date)
    tags_comparison = tags_comparison[2:]

    tags_iterative_pr_commits = pd.read_csv(f"{csv_folder}/commits_for_tags/tags_pairs_iterative_commits.csv", index_col=0)

    builds = pd.read_csv(f"{csv_folder}/builds_cleaned.csv", index_col=0)

    jobs = pd.read_csv(f"{csv_folder}/allJobs.csv", index_col=0)
    for datefield in ["started_at","created_at","finished_at","updated_at"]:
        jobs[f"{datefield}"] = pd.to_datetime(jobs[f"{datefield}"])

    builds_commitref = jobs.drop_duplicates(subset=["buildid", "commitref", "commitsha"], keep="first")[["buildid", "commitref", "commitsha"]]\
    .merge(builds, left_on="buildid", right_on="id")

    _commits = get_commits_from_comparison_row(tags_comparison.loc[35], tags_iterative_pr_commits)
    _builds = get_builds_from_commits(_commits)

    gap_size = 1
    burst_size = 2
    states = ["errored","failed","canceled"]
    #res = detect_build_bursts(get_builds_from_ids(builds_commitref, _builds.id), gap_size, burst_size, states )
    #print(res)
    res = build_burst_metrics(tags_comparison.loc[35])
    print(res)