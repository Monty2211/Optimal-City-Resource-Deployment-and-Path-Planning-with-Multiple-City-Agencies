#  Evaluation_Python_File. 
#  This file demonstrates the model and the results that are generated for the same. 
#  Before runnning the file, you will have to download all the dependencies - ortools is the most important here.
#  To run this file, type Evaluation.py in cmd
#  After running, first you will see the synthetic graph that is created. After closing that, the model will 
#  start running and will give you the output in the form of another figure, in which you will see the paths that
#  connect all the nodes with their coordinates. After this, you will then see evaluation model being run.
#  This evaluation is done with the help of Google's OR-Tools. At the end, you will see the paths that
#  were evaluated using OR-Tools. You can see the paths created from our model as well.
#  This code is running both our model and Google's model on the same synthetic graph.
#  For graphs and figures that explain more about results, see Evaluation-Results.ipynb
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
from pulp import *
import seaborn as sn
import haversine as hs
from haversine import Unit
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


G = nx.random_geometric_graph(15, 0.3)
#Generation_of_Synthetic_Graph
#10: Number of nodes and 0.3: Density are defined first
## G: This is where the definition of the graph is stored
G = nx.random_geometric_graph(10, 0.3)
## pos: Details and attributes of G are stored here.

pos = nx.get_node_attributes(G, "pos")
## dmin: Least amount needed to break the loop.
dmin = 1
## ncenter: Updating the node center after each calculation.
ncenter = 0
## x,y: They signify the coordinates of a particular node.
for n in pos:
    ## x,y: They signify the coordinates of a particular node.
    x, y = pos[n]
    ## d: This stores the calculation of the equation which uses coordinates.
    d = (x - 0.5) ** 2 + (y - 0.5) ** 2
    if d < dmin:
        ncenter = n
        dmin = d
        
## p: This is a dictionary which stores node information.        
p = dict(nx.single_source_shortest_path_length(G, ncenter))
## figsize: This controls the endproduct of the figure.
plt.figure(figsize=(8, 8))
## nodelist, aplha: This stores the list of nodes along with their coordinates.
nx.draw_networkx_edges(G, pos, nodelist=[ncenter], alpha=0.4)
nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=list(p.keys()),
    ## nodesize: This defines the size of the node.
    node_size=80,
    ## nodecolour: This defines the colour of the node.
    node_color=list(p.values()),
    ## cmap: This stores the final figure plot information
    cmap=plt.cm.Reds_r,
)
plt.xlim(-0.05, 1.05)
plt.ylim(-0.05, 1.05)
plt.axis("off")
plt.show()
## ll: This signifies the x-coordinate of the particular node.
ll = list()
for i in pos:
    ll.append(pos[i][0])
## rr: This signifies the y-coordinate of the particular node.    
rr = list()
for i in pos:
    rr.append(pos[i][1])
## df: This declares an empty dataframe.    
df = pd.DataFrame()
df['Left'] = ll
df['Right'] = rr
df['coordinate'] = list(zip(df['Left'],df['Right']))
df['ID'] = df.index

##@dist_from
#Calculates the distance between the provided node coordinates.
# loc1: This stores coordinates of the first node.
# loc2: This stores coordinates of the second node.
def dist_from(loc1,loc2):
    ## dist: This stores the calculated distance of two nodes.
    dist=hs.haversine(loc1,loc2)
    return round(dist,2)
    
for _,row in df.iterrows():
    df[row.ID]=df['coordinate'].apply(lambda x: dist_from(row.coordinate,x))
## distances_df: This stores the dataframe information of the sliced columns.    
distances_df=df.iloc[:,4:4183]
#distances_df.index=df.ID
distances_df.insert(0, 'ID', df.ID)
## locations: This stores the nodes along with their coordinates in the form of a dictionary.
locations = dict( ( ID, (df.loc[ID, 'Left'], df.loc[ID, 'Right']) ) for ID in df.index)
locations
## l: It iterates over every instance of the locations dictionary
for l in locations:
    # lo: This stores an instance of the locations dictionary
    lo = locations[l]
    plt.plot(lo[0],lo[1],'o')
    plt.text(lo[0]+.01,lo[1],l,horizontalalignment='center',verticalalignment='center')    
plt.gca().axis('off');    
## df1: This declares an empty dataframe.
df1 = pd.DataFrame()
df1 = df
df1 = df1.drop(['Left'],axis=1)
df1 = df1.drop(['Right'],axis=1)
df1 = df1.drop(['coordinate'],axis=1)
df1 = df1.drop(['ID'],axis=1)
## distance: This stores values and date from df1.
distance = df1
## distances: This is a dictionary that stores distances from each node with all other nodes.
distances = dict( ((l1,l2), distance.iloc[l1, l2] ) for l1 in locations for l2 in locations if l1!=l2)



V = 5

## V: This defines the total number of vehicles that will traverse the path.
V = 3
## prob: This initializes the problem that will run using provided constraints.

prob=LpProblem("vehicle", LpMinimize)
## indicator: This defines the variable dictionary consisting of distances and indicates if location i is connected to location j along route
indicator = LpVariable.dicts('indicator',distances, 0,1,LpBinary)
## eliminator: This defines the variable dictionary consisting of the node ID's and elimiate subtours
eliminator = LpVariable.dicts('eliminator', df.ID, 0, len(df.ID)-1, LpInteger)
## cost: This stores the result of distances calculations.
cost = lpSum([indicator[(i,j)]*distances[(i,j)] for (i,j) in distances])
prob+=cost


for v in df.ID:
    ## cap: This considers a particular node at a time. 
    cap = 1 if v != 7 else V
    #inward possible route
    prob+= lpSum([ indicator[(i,v)] for i in df.ID if (i,v) in indicator]) ==cap
    #outward possible route
    prob+=lpSum([ indicator[(v,i)] for i in df.ID if (v,i) in indicator]) ==cap
## num: This stores the result of the number of nodes and the number of vehicles.    
num=len(df.ID)/V
for i in df.ID:
    for j in df.ID:
        if i != j and (i != 7 and j!= 7) and (i,j) in indicator:
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
routes = get_next_loc(7)
routes = [ [e] for e in routes ]

for r in routes:
    while r[-1][1] !=7:
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

print(routes)
##@ package create_data_model
# Stores the data for the problem.
def create_data_model():
    data = {}
    data['distance_matrix'] = distance

    data['num_vehicles'] = 5

    data['num_vehicles'] = 3

    data['depot'] = 7
    return data

##@print_solution
#Prints solution on console.
def print_solution(data, manager, routing, solution):
    
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
       #plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    #print('Maximum of the route distances: {}m'.format(max_route_distance))

##@main
#Solve the CVRP problem.
def main():
    # Instantiate the data problem.
    data = create_data_model()
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    # Create and register a transit callback.
    ##Returns the distance between the two nodes.
    def distance_callback(from_index, to_index):
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
        3000,  # vehicle maximum travel distances
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
    
    



