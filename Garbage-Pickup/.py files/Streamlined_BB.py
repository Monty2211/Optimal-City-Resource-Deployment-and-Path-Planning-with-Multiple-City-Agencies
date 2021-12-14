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
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

bb1 = [35.588654,35.591812,-78.808848,-78.806101]
bb2 = [35.581702,35.584546,-78.800222,-78.797915]
bb = []
bb.append(bb1)
bb.append(bb2)
bb3 = [35.596373,35.598830,-78.784815,-78.782240]
bb4 = [35.598926,35.600409,-78.784841,-78.782202]
bb.append(bb3)
bb.append(bb4)

nodelist = []
for i in range(4):
    north, south, east, west = bb[i][0],bb[i][1],bb[i][2],bb[i][3]    
    G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
    nodelist.append(G.nodes)
    
separatednodelist = []
for i in nodelist:
    for j in i:
        #print(j)
        separatednodelist.append(j)

import pandas as pd
data = pd.DataFrame(separatednodelist)
data.rename(columns = {0:'Nodes'}, inplace = True)

data1 = pd.DataFrame()
data1.rename(columns = {0:'Nodes'}, inplace = True)
for i in range(4):
    north, south, east, west = bb[i][0],bb[i][1],bb[i][2],bb[i][3]    
    G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
    Nodes = []
    for i in G.nodes:
        Nodes.append(i)
    lat1 = []
    long1 = []
    data2 = pd.DataFrame(Nodes)
    data2.rename(columns = {0:'Nodes'}, inplace = True)
    for i in Nodes:
        lat1.append(G.nodes[i].get('y'))
        long1.append(G.nodes[i].get('x'))
    data2['Latitude'] = lat1
    data2['Longitude'] = long1     
    data1 = data1.append(data2, ignore_index=True)

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
        
        
long = [] 
lat = []  
for i in data1.index:
    long.append(data1.loc[i]["Longitude"])
    lat.append(data1.loc[i]["Latitude"])
origin_point = (data1.loc[0]["Latitude"], data1.loc[0]["Longitude"]) 
destination_point = (data1.iloc[-1]["Latitude"], data1.iloc[-1]["Longitude"]) 
plot_path(lat, long, origin_point, destination_point)

finalroutes = []

for i in range(4):
    
    #Creating a bounding box
    north, south, east, west = bb[i][0],bb[i][1],bb[i][2],bb[i][3]    
    G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='lightgray', node_size=5)


    #Extracting Node Information from G
    Nodes = []
    for i in G.nodes:
        Nodes.append(i)

    data = pd.DataFrame(Nodes)
    data.rename(columns = {0:'Nodes'}, inplace = True)

    lat1 = []
    long1 = []
    for i in Nodes:
        lat1.append(G.nodes[i].get('y'))
        long1.append(G.nodes[i].get('x'))
    data['Latitude'] = lat1
    data['Longitude'] = long1
    df1 = data


    df1 = df1.drop(['Nodes'],axis=1)
    df1.rename(columns = {'Latitude':'Left'}, inplace = True)
    df1.rename(columns = {'Longitude':'Right'}, inplace = True)

    #Calculating Distance and the distance matrix for all coordinates in the Bounding Box
    df3 = pd.DataFrame()
    for j in df1.index:
        list1 = []
        for i in df1.index:
            r = requests.get(f"""http://router.project-osrm.org/route/v1/car/{df1.loc[j, "Right"]},{df1.loc[j, "Left"]};{df1.loc[i, "Right"]},{df1.loc[i, "Left"]}?overview=false""")
            list1.append(json.loads(r.content)["routes"][0]["distance"])
        df3[j] = list1
    df = df1
    df['coordinate'] = list(zip(df['Right'],df['Left']))
    df['ID'] = df.index

    locations = dict( ( ID, (df.loc[ID, 'Right'], df.loc[ID, 'Left']) ) for ID in df.index)
    distances_df = df3
    distance = distances_df
    distances = dict( ((l1,l2), distance.iloc[l1, l2] ) for l1 in locations for l2 in locations if l1!=l2)


    ## V: This defines the total number of vehicles that will traverse the path.
    V = 1
    ## prob: This initializes the problem that will run using provided constraints.

    prob=LpProblem("vehicle", LpMinimize)
    ## indicator: This defines the variable dictionary consisting of distances and indicates if location i is connected to location j along route
    indicator = LpVariable.dicts('indicator',distances, 0,1,LpBinary)
    ## eliminator: This defines the variable dictionary consisting of the node ID's and elimiate subtours
    eliminator = LpVariable.dicts('eliminator', df.ID, 0, len(df.ID)-1, LpInteger)
    ## cost: This stores the result of distances calculations.
    cost = lpSum([indicator[(i,j)]*distances[(i,j)] for (i,j) in distances])
    prob+=cost

    start1 = 2
    for v in df.ID:
        ## cap: This considers a particular node at a time. 
        cap = 1 if v != start1 else V
        #inward possible route
        prob+= lpSum([ indicator[(i,v)] for i in df.ID if (i,v) in indicator]) ==cap
        #outward possible route
        prob+=lpSum([ indicator[(v,i)] for i in df.ID if (v,i) in indicator]) ==cap
    ## num: This stores the result of the number of nodes and the number of vehicles.    
    num=len(df.ID)/V
    for i in df.ID:
        for j in df.ID:
            if i != j and (i != start1 and j!= start1) and (i,j) in indicator:
                prob += eliminator[i] - eliminator[j] <= (num)*(1-indicator[(i,j)]) - 1         
    prob.solve()
    ## feasibleedges: This stores values of edges after the calculations are done.
    feasible_edges = [ e for e in indicator if value(indicator[e]) != 0 ]
    ##@get_next_loc
    # This provides with the next coordinates for the next node in the path.
    def get_next_loc(initial):
        edges = [e for e in feasible_edges if e[0]==initial]
        for e in edges:
            feasible_edges.remove(e)
        return edges
    ## routes: This stores information regarding paths.    
    routes = get_next_loc(2)
    routes = [ [e] for e in routes ]

    for r in routes:
        while r[-1][1] !=start1:
            r.append(get_next_loc(r[-1][1])[-1])
    ## coloured_loc: This stores information according to individual paths.        
    coloured_loc = [np.random.rand(3) for i in range(len(routes))]
    for r,co in zip(routes,coloured_loc):
        for a,b in r:
            l1,l2 = locations[a], locations[b]
            plt.plot([l1[0],l2[0]],[l1[1],l2[1]], color=co)
    for l in locations:
        lo = locations[l]
        plt.plot(lo[0],lo[1],'o')
        plt.text(lo[0]+.01,lo[1],l,horizontalalignment='center',verticalalignment='center')


    plt.title('%d '%V + 'Vehicle routes' if V > 1 else 'Vehicle route')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.show()        
    finalroutes.append(routes)
    print(routes)



    df2 = df[['Left', 'Right', 'ID']].copy()
    df2.rename(columns = {'Left':'Latitude'}, inplace = True)
    df2.rename(columns = {'Right':'Longitude'}, inplace = True)
    a=[]
    for i in range(data.index.stop):
        print(routes[0][i][0])
        a.append(routes[0][i][0]) 

    df3 = pd.DataFrame()
    for i in a:
        df3 = df3.append(df2.loc[i])

    df3.reset_index(inplace = True)

    df3 = df3.append(df3.loc[0])
    df3.reset_index(inplace = True)
    long2 = [] 
    lat2 = []  
    for i in df3.index:
        long2.append(df3.loc[i]["Longitude"])
        lat2.append(df3.loc[i]["Latitude"])

    origin_point2 = (df3.loc[0]["Latitude"], df3.loc[0]["Longitude"]) 
    destination_point2 = (df3.loc[0]["Latitude"], df3.loc[0]["Longitude"])
    plot_path(lat2, long2, origin_point2, destination_point2)

import matplotlib.pyplot as plt 
G = ox.graph_from_place('Fuquay Varina, NC, USA', network_type='drive')
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='lightgray', node_size=5)

box1 = pd.DataFrame(nodelist[0])
route1 = [2,1,6,0,5,7,8,4,3]
box1.rename(columns = {0:'Nodes'}, inplace = True)
lat1 = []
long1 = []
for i in nodelist[0]:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
box1['Latitude'] = lat1
box1['Longitude'] = long1
bbox1 = pd.DataFrame()
for i in route1:
    bbox1 = bbox1.append(box1.loc[i])
bbox1.reset_index(inplace = True)

nodes = [195438253, 195438255, 195438631, 195447516, 195447518, 195447520, 195500922, 195594836]
box2 = pd.DataFrame(nodes)
route2 = [2,5,4,3,7,0,1,6]
box2.rename(columns = {0:'Nodes'}, inplace = True)
lat1 = []
long1 = []
for i in nodes:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
box2['Latitude'] = lat1
box2['Longitude'] = long1
bbox2 = pd.DataFrame()
for i in route2:
    bbox2 = bbox2.append(box2.loc[i])
bbox2.reset_index(inplace = True)

box3 = pd.DataFrame(nodelist[2])
route3 = [2,17,18,15,19,13,14,16,0,12,1,6,5,7,9,10,11,8,3,4]
box3.rename(columns = {0:'Nodes'}, inplace = True)
lat1 = []
long1 = []
for i in nodelist[2]:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
box3['Latitude'] = lat1
box3['Longitude'] = long1
bbox3 = pd.DataFrame()
for i in route3:
    bbox3 = bbox3.append(box3.loc[i])
bbox3.reset_index(inplace = True)

bb4 = [35.598926,35.600409,-78.784841,-78.782202]
north, south, east, west = 35.598926,35.600409,-78.784841,-78.782202
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
box4 = pd.DataFrame(nodelist[3])
route4 = [2,6,1,0,4,3,7,5]
box4.rename(columns = {0:'Nodes'}, inplace = True)
lat1 = []
long1 = []
for i in nodelist[3]:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
box4['Latitude'] = lat1
box4['Longitude'] = long1
bbox4 = pd.DataFrame()
for i in route4:
    bbox4 = bbox4.append(box4.loc[i])
bbox4.reset_index(inplace = True)

G = ox.graph_from_place('Fuquay Varina, NC, USA', network_type='drive')
path1_2 = nx.shortest_path(G, bbox1.iloc[-1]['Nodes'],bbox2.iloc[0]['Nodes'], weight='travel_time')
bboxm1 = pd.DataFrame(path1_2)
bboxm1.rename(columns = {0:'Nodes'}, inplace = True)
lat1 = []
long1 = []
for i in path1_2:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
bboxm1['Latitude'] = lat1
bboxm1['Longitude'] = long1

path2_3 = nx.shortest_path(G, bbox2.iloc[-1]['Nodes'],bbox3.iloc[0]['Nodes'], weight='travel_time')
bboxm2 = pd.DataFrame(path2_3)
bboxm2.rename(columns = {0:'Nodes'}, inplace = True)
lat1 = []
long1 = []
for i in path2_3:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
bboxm2['Latitude'] = lat1
bboxm2['Longitude'] = long1

path3_4 = nx.shortest_path(G, bbox3.iloc[-1]['Nodes'],bbox4.iloc[0]['Nodes'], weight='travel_time')
bboxm3 = pd.DataFrame(path3_4)
bboxm3.rename(columns = {0:'Nodes'}, inplace = True)
lat1 = []
long1 = []
for i in path3_4:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
bboxm3['Latitude'] = lat1
bboxm3['Longitude'] = long1

path2_4 = nx.shortest_path(G, bbox2.iloc[-1]['Nodes'],bbox4.iloc[0]['Nodes'], weight='travel_time')
bboxm4 = pd.DataFrame(path2_4)
bboxm4.rename(columns = {0:'Nodes'}, inplace = True)
lat1 = []
long1 = []
for i in path2_4:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
bboxm4['Latitude'] = lat1
bboxm4['Longitude'] = long1

finalpath1 = pd.concat([bbox1, bboxm1, bbox2, bboxm4, bbox4],axis=0)
finalpath1.reset_index(inplace = True)
long = [] 
lat = []  
for i in finalpath1.index:
    long.append(finalpath1.loc[i]["Longitude"])
    lat.append(finalpath1.loc[i]["Latitude"])
origin_point = (finalpath1.loc[0]["Latitude"], finalpath1.loc[0]["Longitude"]) 
destination_point = (finalpath1.iloc[-1]["Latitude"], finalpath1.iloc[-1]["Longitude"])
plot_path(lat, long, origin_point, destination_point)