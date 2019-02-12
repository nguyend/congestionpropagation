"""
Please cite the following paper when using the code, the sample data is aggregated and added a random shift from original one.
Author: Hoang Nguyen
Email: dungbk04@gmail.com
Paper: Nguyen, H., Liu, W. and Chen, F., 2017. Discovering congestion propagation patterns in spatio-temporal traffic data. IEEE Transactions on Big Data, 3(2), pp.169-180.

@article{nguyen2017discovering,
  title={Discovering congestion propagation patterns in spatio-temporal traffic data},
  author={Nguyen, Hoang and Liu, Wei and Chen, Fang},
  journal={IEEE Transactions on Big Data},
  volume={3},
  number={2},
  pages={169--180},
  year={2017},
  publisher={IEEE}
}
"""

import gmplot
import scipy.io as spio
from Apriori import *
from DBN_causal import *
from math import ceil
#read data from matlab format, use 90 percentile to detect congested segments
causal90 = spio.loadmat('matdata/causal90pc.mat', squeeze_me=True)

#Location of site and its index
ListOfLongLat = causal90['ListOfLongLat']
indexsite = ListOfLongLat[:,0].tolist()
longs = [row[1] for row in ListOfLongLat]
lats = [row[2] for row in ListOfLongLat]

def refinelist(rlist):
    """
    Convert single integer item in list to list [[1,2],3,[4,5]] -> [[1,2],[3],[4,5]]
    :param rlist:
    :return: list
    """
    for i in range(0,len(rlist)):
        if isinstance(rlist[i], int):
            rlist[i] = [rlist[i]]
    return rlist

#A segment is defined by a pair of sites (Origin and Destination); pair_ids are all road segments in the network (587 segments)
#A segment is referenced by index of pair_ids (0-586)
pair_ids = causal90['pair_ids']

#children of a pair are its outflow segments
#Python indexing starts at 0, rather than 1 (which is how Matlab does it), hence we need to minus 1 when use index
children = causal90['children']
children = refinelist(children)
#parents of a pair are its inflow segments
parents = causal90['parents']
parents = refinelist(parents)
compress_parent = causal90['compress_parent']

#longer_pairs are segment with travel time > threshold percentile which are considered as congested segments at a snapshot
#longer_pairs are input to build congestion propagation trees
longer_pairs = causal90['longer_pairs']
longer_pairs = refinelist(longer_pairs)

#index time of snapshots
time_removed = causal90['time_removed']

def combine(snapshot):
    """
    Combine trees within a snapshot which have the same root
    Keep the same root and union all other branches from the trees
    All trees in the output snapshot should have different first elements (root)
    :param snapshot:
    :return: combined snapshot
    """
    getconnect = True
    while len(snapshot)>1 and getconnect==True:
        getconnect = False
        i=0
        while i < (len(snapshot)-1):
            treei = snapshot[i]
            j = i+1
            while (j<len(snapshot)):
                treej = snapshot[j]
                if treei[0]==treej[0]:
                    combinetree = list(set().union(treei[1:],treej[1:]))
                    combinetree.insert(0,treei[0])
                    if treei in snapshot:
                        snapshot.remove(treei)
                    if treej in snapshot:
                        snapshot.remove(treej)
                    snapshot.append(combinetree)
                    getconnect = True
                j+=1
            i+=1
    return snapshot

def construct_scts():
    """
    Main function to build congestion propagation trees (Algorithm 2 in Nguyen et. al. (2016) paper
    :return:causal congestion trees with root as first congested segment that caused consequential congestions in
    the following snapshots.
    """
    previous_snapshot = []
    STCtrees = [[]]*len(time_removed)
    for i in range(len(longer_pairs)-1,0,-1):
        congestions = longer_pairs[i]
        #Proceed to next snapshot if there is no congestion
        if len(congestions)==0:
            STCtrees[i] = []
            previous_snapshot = []
            continue

        if len(previous_snapshot)==0:
            previous_snapshot = [[congestion] for congestion in congestions]
            STCtrees[i] = previous_snapshot[:]
            continue
        new_snapshot = []
        used_trees = []
        for congestion in congestions:
            usecongestion = False
            for tree in previous_snapshot:
                if congestion in children[tree[0]-1]:
                    used_trees.append(tree)
                    new_tree = tree[:]
                    new_tree.insert(0,congestion)
                    new_snapshot.append(new_tree)
                    usecongestion = True
            if usecongestion == False:
                new_snapshot.append([congestion])

        #combine tree with same root in each snapshot
        new_snapshot = combine(new_snapshot)
        STCtrees[i] = new_snapshot[:]
        try:
            #remove used tree from previous snapshot
            for used_tree in used_trees:
                if used_tree in previous_snapshot:
                    previous_snapshot.remove(used_tree)
        except Exception, e:
            print str(e)

        STCtrees[i+1] = previous_snapshot[:]
        previous_snapshot = new_snapshot[:]
    return STCtrees

def plot_stc(stctrees):
    """
    Plot congestions on Google Map with root marked as 1
    :param STCtreesfinal:
    :return: mymap.html
    """
    gmap = gmplot.GoogleMapPlotter(-37.805857, 144.967230, 14)
    for tree in stctrees:
        j=1
        for branch in tree:
            segment = pair_ids[branch-1]
            origin = indexsite.index(segment[0])
            destination = indexsite.index(segment[1])
            if j==1:
                gmap.plot([lats[origin],lats[destination]], [longs[origin],longs[destination]], 'red', edge_width=5)
                gmap.marker(lats[origin],longs[origin],color="#FF0000",label=str(j), title = str(branch))
            else:
                gmap.plot([lats[origin],lats[destination]], [longs[origin],longs[destination]], 'cornflowerblue', edge_width=5)
            j+=1
    gmap.draw("mymap.html")

def uniondata(STCTrees):
    """
    Combine congestion trees in all snapshot to input into frequent mining algorithm
    :param STCTrees:
    :return: all trees
    """
    alltree = []
    for snapshot in STCTrees:
        for tree in snapshot:
            if len(tree)>3:
                alltree.append(tree)
    return alltree

if __name__ == '__main__':
    STCtreesfinal = construct_scts()
    #Visualise some results
    alltrees = uniondata(STCtreesfinal)
    frequents, support = apriori(alltrees,0.01)
    trees2view = []
    for key in support.keys():
        if len(key)>5:
            tree = list(key)
            frequent = ceil(support[key]*len(alltrees))
            print(tree, frequent)
            if (frequent > 18):
                trees2view.append(tree)
    plot_stc(trees2view)

    prob1 = DBN_causal(trees2view[0],longer_pairs,100,200,children)

    times = timebetween('17:00','18:00', time_removed)
    prob2 = DBN_causal_between(trees2view[0],longer_pairs,children, times)
    print(prob1,prob2)
