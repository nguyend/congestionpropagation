"""
Author: Hoang Nguyen
Email: hoang.nguyen@data61.csiro.au
Paper: Nguyen, H., Liu, W. and Chen, F., 2017. Discovering congestion propagation patterns in spatio-temporal traffic data. IEEE Transactions on Big Data, 3(2), pp.169-180.
"""

def timebetween(start,end, snapshots):
    """
    Extract all the snapshots between a period of a day
    :param start: start time (e.g. '08:00')
    :param end: end time (e.g. '09:00')
    :param snapshots:
    :return: snapshots covered by the period of day
    """
    included = []
    for i in range(0,len(snapshots)):
        time = snapshots[i][11:16]
        #print(time)
        if time <= end and time >=start:
            included.append(i)
    return included

def DBN_causal(causaltree, longer_pairs, start, end, children):
    """
    Calculate probability for a tree structure between any start and end time
    :param causaltree: connected causal congestion tree
    :param longer_pairs: all snapshots with congestions information
    :param start: start time
    :param end: end time
    :param children:
    :return: probability score
    """
    causalpair = []
    allpair = [(x,y) for x in causaltree for y in causaltree]
    for pair in allpair:
        print(pair)
        if pair[0] in children[pair[1]-1]:
            causalpair.append(pair)
    timeperiod = longer_pairs[start:end]
    prob = float(1.0)
    for pair in causalpair:
        currentsnapshot = 0
        nextsnapshot = 0
        for i in range(0,len(timeperiod)-1):
            if pair[0] in timeperiod[i]:
                currentsnapshot+=1
                if pair[1] in timeperiod[i+1]:
                    nextsnapshot+=1
        if currentsnapshot>0:
            prob = prob*nextsnapshot/float(currentsnapshot)
    return prob

def DBN_causal_between(causaltree, longer_pairs, children, times):
    """
    Calculate probability for a tree structure between any start and end time of the day
    :param causaltree: connected causal congestion tree
    :param longer_pairs: all snapshots with congestions information
    :param children:
    :param times: all snapshot index of times included in the period of day
    :return: probability
    """
    causalpair = []
    allpair = [(x,y) for x in causaltree for y in causaltree]
    for pair in allpair:
        #print(pair)
        if pair[0] in children[pair[1]-1]:
            causalpair.append(pair)

    prob = float(1.0)
    print(causalpair)
    for pair in causalpair:
        currentsnapshot = 0
        nextsnapshot = 0
        for time in times:
            if time==len(longer_pairs)-1:
                break
            if pair[0] in longer_pairs[time]:
                currentsnapshot+=1
                if pair[1] in longer_pairs[time+1]:
                    nextsnapshot+=1
        if currentsnapshot>0:
            prob = prob*nextsnapshot/float(currentsnapshot)
    return prob