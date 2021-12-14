import osmnx as ox
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd
from geopy import distance
import requests # to call the openmap/google apis
import json
import datetime
import math
import itertools
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pulp import *
import seaborn as sn
import osmnx as ox
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd
from geopy import distance
import requests # to call the openmap/google apis
import json
import datetime
import math
import itertools
import numpy as np
import networkx as nx
import osmnx as ox
from shapely.geometry import Point, LineString
import plotly_express as px
import pandas as pd
import geopandas as gpd


prob=LpProblem("vehicle", LpMinimize)
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

rochester_city = ox.geocode_to_gdf('Rochester, NY, USA')
ax = ox.project_gdf(rochester_city).plot()
_ = ax.axis('off')

rochester_graph = ox.graph_from_place('Rochester, NY, USA', network_type='drive')
ox.plot_graph(rochester_graph)

import matplotlib.pyplot as plt
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(rochester_graph, bgcolor='#FFFFFF', node_color=colors[0], edge_color='grey', node_size=5)
# Sample bounding box in Rochester, NY - Plymouth exchange - Mayors Heights
north, south, east, west = 43.133656,43.138291,-77.603903,-77.597766
# create a network from the above bounded box
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='gray', node_size=20)

#Number of nodes within the selected area
print("The number of nodes present in the bounded box selected")
count=0
for i in G.nodes:
    count=count+1
print(count)

print("The locations where cordinates are to be extracted from")
for i in G.nodes:
    print(i)

#Add locations to dataframe
Locations = []
for i in G.nodes:
    Locations.append(i)

roc_data = pd.DataFrame(Locations)
roc_data.rename(columns = {0:'Locations'}, inplace = True)

#Appending lats and longitudes
latitude = []
longitude = []
for i in Locations:
    latitude.append(G.nodes[i].get('y'))
    longitude.append(G.nodes[i].get('x'))
roc_data['Latitude'] = latitude
roc_data['Longitude'] = longitude




#Converting the dataframe to a csv
roc_data.to_csv("BoxAreaRochester.csv")
#Saving in a df
roc_df = pd.read_csv("BoxAreaRochester.csv")
roc_df = roc_df.drop(['Locations'],axis=1)
roc_df.rename(columns = {'Latitude':'Left'}, inplace = True)
roc_df.rename(columns = {'Longitude':'Right'}, inplace = True)

import requests # to call the openmap/google apis -- OSRM for distances
r = requests.get(f"""http://router.project-osrm.org/route/v1/car/{roc_df.loc[0, "Right"]},{roc_df.loc[0, "Left"]};\
{roc_df.loc[6, "Right"]},{roc_df.loc[6, "Left"]}?overview=false""")

import json
df3 = pd.DataFrame()
for j in roc_df.index:
    list1 = []
    for i in roc_df.index:
        r = requests.get(f"""http://router.project-osrm.org/route/v1/car/{roc_df.loc[j, "Right"]},{roc_df.loc[j, "Left"]};{roc_df.loc[i, "Right"]},{roc_df.loc[i, "Left"]}?overview=false""")
        list1.append(json.loads(r.content)["routes"][0]["distance"])
    df3[j] = list1



df = roc_df
df['coordinate'] = list(zip(df['Right'],df['Left']))
df['ID'] = df.index
locations = dict( ( ID, (df.loc[ID, 'Right'], df.loc[ID, 'Left']) ) for ID in df.index)
distances_df = df3
print("Distance Matrix")
print(distances_df)

#bounded box display
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='lightgray', node_size=5)


#Plot points representing location numbers
for l in locations:
    lo = locations[l]
    plt.plot(lo[0], lo[1], 'o')
    plt.text(lo[0] + .01, lo[1], l, horizontalalignment='center', verticalalignment='center')
plt.gca().axis('off');

distance = distances_df
distances = dict( ((l1,l2), distance.iloc[l1, l2] ) for l1 in locations for l2 in locations if l1!=l2)

#MODEL:
V = 2 #the number vehicles/people deployed
#indicates if location i is connected to location j along route
indicator = LpVariable.dicts('indicator',distances, 0,1,LpBinary)
#elimiate subtours
eliminator = LpVariable.dicts('eliminator', df.ID, 0, len(df.ID)-1, LpInteger)
cost = lpSum([indicator[(i,j)]*distances[(i,j)] for (i,j) in distances])
prob+=cost

# constraints
for v in df.ID:
    cap = 1 if v != 11 else V
    # inward possible route
    prob += lpSum([indicator[(i, v)] for i in df.ID if (i, v) in indicator]) == cap
    # outward possible route
    prob += lpSum([indicator[(v, i)] for i in df.ID if (v, i) in indicator]) == cap

# subtour elimination
num = len(df.ID) / V
for i in df.ID:
    for j in df.ID:
        if i != j and (i != 11 and j != 11) and (i, j) in indicator:
            prob += eliminator[i] - eliminator[j] <= (num) * (1 - indicator[(i, j)]) - 1

prob.solve()
print(LpStatus[prob.status])
feasible_edges = [ e for e in indicator if value(indicator[e]) != 0 ]

def get_next_loc(initial):
    '''to get the next edge'''
    edges = [e for e in feasible_edges if e[0]==initial]
    for e in edges:
        feasible_edges.remove(e)
    return edges

routes = get_next_loc(11)
routes = [ [e] for e in routes ]

for r in routes:
    while r[-1][1] !=11:
        r.append(get_next_loc(r[-1][1])[-1])
print("Routes from Model")
print(routes)
routes1 = routes

import numpy as np
#outline the routes
coloured_loc = [np.random.rand(3) for i in range(len(routes))]
for r,co in zip(routes,coloured_loc):
    for a,b in r:
        l1,l2 = locations[a], locations[b]
        plt.plot([l1[0],l2[0]],[l1[1],l2[1]], color=co)

# outline the routes
coloured_loc = [np.random.rand(3) for i in range(len(routes))]
for r, co in zip(routes, coloured_loc):
    for a, b in r:
        l1, l2 = locations[a], locations[b]
        plt.plot([l1[0], l2[0]], [l1[1], l2[1]], color=co)
for l in locations:
    lo = locations[l]
    plt.plot(lo[0], lo[1], 'o')
    plt.text(lo[0] + .01, lo[1], l, horizontalalignment='center', verticalalignment='center')

plt.title('%d ' % V + 'Vehicle routes' if V > 1 else 'Vehicle route')
plt.xlabel('Left')
plt.ylabel('Right')
plt.show()

#OR TOOLS

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distance

    data['num_vehicles'] = 2
    data['depot'] = 11
    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'OR Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)

def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
if __name__ == '__main__':
    main()

#Graph-roc_graph for visualizing boxed routes in Rochester
def create_rochester_graph(loc, dist, transport_mode, loc_type="address"):
    """Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’"""
    if loc_type == "address":
        roc_graph = ox.graph_from_address(loc, dist=dist, network_type=transport_mode)
    elif loc_type == "points":
        roc_graph = ox.graph_from_point(loc, dist=dist, network_type=transport_mode )
    return roc_graph

roc_graph = create_rochester_graph('Rochester', 2500, 'drive_service')
#Paths generated from LP model


path=[212711088,
 6863491042,
 212711081,
 6950355751,
 6950355754,
 212711079,
 8578511237,
 8578511239,
 212627933,
 8077503695,
 3665094176,
 212890741,
 5371345759,
 212630426,
 212863159,
 212663712,
 212654931,
 7302320094,
 5585330044,
 3415688712,
 391967057,
 212690367,
 212745042,
 212890690,
 212772328,
 212762363,
 212714271,
 212838342,
 212859862,
 5746222889,
 212898187,
 212757743,
 8578366709,
 212666680,
 212681097,
 5745948590,
 212685591,
 212685595,
 212631301,
 7085426685,
 212685599,
 212685602,
 6937268311,
 212685604,
 212627367,
 212685619,
 212685624,
 212685628,
 212685631,
 212685635,
 212685639,
 212685642,
 8021283011,
 212685650,
 212685653,
 212685657,
 212685660,
 212685663,
 212685666,
 212643349,
 212685670,
 212685673,
 212685678,
 212685682,
 212685686,
 212685688,
 212685691]

# 11 43.136007, 77.601529
# 4  43.136636, 77.601178
# 7  43.137609,-77.598897
# 0  43.137407,-77.598233
# 18 43.137160,-77.598372
# 1  43.136945,-77.598493
# 6  43.138067,-77.600400
# 9  43.137271,-77.600835
# 8  43.138074,-77.603483
# 3  43.137430,-77.603818

# First Route
# [[(11, 4),(4, 7),(7, 0),(0, 18),(18, 1),(1, 6),(6, 9),(9, 8),(8, 3),(3, 11)],


paths = []
# 11-4
roc_graph = ox.add_edge_speeds(roc_graph)  # Impute
roc_graph = ox.add_edge_travel_times(roc_graph)  # Travel time
source = (43.136007, -77.601529)  # Highland Park
destination = (43.136636, -77.601178)  # West Irondequoit
source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths.append(path)
del paths[0][-1]

# 4-7
paths2 = []
source = (43.136636, -77.601178)
destination = (43.137609, -77.598897)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths2.append(path)
del paths2[0][-1]

# 7-0
paths3 = []
source = (43.137609, -77.598897)
destination = (43.137407, -77.598233)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths3.append(path)
del paths3[0][-1]

# 0-18
paths4 = []
source = (43.137407, -77.598233)
destination = (43.137160, -77.598372)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths4.append(path)
del paths4[0][-1]

# 18-1
paths5 = []
source = (43.137160, -77.598372)
destination = (43.136945, -77.598493)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths5.append(path)
del paths5[0][-1]

# 1-6
paths6 = []
source = (43.136945, -77.598493)
destination = (43.138067, -77.600400)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths6.append(path)
del paths6[0][-1]

# 6-9
paths7 = []
source = (43.138067, -77.600400)
destination = (43.137271, -77.600835)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths7.append(path)
del paths7[0][-1]

# 9-8
paths8 = []
source = (43.137271, -77.600835)
destination = (43.138074, -77.603483)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths8.append(path)
del paths8[0][-1]

# 8-3
paths9 = []
source = (43.138074, -77.603483)
destination = (43.137430, -77.603818)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
paths9.append(path)
# del paths[-1]


final = []
final = paths + paths2 + paths3 + paths4 + paths5 + paths6 + paths7 + paths8 + paths9
final_a = final[0] + final[1] + final[2] + final[3] + final[4] + final[5] + final[6] + final[7] + final[8]

# Plot the route and street networks
ox.plot_graph_route(roc_graph, final_a, route_linewidth=3, node_size=0, bgcolor='k');

# 15  43.135347,-77.601880
# 2   43.134420,-77.602399
# 16  43.133946,-77.603805
# 14  43.134500, -77.599068
# 12  43.135133, -77.598700
# 13  43.135553, -77.598466
# 5   43.135769, -77.598343
# 17  43.136355, -77.598010
# 10  43.136415, -77.597977


# Second Route
# [(11, 15),(15, 2),(2, 16),(16, 14),(14, 12),(12, 13),(13, 5),(5, 17),(17, 10),(10, 11)]]
p = []
# Second Route-
roc_graph = ox.add_edge_speeds(roc_graph)  # Impute
roc_graph = ox.add_edge_travel_times(roc_graph)  # Travel time
# 11-15
source = (43.136007, -77.601529)
destination = (43.135347, -77.601880)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p.append(path)
del p[0][-1]

# 15-2
p2 = []
source = (43.135347, -77.601880)
destination = (43.134420, -77.602399)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p2.append(path)
del p2[0][-1]

# 2-16
p3 = []
source = (43.134420, -77.602399)
destination = (43.133946, -77.603805)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p3.append(path)
del p3[0][-1]

# 16-14
p4 = []
source = (43.133946, -77.603805)
destination = (43.134500, -77.599068)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p4.append(path)
del p4[0][-1]

# 14-12
p5 = []
source = (43.134500, -77.599068)
destination = (43.135133, -77.598700)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p5.append(path)
del p5[0][-1]

# 12-13
p6 = []
source = (43.135133, -77.598700)
destination = (43.135553, -77.598466)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p6.append(path)
del p6[0][-1]

# 13-5
p7 = []
source = (43.135553, -77.598466)
destination = (43.135769, -77.598343)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p7.append(path)
del p7[0][-1]

# 5-17
p8 = []
source = (43.135769, -77.598343)
destination = (43.136355, -77.598010)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p8.append(path)
del p8[0][-1]

# 17-10
p9 = []
source = (43.136355, -77.598010)
destination = (43.136415, -77.597977)

source_node = ox.get_nearest_node(roc_graph, source)
destination_node = ox.get_nearest_node(roc_graph, destination)
# Calculate the shortest path
path = nx.shortest_path(roc_graph, source_node, destination_node, weight='travel_time')
p9.append(path)

final_p = []
final_p = p + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
final_path = final_p[0] + final_p[1] + final_p[2] + final_p[3] + final_p[4] + final_p[5] + final_p[6] + final_p[7] + \
             final_p[8]

# Plot the route and street networks
ox.plot_graph_route(roc_graph, final_path, route_linewidth=3, node_size=0, bgcolor='k');