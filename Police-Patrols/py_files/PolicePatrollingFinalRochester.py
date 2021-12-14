import osmnx as ox
import matplotlib.pyplot as plt
import pandas as pd
from geopy import distance
import requests
import json
import datetime
import math
import itertools
import numpy as np
import networkx as nx
import plotly.graph_objects as go
from pulp import *
import seaborn as sn
import osmnx as ox
import matplotlib.pyplot as plt
import pandas as pd
from geopy import distance
import requests
import json
import datetime
import math
import itertools
import numpy as np
import networkx as nx
import plotly.graph_objects as go
from pulp import *
import seaborn as sn
import geopandas as gpd
from geopandas.tools import geocode
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
locator = Nominatim(user_agent="myGeocoder")


# FIRST AGAIN____
# Creating a bounding box
north, south, east, west = 43.142237, 43.147200, -77.648127, -77.645767
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='lightgray', node_size=5)

# Extracting Node Information from G
Nodes = []
for i in G.nodes:
    Nodes.append(i)

data = pd.DataFrame(Nodes)
data.rename(columns={0: 'Nodes'}, inplace=True)

lat1 = []
long1 = []
for i in Nodes:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
data['Latitude'] = lat1
data['Longitude'] = long1
df1 = data

df1 = df1.drop(['Nodes'], axis=1)
df1.rename(columns={'Latitude': 'Left'}, inplace=True)
df1.rename(columns={'Longitude': 'Right'}, inplace=True)

# Calculating Distance and the distance matrix for all coordinates in the Bounding Box
df3 = pd.DataFrame()
for j in df1.index:
    list1 = []
    for i in df1.index:
        r = requests.get(
            f"""http://router.project-osrm.org/route/v1/car/{df1.loc[j, "Right"]},{df1.loc[j, "Left"]};{df1.loc[i, "Right"]},{df1.loc[i, "Left"]}?overview=false""")
        list1.append(json.loads(r.content)["routes"][0]["distance"])
    df3[j] = list1
df = df1
df['coordinate'] = list(zip(df['Right'], df['Left']))
df['ID'] = df.index

locations = dict((ID, (df.loc[ID, 'Right'], df.loc[ID, 'Left'])) for ID in df.index)
distances_df = df3
distance = distances_df
distances = dict(((l1, l2), distance.iloc[l1, l2]) for l1 in locations for l2 in locations if l1 != l2)

## V: This defines the total number of vehicles that will traverse the path.
V = 1
## prob: This initializes the problem that will run using provided constraints.

prob = LpProblem("vehicle", LpMinimize)
## indicator: This defines the variable dictionary consisting of distances and indicates if location i is connected to location j along route
indicator = LpVariable.dicts('indicator', distances, 0, 1, LpBinary)
## eliminator: This defines the variable dictionary consisting of the node ID's and elimiate subtours
eliminator = LpVariable.dicts('eliminator', df.ID, 0, len(df.ID) - 1, LpInteger)
## cost: This stores the result of distances calculations.
cost = lpSum([indicator[(i, j)] * distances[(i, j)] for (i, j) in distances])
prob += cost

start1 = 2
for v in df.ID:
    ## cap: This considers a particular node at a time.
    cap = 1 if v != start1 else V
    # inward possible route
    prob += lpSum([indicator[(i, v)] for i in df.ID if (i, v) in indicator]) == cap
    # outward possible route
    prob += lpSum([indicator[(v, i)] for i in df.ID if (v, i) in indicator]) == cap
    ## num: This stores the result of the number of nodes and the number of vehicles.
num = len(df.ID) / V
for i in df.ID:
    for j in df.ID:
        if i != j and (i != start1 and j != start1) and (i, j) in indicator:
            prob += eliminator[i] - eliminator[j] <= (num) * (1 - indicator[(i, j)]) - 1
prob.solve()
## feasibleedges: This stores values of edges after the calculations are done.
feasible_edges = [e for e in indicator if value(indicator[e]) != 0]


##@get_next_loc
# This provides with the next coordinates for the next node in the path.
def get_next_loc(initial):
    edges = [e for e in feasible_edges if e[0] == initial]
    for e in edges:
        feasible_edges.remove(e)
    return edges
    ## routes: This stores information regarding paths.


routes = get_next_loc(start1)
routes = [[e] for e in routes]

for r in routes:
    while r[-1][1] != start1:
        r.append(get_next_loc(r[-1][1])[-1])

df2 = df[['Left', 'Right', 'ID']].copy()
df2.rename(columns={'Left': 'Latitude'}, inplace=True)
df2.rename(columns={'Right': 'Longitude'}, inplace=True)
a = []
for i in range(data.index.stop):
    # print(routes[0][i][0])
    a.append(routes[0][i][0])

df3 = pd.DataFrame()
for i in a:
    df3 = df3.append(df2.loc[i])

df3.reset_index(inplace=True)

df3 = df3.append(df3.loc[0])
df3.reset_index(inplace=True)
df4 = df3
dfnodes = pd.DataFrame(Nodes)
dfnodes.rename(columns={0: 'Nodes'}, inplace=True)
dfnodes = dfnodes.reindex(a)
dfnodes = dfnodes.append({"Nodes": Nodes[a[0]]}, ignore_index=True)
df4 = pd.concat([df4, dfnodes], axis=1)


def node_list_to_path2(G, node_list):
    edge_nodes = list(zip(node_list[:-1], node_list[1:]))
    lines = []
    newlist = []

    # for u, v in edge_nodes:
    #    if(G.get_edge_data(u, v)):
    #        newlist.append((u,v))

    for u, v in edge_nodes:
        if (G.get_edge_data(u, v)):
            newlist.append((u, v))
        else:
            path1 = nx.shortest_path(G, u, v, weight='travel_time')
            path2 = list(zip(path1[:-1], path1[1:]))
            newlist = newlist + path2
            # print(newlist)
    # print(len(newlist))

    for u, v in newlist:
        # if there are parallel edges, select the shortest in length

        data = min(G.get_edge_data(u, v).values(),
                   key=lambda x: x['length'])
        # if it has a geometry attribute
        if 'geometry' in data:
            # add them to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            # if it doesn't have a geometry attribute,
            # then the edge is a straight line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines.append(line)

    return lines


def plot_path(lat, long, origin_point, destination_point):
    fig = go.Figure(go.Scattermapbox(
        name="Path",
        mode="lines",
        lon=long,
        lat=lat,
        marker={'size': 10},
        line=dict(width=4.5, color='grey')))
    fig.add_trace(go.Scattermapbox(
        name="Source",
        mode="markers",
        lon=[origin_point[1]],
        lat=[origin_point[0]],
        marker={'size': 12, 'color': "red"}))
    fig.add_trace(go.Scattermapbox(
        name="Destination",
        mode="markers",
        lon=[destination_point[1]],
        lat=[destination_point[0]],
        marker={'size': 12, 'color': 'green'}))
    lat_center = np.mean(lat)
    long_center = np.mean(long)
    fig.update_layout(mapbox_style="carto-darkmatter",
                      mapbox_center_lat=30, mapbox_center_lon=-80)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox={
                          'center': {'lat': lat_center,
                                     'lon': long_center},
                          'zoom': 13})
    fig.show()


pathlist = []
for i in range(df4['Nodes'].count() - 1):
    path1 = nx.shortest_path(G, df4.iloc[i]['Nodes'], df4.iloc[i + 1]['Nodes'], weight='travel_time')
    pathlist = pathlist + path1
# pathlist1 = list(dict.fromkeys(pathlist))
# pathlist1.append(pathlist1[0])
data4 = pd.DataFrame(pathlist)
data4.rename(columns={0: 'Nodes'}, inplace=True)
lat1 = []
long1 = []
lines = node_list_to_path2(G, pathlist)
long2 = []
lat2 = []
for i in range(len(lines)):
    z = list(lines[i])
    l1 = list(list(zip(*z))[0])
    l2 = list(list(zip(*z))[1])
    for j in range(len(l1)):
        long2.append(l1[j])
        lat2.append(l2[j])
for i in pathlist:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
data4['Latitude'] = lat1
data4['Longitude'] = long1
origin_point = (data4.loc[0]["Latitude"], data4.loc[0]["Longitude"])
destination_point = (data4.iloc[-1]["Latitude"], data4.iloc[-1]["Longitude"])
# plot_path(lat1, long1, origin_point, destination_point)


plot_path(lat2, long2, origin_point, destination_point)


path1=pathlist
node_loc_duration = []
for i in range(data4.index.stop-1):
    r = requests.get(f"""http://router.project-osrm.org/route/v1/car/{data4.loc[i, "Longitude"]},{data4.loc[i, "Latitude"]};{data4.loc[i+1, "Longitude"]},{data4.loc[i+1, "Latitude"]}?overview=false""")
    node_loc_duration.append(json.loads(r.content)["routes"][0]["duration"])

node_loc_duration
path1

# Creating a bounding box
north, south, east, west = 43.143614, 43.149031, -77.642269, -77.640467
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='lightgray', node_size=5)

# Extracting Node Information from G
Nodes = []
for i in G.nodes:
    Nodes.append(i)

data = pd.DataFrame(Nodes)
data.rename(columns={0: 'Nodes'}, inplace=True)
# G = ox.graph_from_place('Rochester, NY, USA', network_type='drive')

lat1 = []
long1 = []
for i in Nodes:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
data['Latitude'] = lat1
data['Longitude'] = long1
df1 = data

df1 = df1.drop(['Nodes'], axis=1)
df1.rename(columns={'Latitude': 'Left'}, inplace=True)
df1.rename(columns={'Longitude': 'Right'}, inplace=True)

# Calculating Distance and the distance matrix for all coordinates in the Bounding Box
df3 = pd.DataFrame()
for j in df1.index:
    list1 = []
    for i in df1.index:
        r = requests.get(
            f"""http://router.project-osrm.org/route/v1/car/{df1.loc[j, "Right"]},{df1.loc[j, "Left"]};{df1.loc[i, "Right"]},{df1.loc[i, "Left"]}?overview=false""")
        list1.append(json.loads(r.content)["routes"][0]["distance"])
    df3[j] = list1
df = df1
df['coordinate'] = list(zip(df['Right'], df['Left']))
df['ID'] = df.index

locations = dict((ID, (df.loc[ID, 'Right'], df.loc[ID, 'Left'])) for ID in df.index)
distances_df = df3
distance = distances_df
distances = dict(((l1, l2), distance.iloc[l1, l2]) for l1 in locations for l2 in locations if l1 != l2)

## V: This defines the total number of vehicles that will traverse the path.
V = 1
## prob: This initializes the problem that will run using provided constraints.

prob = LpProblem("vehicle", LpMinimize)
## indicator: This defines the variable dictionary consisting of distances and indicates if location i is connected to location j along route
indicator = LpVariable.dicts('indicator', distances, 0, 1, LpBinary)
## eliminator: This defines the variable dictionary consisting of the node ID's and elimiate subtours
eliminator = LpVariable.dicts('eliminator', df.ID, 0, len(df.ID) - 1, LpInteger)
## cost: This stores the result of distances calculations.
cost = lpSum([indicator[(i, j)] * distances[(i, j)] for (i, j) in distances])
prob += cost

start1 = 2
for v in df.ID:
    ## cap: This considers a particular node at a time.
    cap = 1 if v != start1 else V
    # inward possible route
    prob += lpSum([indicator[(i, v)] for i in df.ID if (i, v) in indicator]) == cap
    # outward possible route
    prob += lpSum([indicator[(v, i)] for i in df.ID if (v, i) in indicator]) == cap
    ## num: This stores the result of the number of nodes and the number of vehicles.
num = len(df.ID) / V
for i in df.ID:
    for j in df.ID:
        if i != j and (i != start1 and j != start1) and (i, j) in indicator:
            prob += eliminator[i] - eliminator[j] <= (num) * (1 - indicator[(i, j)]) - 1
prob.solve()
## feasibleedges: This stores values of edges after the calculations are done.
feasible_edges = [e for e in indicator if value(indicator[e]) != 0]


##@get_next_loc
# This provides with the next coordinates for the next node in the path.
def get_next_loc(initial):
    edges = [e for e in feasible_edges if e[0] == initial]
    for e in edges:
        feasible_edges.remove(e)
    return edges
    ## routes: This stores information regarding paths.


routes = get_next_loc(start1)
routes = [[e] for e in routes]

for r in routes:
    while r[-1][1] != start1:
        r.append(get_next_loc(r[-1][1])[-1])

df2 = df[['Left', 'Right', 'ID']].copy()
df2.rename(columns={'Left': 'Latitude'}, inplace=True)
df2.rename(columns={'Right': 'Longitude'}, inplace=True)
a = []
for i in range(data.index.stop):
    # print(routes[0][i][0])
    a.append(routes[0][i][0])

df3 = pd.DataFrame()
for i in a:
    df3 = df3.append(df2.loc[i])

df3.reset_index(inplace=True)

df3 = df3.append(df3.loc[0])
df3.reset_index(inplace=True)
df4 = df3
dfnodes = pd.DataFrame(Nodes)
dfnodes.rename(columns={0: 'Nodes'}, inplace=True)
dfnodes = dfnodes.reindex(a)
dfnodes = dfnodes.append({"Nodes": Nodes[a[0]]}, ignore_index=True)
df4 = pd.concat([df4, dfnodes], axis=1)


def node_list_to_path2(G, node_list):
    edge_nodes = list(zip(node_list[:-1], node_list[1:]))
    lines = []
    newlist = []

    # for u, v in edge_nodes:
    #    if(G.get_edge_data(u, v)):
    #        newlist.append((u,v))

    for u, v in edge_nodes:
        if (G.get_edge_data(u, v)):
            newlist.append((u, v))
        else:
            path1 = nx.shortest_path(G, u, v, weight='travel_time')
            path2 = list(zip(path1[:-1], path1[1:]))
            newlist = newlist + path2
            # print(newlist)
    # print(len(newlist))

    for u, v in newlist:
        # if there are parallel edges, select the shortest in length

        data = min(G.get_edge_data(u, v).values(),
                   key=lambda x: x['length'])
        # if it has a geometry attribute
        if 'geometry' in data:
            # add them to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            # if it doesn't have a geometry attribute,
            # then the edge is a straight line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines.append(line)

    return lines


def plot_path(lat, long, origin_point, destination_point):
    fig = go.Figure(go.Scattermapbox(
        name="Path",
        mode="lines",
        lon=long,
        lat=lat,
        marker={'size': 10},
        line=dict(width=4.5, color='grey')))
    fig.add_trace(go.Scattermapbox(
        name="Source",
        mode="markers",
        lon=[origin_point[1]],
        lat=[origin_point[0]],
        marker={'size': 12, 'color': "red"}))
    fig.add_trace(go.Scattermapbox(
        name="Destination",
        mode="markers",
        lon=[destination_point[1]],
        lat=[destination_point[0]],
        marker={'size': 12, 'color': 'green'}))
    lat_center = np.mean(lat)
    long_center = np.mean(long)
    fig.update_layout(mapbox_style="carto-darkmatter",
                      mapbox_center_lat=30, mapbox_center_lon=-80)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox={
                          'center': {'lat': lat_center,
                                     'lon': long_center},
                          'zoom': 13})
    fig.show()


pathlist = []
for i in range(df4['Nodes'].count() - 1):
    path1 = nx.shortest_path(G, df4.iloc[i]['Nodes'], df4.iloc[i + 1]['Nodes'], weight='travel_time')
    pathlist = pathlist + path1
# pathlist1 = list(dict.fromkeys(pathlist))
# pathlist1.append(pathlist1[0])
data4 = pd.DataFrame(pathlist)
data4.rename(columns={0: 'Nodes'}, inplace=True)
lat1 = []
long1 = []
lines = node_list_to_path2(G, pathlist)
long2 = []
lat2 = []
for i in range(len(lines)):
    z = list(lines[i])
    l1 = list(list(zip(*z))[0])
    l2 = list(list(zip(*z))[1])
    for j in range(len(l1)):
        long2.append(l1[j])
        lat2.append(l2[j])
for i in pathlist:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
data4['Latitude'] = lat1
data4['Longitude'] = long1
origin_point = (data4.loc[0]["Latitude"], data4.loc[0]["Longitude"])
destination_point = (data4.iloc[-1]["Latitude"], data4.iloc[-1]["Longitude"])
# plot_path(lat1, long1, origin_point, destination_point)


plot_path(lat2, long2, origin_point, destination_point)


path2=pathlist
node_loc_duration2 = []
for i in range(data4.index.stop-1):
    r = requests.get(f"""http://router.project-osrm.org/route/v1/car/{data4.loc[i, "Longitude"]},{data4.loc[i, "Latitude"]};{data4.loc[i+1, "Longitude"]},{data4.loc[i+1, "Latitude"]}?overview=false""")
    node_loc_duration2.append(json.loads(r.content)["routes"][0]["duration"])


node_loc_duration2

# Creating a bounding box
north, south, east, west = 43.142049, 43.144241, -77.646089, -77.641239
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='lightgray', node_size=5)

# Extracting Node Information from G
Nodes = []
for i in G.nodes:
    Nodes.append(i)

data = pd.DataFrame(Nodes)
data.rename(columns={0: 'Nodes'}, inplace=True)
# G = ox.graph_from_place('Rochester, NY, USA', network_type='drive')

lat1 = []
long1 = []
for i in Nodes:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
data['Latitude'] = lat1
data['Longitude'] = long1
df1 = data

df1 = df1.drop(['Nodes'], axis=1)
df1.rename(columns={'Latitude': 'Left'}, inplace=True)
df1.rename(columns={'Longitude': 'Right'}, inplace=True)

# Calculating Distance and the distance matrix for all coordinates in the Bounding Box
df3 = pd.DataFrame()
for j in df1.index:
    list1 = []
    for i in df1.index:
        r = requests.get(
            f"""http://router.project-osrm.org/route/v1/car/{df1.loc[j, "Right"]},{df1.loc[j, "Left"]};{df1.loc[i, "Right"]},{df1.loc[i, "Left"]}?overview=false""")
        list1.append(json.loads(r.content)["routes"][0]["distance"])
    df3[j] = list1
df = df1
df['coordinate'] = list(zip(df['Right'], df['Left']))
df['ID'] = df.index

locations = dict((ID, (df.loc[ID, 'Right'], df.loc[ID, 'Left'])) for ID in df.index)
distances_df = df3
distance = distances_df
distances = dict(((l1, l2), distance.iloc[l1, l2]) for l1 in locations for l2 in locations if l1 != l2)

## V: This defines the total number of vehicles that will traverse the path.
V = 1
## prob: This initializes the problem that will run using provided constraints.

prob = LpProblem("vehicle", LpMinimize)
## indicator: This defines the variable dictionary consisting of distances and indicates if location i is connected to location j along route
indicator = LpVariable.dicts('indicator', distances, 0, 1, LpBinary)
## eliminator: This defines the variable dictionary consisting of the node ID's and elimiate subtours
eliminator = LpVariable.dicts('eliminator', df.ID, 0, len(df.ID) - 1, LpInteger)
## cost: This stores the result of distances calculations.
cost = lpSum([indicator[(i, j)] * distances[(i, j)] for (i, j) in distances])
prob += cost

start1 = 2
for v in df.ID:
    ## cap: This considers a particular node at a time.
    cap = 1 if v != start1 else V
    # inward possible route
    prob += lpSum([indicator[(i, v)] for i in df.ID if (i, v) in indicator]) == cap
    # outward possible route
    prob += lpSum([indicator[(v, i)] for i in df.ID if (v, i) in indicator]) == cap
    ## num: This stores the result of the number of nodes and the number of vehicles.
num = len(df.ID) / V
for i in df.ID:
    for j in df.ID:
        if i != j and (i != start1 and j != start1) and (i, j) in indicator:
            prob += eliminator[i] - eliminator[j] <= (num) * (1 - indicator[(i, j)]) - 1
prob.solve()
## feasibleedges: This stores values of edges after the calculations are done.
feasible_edges = [e for e in indicator if value(indicator[e]) != 0]


##@get_next_loc
# This provides with the next coordinates for the next node in the path.
def get_next_loc(initial):
    edges = [e for e in feasible_edges if e[0] == initial]
    for e in edges:
        feasible_edges.remove(e)
    return edges
    ## routes: This stores information regarding paths.


routes = get_next_loc(start1)
routes = [[e] for e in routes]

for r in routes:
    while r[-1][1] != start1:
        r.append(get_next_loc(r[-1][1])[-1])

df2 = df[['Left', 'Right', 'ID']].copy()
df2.rename(columns={'Left': 'Latitude'}, inplace=True)
df2.rename(columns={'Right': 'Longitude'}, inplace=True)
a = []
for i in range(data.index.stop):
    # print(routes[0][i][0])
    a.append(routes[0][i][0])

df3 = pd.DataFrame()
for i in a:
    df3 = df3.append(df2.loc[i])

df3.reset_index(inplace=True)

df3 = df3.append(df3.loc[0])
df3.reset_index(inplace=True)
df4 = df3
dfnodes = pd.DataFrame(Nodes)
dfnodes.rename(columns={0: 'Nodes'}, inplace=True)
dfnodes = dfnodes.reindex(a)
dfnodes = dfnodes.append({"Nodes": Nodes[a[0]]}, ignore_index=True)
df4 = pd.concat([df4, dfnodes], axis=1)


def node_list_to_path2(G, node_list):
    edge_nodes = list(zip(node_list[:-1], node_list[1:]))
    lines = []
    newlist = []

    # for u, v in edge_nodes:
    #    if(G.get_edge_data(u, v)):
    #        newlist.append((u,v))

    for u, v in edge_nodes:
        if (G.get_edge_data(u, v)):
            newlist.append((u, v))
        else:
            path1 = nx.shortest_path(G, u, v, weight='travel_time')
            path2 = list(zip(path1[:-1], path1[1:]))
            newlist = newlist + path2
            # print(newlist)
    # print(len(newlist))

    for u, v in newlist:
        # if there are parallel edges, select the shortest in length

        data = min(G.get_edge_data(u, v).values(),
                   key=lambda x: x['length'])
        # if it has a geometry attribute
        if 'geometry' in data:
            # add them to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            # if it doesn't have a geometry attribute,
            # then the edge is a straight line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines.append(line)

    return lines


def plot_path(lat, long, origin_point, destination_point):
    fig = go.Figure(go.Scattermapbox(
        name="Path",
        mode="lines",
        lon=long,
        lat=lat,
        marker={'size': 10},
        line=dict(width=4.5, color='grey')))
    fig.add_trace(go.Scattermapbox(
        name="Source",
        mode="markers",
        lon=[origin_point[1]],
        lat=[origin_point[0]],
        marker={'size': 12, 'color': "red"}))
    fig.add_trace(go.Scattermapbox(
        name="Destination",
        mode="markers",
        lon=[destination_point[1]],
        lat=[destination_point[0]],
        marker={'size': 12, 'color': 'green'}))
    lat_center = np.mean(lat)
    long_center = np.mean(long)
    fig.update_layout(mapbox_style="carto-darkmatter",
                      mapbox_center_lat=30, mapbox_center_lon=-80)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox={
                          'center': {'lat': lat_center,
                                     'lon': long_center},
                          'zoom': 13})
    fig.show()


pathlist = []
for i in range(df4['Nodes'].count() - 1):
    path1 = nx.shortest_path(G, df4.iloc[i]['Nodes'], df4.iloc[i + 1]['Nodes'], weight='travel_time')
    pathlist = pathlist + path1
# pathlist1 = list(dict.fromkeys(pathlist))
# pathlist1.append(pathlist1[0])
data4 = pd.DataFrame(pathlist)
data4.rename(columns={0: 'Nodes'}, inplace=True)
lat1 = []
long1 = []
lines = node_list_to_path2(G, pathlist)
long2 = []
lat2 = []
for i in range(len(lines)):
    z = list(lines[i])
    l1 = list(list(zip(*z))[0])
    l2 = list(list(zip(*z))[1])
    for j in range(len(l1)):
        long2.append(l1[j])
        lat2.append(l2[j])
for i in pathlist:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
data4['Latitude'] = lat1
data4['Longitude'] = long1
origin_point = (data4.loc[0]["Latitude"], data4.loc[0]["Longitude"])
destination_point = (data4.iloc[-1]["Latitude"], data4.iloc[-1]["Longitude"])
# plot_path(lat1, long1, origin_point, destination_point)


plot_path(lat2, long2, origin_point, destination_point)



path3=pathlist

node_loc_duration3 = []
for i in range(data4.index.stop-1):
    r = requests.get(f"""http://router.project-osrm.org/route/v1/car/{data4.loc[i, "Longitude"]},{data4.loc[i, "Latitude"]};{data4.loc[i+1, "Longitude"]},{data4.loc[i+1, "Latitude"]}?overview=false""")
    node_loc_duration3.append(json.loads(r.content)["routes"][0]["duration"])

node_loc_duration3
mainpath=path1+path2+path3
total=node_loc_duration+node_loc_duration2+node_loc_duration3

total
sum(total)

path1
path2
path3

#G = ox.graph_from_place('Rochester, NY, USA', network_type='drive_service')

G = ox.graph_from_place('Rochester, NY', network_type='drive_service')
path12 = nx.shortest_path(G,212673147,212650634, weight='travel_time')
path23 = nx.shortest_path(G,212650634,212624944, weight='travel_time')
path12
path12[1:-1]
path23
path23[1:-1]

mainroute = path1+path12[1:-1]+path2+path23[1:-1]+path3
mainroute1 = []
for i in mainroute:
    mainroute1.append(int(i))

lines = node_list_to_path2(G, mainroute1)
long2 = []
lat2 = []

for i in range(len(lines)):
    z = list(lines[i])
    l1 = list(list(zip(*z))[0])
    l2 = list(list(zip(*z))[1])
    for j in range(len(l1)):
        long2.append(l1[j])
        lat2.append(l2[j])


plot_path(lat2, long2, origin_point, destination_point)
len(mainroute1)

rpd1="Irondequoit Police Department, 1300, Titus Ave, Rochester, NY, 14617"
rpd2="Police Department-Patrol Section Office, 630, North Clinton Avenue, Rochester, NY, 14605"
rpd3="Lake Section, Rochester Police Department, 1099, Jay St 100D, Rochester, NY, 14611"
rpd3="Rochester Police Department Special Operations Division, 261, Child St, Rochester, NY, 14611"
rpd4="New York State Police - Troop E SP Rochester, 1155, Scottsville Rd, Rochester, NY, 14624"
rpd5="East Rochester Police Department, 317, Main St, East Rochester, NY, 14445"
rpd6="Brighton Police Department,2300, Elmwood Ave, Rochester, NY, 14618"
rpd7="Rochester Police Department, 184, Verona St, Rochester, NY, 14608"
rpd8="Rochester Police Department, 185, Exchange Boulevard, Rochester, NY, 14614"
rpd9="Central Section Rochester Police Department, 30, North Clinton Ave, Rochester, NY, 14604"

geolocator = Nominatim(user_agent="example app")

PoliceSitelist = [rpd1,rpd2,rpd3,rpd4,rpd5,rpd6,rpd7,rpd8,rpd9]
pst= pd.DataFrame([rpd.split(",") for rpd in PoliceSitelist])
pst.rename(columns={0: 'Site Name',1: 'Code',2: 'Locality',3: 'Zone',4: 'State',5: 'Pin-Code'}, inplace=True)


pst

pst['Address'] = pst['Code']+pst['Locality']+pst['Zone']+pst['State']+pst['Pin-Code']
pst

geolocator = Nominatim(user_agent="example app")
pst["loc"] = pst["Address"].apply(geolocator.geocode)
pst

geolocator.geocode("630 North Clinton Avenue Rochester NY 14605").point
pst["point"]= pst["loc"].apply(lambda loc: tuple(loc.point) if loc else None)
pst

pst[['lat', 'lon', 'altitude']] = pd.DataFrame(pst['point'].to_list(), index=pst.index)
pst

import folium
map1 = folium.Map(
    location=[43.1125714, -77.4856604],
    tiles='cartodbpositron',
    zoom_start=12,
)
pst.apply(lambda row:folium.CircleMarker(location=[row["lat"], row["lon"]]).add_to(map1), axis=1)
map1

nodes_to_pol = []
for i in pst.index:
    r = requests.get(f"""http://router.project-osrm.org/route/v1/car/{df4.loc[0]["Longitude"]},{df4.loc[0]["Latitude"]};{pst.loc[i]["lon"]},{pst.loc[i]["lat"]}?overview=false""")
    nodes_to_pol.append(json.loads(r.content)["routes"][0]["duration"])

nodes_to_pol
total=node_loc_duration+node_loc_duration2+node_loc_duration3+nodes_to_pol
total

sum(total)

origin_node = ox.nearest_nodes(G,pst.loc[nodes_to_pol.index(min(nodes_to_pol))]["lon"],pst.loc[nodes_to_pol.index(min(nodes_to_pol))]["lat"])

paths_d = nx.shortest_path(G, mainroute[0],origin_node, weight='travel_time')
paths_d

mainroute2 = mainroute1+paths_d

lines = node_list_to_path2(G, mainroute2)
long2 = []
lat2 = []
for i in range(len(lines)):
    z = list(lines[i])
    l1 = list(list(zip(*z))[0])
    l2 = list(list(zip(*z))[1])
    for j in range(len(l1)):
        long2.append(l1[j])
        lat2.append(l2[j])
origin_point = (lat2[0],long2[0])
destination_point = (lat2[0],long2[0])
plot_path(lat2, long2, origin_point, destination_point)

from IPython.display import Image
#Output for traversal of the path becasue the video is not visible on github. The purple circle
#in the middle traverses the path from source to destination in a video form
Image(filename = "Closest-Police-Station.png", width = 700, height = 400)

