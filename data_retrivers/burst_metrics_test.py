def detect_build_bursts(_builds, gap_size,\
                        burst_size, states):
    positive_count = 0
    #used to count the gap size
    negative_count = 0
    n_bursts = 0
    burst_sizes = []
    i = 0
    for row in _builds:
        i+=1
        #not part of the burst
        if (not (row["state"] in states)):
            negative_count+=1
            #check if burst is terminated
            if(negative_count == gap_size):
                if(positive_count >= burst_size):
                    n_bursts+=1
                    burst_sizes.append(positive_count)
                negative_count = 0
                positive_count = 0
        #part of the burst
        if(row["state"] in states):
            positive_count+=1
            negative_count = 0
            #end of the loop
            if(i == len(_builds)):
                if(positive_count >= burst_size):
                    n_bursts+=1
                    burst_sizes.append(positive_count)
    return n_bursts, burst_sizes

if __name__ == "__main__":
    builds = [{"state": "canceled"}, 
                {"state": "passed"},
                {"state": "canceled"},
                 {"state": "passed"},
                {"state": "canceled"},
                {"state": "passed"},
                {"state": "passed"},
                {"state": "canceled"},
                {"state": "passed"},
                {"state": "passed"}]
    print(detect_build_bursts(builds, 2, 3,"canceled"))