##
## Name of the file: LPRoute.py
# The setup:
# install pandas, numpy, pulp, networkx, matplotlib, haversine using 'pip install'.
# LPRoute.py generates paths for 'V' number of vehicles to be deployed given nodes
# which replicates locations that need to be covered by that vehicle in the form of a graph.
# This file uses synthetic graphs (which are in the form of Random Geometric Graphs RGG)
# as its input and prints the routes that can be taken by 'V' vehicles.
# In addition to the route paths for each vehicle this code also indicates whether or
# not there is an optimal solution given a synthetic graph and if there isn't one,
# it prints "infeasible solution".
# It also generates the enumerated nodes, total number of iterations, time taken in terms
# of CPU seconds and wall clock seconds.
# Once the required tools are installed, you can edit the number of vehicles to be deployed in this file
# by changing the value of 'V' or just run it on any python editor or using command line python LPRoute.py.
# Python version: Python 3.8.3
# To see these paths and outputs in more detail, see Routes with synthetic graph.ipynb

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
from pulp import *
import haversine as hs


## To Generate a Synthetic graph
# with 10 nodes having a density of 0.3
# storing the random geometric graph in G.
G = nx.random_geometric_graph(10, 0.3)
## pos stores node attributes from G.
pos = nx.get_node_attributes(G, "pos")
## dmin: helps break the loop, min required.
dmin = 1
## ncenter: stores node updates post calculation.
ncenter = 0
for n in pos:
    ## x,y : are the cordinate positons for a node.
    x, y = pos[n]
    ## d: stores the distance using the distance formula used between point (0.5,0.5)  and (x,y).
    d = (x - 0.5) ** 2 + (y - 0.5) ** 2
    if d < dmin:
        ncenter = n
        dmin = d
## p: is a dictionarty that stores node information taken from random geometric graphs
## and the updates made to each node after calculation.
p = dict(nx.single_source_shortest_path_length(G, ncenter))
## figsize: This controls the endproduct of the figure.
plt.figure(figsize=(8, 8))
nx.draw_networkx_edges(G, pos, nodelist=[ncenter], alpha=0.4)
nx.draw_networkx_nodes(
    G,
    pos,
    ## nodelist: list of nodes with their cordinates.
    nodelist=list(p.keys()),
    ## node_size: declares the node size.
    node_size=80,
    ## node_color: assigns color to depict a node.
    node_color=list(p.values()),
    ## cmap: responsible for the plot by storing all.
    cmap=plt.cm.Reds_r,
)
plt.xlim(-0.05, 1.05)
plt.ylim(-0.05, 1.05)
plt.axis("off")
plt.show()
## ll: indicates the left or x cordinate.
ll = list()
for i in pos:
    ll.append(pos[i][0])
plt.show()
## rr: indicates the right or y cordinate.
rr = list()
for i in pos:
    rr.append(pos[i][1])
## df: creates a dataframe to store the cordinate information and unique indexes to represent these.
df = pd.DataFrame()
df['Left'] = ll
df['Right'] = rr
df['coordinate'] = list(zip(df['Left'],df['Right']))
df['ID'] = df.index


def dist_from(loc1,loc2):
    ##@dist_from
    # Calculates the distance loc1 and loc2 provided in the arguments
    # @param
    # loc1: This stores coordinates of the first node.
    # loc2: This stores coordinates of the second node.
    # @return
    # Returns the distance using haversine
    dist=hs.haversine(loc1,loc2)
    return round(dist,2)
    
for _,row in df.iterrows():
    df[row.ID]=df['coordinate'].apply(lambda x: dist_from(row.coordinate,x))

## distances_df: This slices the original dataframe for information from columns 4-4183 which
## includes cordinate infromation and their unique indexes.
distances_df=df.iloc[:,4:4183]
## distances_df.index=df.ID.
distances_df.insert(0, 'ID', df.ID)

dist_dict={}

## locations: This stores the required node information (x/left,y/right cordinates and index) in the form a dictionary.
locations = dict( ( ID, (df.loc[ID, 'Left'], df.loc[ID, 'Right']) ) for ID in df.index)
locations

for l in locations:
    ## lo: This stores a single location from the dictionary being dealt with at a time.
    lo = locations[l]
    plt.plot(lo[0],lo[1],'o')
    plt.text(lo[0]+.01,lo[1],l,horizontalalignment='center',verticalalignment='center')    
plt.gca().axis('off');

## df1: dataframe used to drop cordinate information and unique indexes to store values and dates.
df1 = pd.DataFrame()
df1 = df
df1 = df1.drop(['Left'],axis=1)
df1 = df1.drop(['Right'],axis=1)
df1 = df1.drop(['coordinate'],axis=1)
df1 = df1.drop(['ID'],axis=1)
## distance: Stores values left in dataframe df1.
distance = df1
## distances: is a ditionary used to store distances from each node to all the other nodes in the graph.
distances = dict( ((l1,l2), distance.iloc[l1, l2] ) for l1 in locations for l2 in locations if l1!=l2)

## V: Indicates the number of vehicles to be deployed to visit the paths.
V = 3
## prob: Creating the problem initialization using Linear Programming that will use constraints.
prob=LpProblem("vehicle", LpMinimize)
## indicator: The indicator variable that defines distances in a dictionary.
indicator = LpVariable.dicts('indicator',distances, 0,1,LpBinary)
## eliminator: The eliminator to remove revisting nodes already visited.
eliminator = LpVariable.dicts('eliminator', df.ID, 0, len(df.ID)-1, LpInteger)
## cost: sets up the objective by storing results of distance calculations of a single node with all the others.
cost = lpSum([indicator[(i,j)]*distances[(i,j)] for (i,j) in distances])
prob+=cost

## Setting up constraints for each to check if the vehicle can visit the node
for v in df.ID:
    ## cap: Takes a single node at a time
    cap = 1 if v != 7 else V
    #inward possible route
    prob+= lpSum([ indicator[(i,v)] for i in df.ID if (i,v) in indicator]) ==cap
    #outward possible route
    prob+=lpSum([ indicator[(v,i)] for i in df.ID if (v,i) in indicator]) ==cap

## To eliminate subtours
num=len(df.ID)/V
for i in df.ID:
    for j in df.ID:
        if i != j and (i != 7 and j!= 7) and (i,j) in indicator:
            prob += eliminator[i] - eliminator[j] <= (num)*(1-indicator[(i,j)]) - 1
            
            
prob.solve()

## feasibleedges: This stores values of edges that can be reached in a tour by a vehicle along the path.
feasible_edges = [ e for e in indicator if value(indicator[e]) != 0 ]

def get_next_loc(initial):
    ##@get_next_loc
    # This calculates the next edge to be traversed along the path for a vehicle.
    # @param
    # initial: The first/previous node in the tour/path.
    # @return
    # Returns the next edge to be taken to reach a particular node/locations
    edges = [e for e in feasible_edges if e[0]==initial]
    for e in edges:
        feasible_edges.remove(e)
    return edges

## routes: Stores path information.
routes = get_next_loc(7)
routes = [ [e] for e in routes ]

for r in routes:
    while r[-1][1] !=7:
        r.append(get_next_loc(r[-1][1])[-1])

## coloured_loc: This stores information for node paths seperated with different colours to indicate seperate paths
## taken by each path outlining these routes.
coloured_loc = [np.random.rand(3) for i in range(len(routes))]
for r,co in zip(routes,coloured_loc):
    for a,b in r:
        l1,l2 = locations[a], locations[b]
        plt.plot([l1[0],l2[0]],[l1[1],l2[1]], color=co)
for l in locations:
    lo = locations[l]
    plt.plot(lo[0],lo[1],'o')
    plt.text(lo[0]+.01,lo[1],l,horizontalalignment='center',verticalalignment='center')
    
## Prints the number of vehcile routes /route generated in a graph fromat along the x (left) and y (right) axes
plt.title('%d '%V + 'Vehicle routes' if V > 1 else 'Vehicle route')
plt.xlabel('Left')
plt.ylabel('Right')
## Displaying the graph
plt.show()