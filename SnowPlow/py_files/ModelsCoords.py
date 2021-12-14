import pandas as pd
from geopy import distance
import requests # to call the openmap/google apis
import json
import datetime
import math
import itertools
import numpy as np
import json
import osmnx as ox
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests
import networkx as nx
from pulp import *
import seaborn as sn
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform

df = pd.read_csv("Cluster.csv")
df.head()
dataPart1 = df.head(10)

df = dataPart1

selected_columns = df[["Latitude","Longitude"]]

df0 = selected_columns.copy()

subset = df0[['Latitude', 'Longitude']]
tuples = [tuple(x) for x in subset.to_numpy()]
# print(tuples)
coordinates_array = np.array(tuples)
dist_array = pdist(coordinates_array)

dist_matrix = squareform(dist_array)

distances = pd.DataFrame(dist_matrix, columns = ['0','1','2','3','4','5','6','7','8','9'])

df0['Coords'] = list(zip(df0['Latitude'],df0['Longitude']))
df0['ID'] = df0.index

location = dict( ( ID, (df0.loc[ID, 'Latitude'], df0.loc[ID, 'Longitude']) ) for ID in df0.index)

for i in location:
    lo = location[i]
    plt.plot(lo[0], lo[1], 'o')
    plt.text(lo[0] + .01, lo[1], i, horizontalalignment='center',
             verticalalignment='center')

plt.gca().axis('off')

nodeDist = dict( ((i,j), distances.iloc[i, j] ) for i in location for j in location if i != j)


vehicles = 3

prob=LpProblem("vehicle", LpMinimize)

#indicates if location i is connected to location j along route
indicator = LpVariable.dicts('indicator',nodeDist, 0,1,LpBinary)
#elimiate subtours
eliminator = LpVariable.dicts('eliminator', df0.ID, 0, len(df0.ID)-1, LpInteger)

cost = lpSum([indicator[(i,j)]*nodeDist[(i,j)] for (i,j) in nodeDist])
prob+=cost

for v in df0.ID:
    cap = 1 if v != 8 else vehicles
    # inward possible route
    prob += lpSum([indicator[(i, v)] for i in df0.ID if (i, v) in indicator]) == cap
    # outward possible route
    prob += lpSum([indicator[(v, i)] for i in df0.ID if (v, i) in indicator]) == cap

# subtour elimination
num = len(df0.ID) / vehicles
for i in df0.ID:
    for j in df0.ID:
        if i != j and (i != 8 and j != 8) and (i, j) in indicator:
            prob += eliminator[i] - eliminator[j] <= (num) * (1 - indicator[(i, j)]) - 1

%time prob.solve()
print(LpStatus[prob.status])

feasible_edges = [ e for e in indicator if value(indicator[e]) != 0 ]

def get_next_loc(initial):
    '''to get the next edge'''
    edges = [e for e in feasible_edges if e[0]==initial]
    for e in edges:
        feasible_edges.remove(e)
    return edges

routes = get_next_loc(8)
routes = [ [e] for e in routes ]

for r in routes:
    while r[-1][1] !=8:
        r.append(get_next_loc(r[-1][1])[-1])

print(routes)

coloured_loc = [np.random.rand(3) for i in range(len(routes))]
for r,co in zip(routes,coloured_loc):
    for a,b in r:
        l1,l2 = location[a], location[b]
        plt.plot([l1[0],l2[0]],[l1[1],l2[1]], color=co)

# outline the routes
coloured_loc = [np.random.rand(3) for i in range(len(routes))]
for r, co in zip(routes, coloured_loc):
    for a, b in r:
        l1, l2 = location[a], location[b]
        plt.plot([l1[0], l2[0]], [l1[1], l2[1]], color=co)
for l in location:
    lo = location[l]
    plt.plot(lo[0], lo[1], 'o')
    plt.text(lo[0] + .01, lo[1], l, horizontalalignment='center', verticalalignment='center')

plt.title('%d ' % vehicles + 'Vehicle routes' if vehicles > 1 else 'Vehicle route')
plt.xlabel('Left')
plt.ylabel('Right')
plt.show()

df2 = df0[['Latitude', 'Longitude', 'ID']].copy()

order1 = [8,0,6,7,8]
order2 = [8,1,4,5,8]
order3 = [8,3,9,2,8]

df3 = pd.DataFrame()
for i in order1:
    df3 = df3.append(df2.loc[i])


df4 = pd.DataFrame()
for i in order2:
    df4 = df4.append(df2.loc[i])

df5 = pd.DataFrame()
for i in order3:
    df5 = df5.append(df2.loc[i])


df3.reset_index(inplace = True)
df4.reset_index(inplace = True)
df5.reset_index(inplace = True)
df3 = df3.append(df3.loc[0])
df4 = df4.append(df4.loc[0])
df5 = df5.append(df5.loc[0])

df3.reset_index(inplace = True)
long2 = []
lat2 = []
for i in df3.index:
    long2.append(df3.loc[i]["Longitude"])
    lat2.append(df3.loc[i]["Latitude"])

df4.reset_index(inplace = True)
long3 = []
lat3 = []
for i in df4.index:
    long3.append(df4.loc[i]["Longitude"])
    lat3.append(df4.loc[i]["Latitude"])

df5.reset_index(inplace = True)
long4 = []
lat4 = []
for i in df5.index:
    long4.append(df5.loc[i]["Longitude"])
    lat4.append(df5.loc[i]["Latitude"])

def plot_path(lat, long, origin_point, destination_point):
    fig = go.Figure(go.Scattermapbox(
        name = "Path",
        mode = "lines",
        lon = long,
        lat = lat,
        marker = {'size': 10},
        line = dict(width = 4.5, color = 'grey')))
    fig.add_trace(go.Scattermapbox(
        name = "Source",
        mode = "markers",
        lon = [origin_point[1]],
        lat = [origin_point[0]],
        marker = {'size': 12, 'color':"red"}))
    fig.add_trace(go.Scattermapbox(
        name = "Destination",
        mode = "markers",
        lon = [destination_point[1]],
        lat = [destination_point[0]],
        marker = {'size': 12, 'color':'green'}))
    lat_center = np.mean(lat)
    long_center = np.mean(long)
    fig.update_layout(mapbox_style="carto-darkmatter",
        mapbox_center_lat = 30, mapbox_center_lon=-80)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                      mapbox = {
                          'center': {'lat': lat_center,
                          'lon': long_center},
                          'zoom': 13})
    fig.show()

origin_point2 = (df3.loc[0]["Latitude"], df3.loc[0]["Longitude"])
destination_point2 = (df3.loc[0]["Latitude"], df3.loc[0]["Longitude"])

origin_point3 = (df4.loc[0]["Latitude"], df4.loc[0]["Longitude"])
destination_point3 = (df4.loc[0]["Latitude"], df4.loc[0]["Longitude"])

origin_point4 = (df5.loc[0]["Latitude"], df5.loc[0]["Longitude"])
destination_point4 = (df5.loc[0]["Latitude"], df5.loc[0]["Longitude"])


plot_path(lat2, long2, origin_point2, destination_point2)
plot_path(lat3, long3, origin_point3, destination_point3)
plot_path(lat4, long4, origin_point4, destination_point4)
