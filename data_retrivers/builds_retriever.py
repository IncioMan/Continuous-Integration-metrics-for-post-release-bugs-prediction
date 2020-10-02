import pprint
import pickle
from travis import get_builds

PROJECT_ID = "234484"
OFFSET_SIZE = 100
NUMBER_BUILDS_TO_SKIP = 0
DEST_FOLDER = "test"

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(depth=6)
    current_builds = []
    i = NUMBER_BUILDS_TO_SKIP
    n_builds = 0
    while True:
        response = get_builds(PROJECT_ID, {"offset": i*OFFSET_SIZE, "limit": OFFSET_SIZE})
        current_builds = current_builds + response["builds"]
        n_builds = n_builds + len(response["builds"])
        i+=1
        if(len(response["builds"])==0 or n_builds % 1000 == 0):
            print(f"Downloaded builds: {n_builds}...")
            with open(f'{DEST_FOLDER}/builds{n_builds}.pkl', 'wb') as f:
                pickle.dump(current_builds, f)
            if(len(response["builds"]) == 0):
                break
            current_builds = []   
    print(n_builds)