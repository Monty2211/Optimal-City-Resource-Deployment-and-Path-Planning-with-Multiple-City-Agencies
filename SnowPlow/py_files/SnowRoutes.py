import folium
import openrouteservice as ors
import sys
import heapq
import random, math

%matplotlib inline

import matplotlib.pyplot as plt
import geopandas as gpd
import pysal as ps


import pandas as pd
import osmnx as ox
city = ox.geocode_to_gdf('Washington, D.C.')
ax = ox.project_gdf(city).plot()
_ = ax.axis('off')


import geopandas as gpd
from shapely.geometry import Point, Polygon
import pandas as pd

import networkx as nx

import igraph as ig
print(ox.__version__)
print(ig.__version__)

weight = "length"


import numpy
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform


gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
my_map = gpd.read_file('Snow_Removal_Areas.kml', driver='KML')
my_map

polys = []
coordinates = []

for i in range( len(my_map)):
    polys.append(my_map.iloc[i])
    coordinates.append(polys[i][2])

Graphs = []

from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)


for i in range(len(coordinates)):
    Graphs.append(ox.graph_from_polygon(coordinates[i], network_type="drive",
                            simplify=True, retain_all=True, truncate_by_edge=True,
                            clean_periphery=True, custom_filter=None))


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

denseGraphs1 = []

Graphs2 = []

Graphs2 = Graphs.copy()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

for i in range(len(Graphs)):
    G_proj = ox.project_graph(Graphs[i])
    dense = ox.consolidate_intersections(G_proj, rebuild_graph=False, tolerance=15, dead_ends=False)
    denseGraphs1.append(dense)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

nxGraphs = []
denseGraphs = denseGraphs1
idenseGraphs = []


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)


for i in range(len(Graphs)):
    osmids = list(Graphs[i].nodes)
    Graphs[i] = nx.relabel.convert_node_labels_to_integers(Graphs[i])
    osmid_values = {k: v for k, v in zip(Graphs[i].nodes, osmids)}
    nx.set_node_attributes(Graphs[i], osmid_values, "osmid")

numberOfAreas = len(Graphs)

for i in range(numberOfAreas):
    idenseGraphs.insert( i, ig.Graph(directed=True))
    idenseGraphs[i].add_vertices(Graphs[i].nodes)
    idenseGraphs[i].add_edges(Graphs[i].edges())
    idenseGraphs[i].vs["osmid"] = osmids
    idenseGraphs[i].es[weight] = list(nx.get_edge_attributes(Graphs[i], weight).values())


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

eccentricities = []
neighbors = []

for i in range(len(idenseGraphs)):
    eccentricities.append(idenseGraphs[i].eccentricity(vertices=None, mode='in'))
    neighbors.append(idenseGraphs[i].neighborhood(vertices=None, order=1, mode='all', mindist=0))

df1 = pd.DataFrame()
Nodes = []

G23 = Graphs[3]
for i in G23.nodes:
    Nodes.append(i)
df1 = pd.DataFrame(Nodes)
df1.rename(columns={0: 'Nodes'}, inplace=True)

df1 = pd.DataFrame(Nodes)

df1.rename(columns={0: 'Nodes'}, inplace=True)

lats = []
longs = []

for i in Nodes:
    lats.append(G23.nodes[i].get('y'))
    longs.append(G23.nodes[i].get('x'))

df1['Latitude'] = lats
df1['Longitude'] = longs

df1.head()

subset = df1[['Latitude', 'Longitude']]
tuples = [tuple(x) for x in subset.to_numpy()]

len(tuples)


arrayofTuples = numpy.array_split(tuples, 5)
arrayofEccentricity = numpy.array_split(eccentricities[0], 5)


class PrioritySet(object):

    def __init__(self):
        self.heap = []
        self.set = set()

    def push(self, d):
        if not d in self.set:
            heapq.heappush(self.heap, d)
            self.set.add(d)

    def pop(self):
        d = heapq.heappop(self.heap)
        self.set.remove(d)
        return d

    def size(self):
        return len(self.heap)

    def __str__(self):
        op = ""
        for i in self.heap:
            op += str(i[0]) + " : " + i[1].__str__()
            op += "\n"
        return op

    def __getitem__(self, index):
        return self.heap[index]


class Position:

    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ") "

    def x_coor(self):
        return self.x

    def y_coor(self):
        return self.y


class Vehicle:

    def __init__(self, capacity):
        self.capacity = capacity

    def capacity(self):
        return self.capacity

class Node:

    pos = Position(-1,-1)
    demand = 0

    def __init__(self,name):
        self.name = name

    def setPosition(self,x,y):
        self.pos = Position(x, y)

    def setDemand(self,d):
        self.demand = d

    def __str__(self):
        return "( " + str(self.pos.x) + " , " + \
                   str(self.pos.y) + " )"


def copy(li):
    return [i for i in li]


def getProb():
    return random.random()


def get_random(li):
    index = random.randint(0, len(li) - 1)
    return li[index]


def get_distance(cus1, cus2):
    # Euclideian
    # change to vincenty later
    dist = 0
    dist = math.sqrt(((cus1.pos.x - cus2.pos.x) ** 2) + ((cus1.pos.y - cus2.pos.y) ** 2))
    return dist


def print_tuple(t):
    #     print( "0"),
    for i in t:
        print(i),
    #     print( "0"),


#     print (" -> f: " + str(get_fitness(t)))

def print_population(p):
    for i in p:
        for c in i:
            print(c),
        print("\n")


def print_population_heap(p):
    count = 1
    for i in p:
        print(count, " )  ")
        print_tuple(i[1])
        count += 1
        print("\n")


def mutate(chromosome):
    temp = [i for i in chromosome]

    if getProb() < MUTATION_RATE:
        left = random.randint(1, len(temp) - 2)
        right = random.randint(left, len(temp) - 1)
        temp[left], temp[right] = temp[right], temp[left]
    return temp


def crossover(a, b):
    if getProb() < CROSSOVER_RATE:
        left = random.randint(1, len(a) - 2)
        right = random.randint(left, len(a) - 1)
        # print left, " ", right
        c1 = [c for c in a[0:] if c not in b[left:right + 1]]
        # print len(c1)
        a1 = c1[:left] + b[left:right + 1] + c1[left:]
        # print len(p1)
        c2 = [c for c in b[0:] if c not in a[left:right + 1]]
        b1 = c2[:left] + a[left:right + 1] + c2[left:]
        return a1, b1

    return a, b


def get_fitness(li):
    num_custo = len(li)
    fitness = 0

    for i in range(num_custo - 1):
        fitness += get_distance(li[i], li[i + 1])

    fitness += get_distance(DEPOT, li[0])
    fitness += get_distance(li[-1], DEPOT)

    temp = copy(li)
    temp.insert(0, DEPOT)
    temp.append(DEPOT)
    valid = 1
    curr_demand = 0
    for i in range(len(temp)):
        if temp[i] == DEPOT and curr_demand > CAPACITY:
            fitness = INF
        elif temp[i] == DEPOT:
            curr_demand = 0
        else:
            curr_demand += temp[i].demand

    return fitness


def getPopulationFitness(p):
    h = PrioritySet()
    for i in p:
        h.push((get_fitness(i), i))
    return h


def create_new():
    TempSet = copy(Nodes)
    chromosome = []
    while len(TempSet) > 0:
        index = (int)(getProb() * len(TempSet))
        chromosome.append(TempSet.pop(index))

    return chromosome


def initialize_population():

    while len(population) < POPULATION_SIZE:
        TempSet = copy(Nodes)
        chromosome = []
        while len(TempSet) > 0:
            index = (int)(getProb() * len(TempSet))
            chromosome.append(TempSet.pop(index))

        if get_fitness(chromosome) != INF:
            population.add(tuple(chromosome))


MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.9
POPULATION_SIZE = 100
FITNESS = 0
TRUCKS = 15
DEPOT = None
CAPACITY = 100
INF = float("inf")


def Genetic_Algo():

#     print ("POPULATION GENERATED... EVOLUTION BEGINING ...")
    minimum_chrom = h[0]
#     print( "Curr Min: ", minimum_chrom[0])
    count = 0
    # while h[0][0] > 1800:
    while count < 1000:
        ax = h.pop()
        bx = h.pop()
        a,b = crossover(list(ax[1]),list(bx[1]))
        a = mutate(a)
        while get_fitness(a) == INF:
            a = create_new()
        b = mutate(b)
        while get_fitness(b) == INF:
            b = create_new()
        if get_fitness(a) != INF:
            h.push((get_fitness(a),tuple(a)))
        else:
            h.push(ax)
        if get_fitness(b) != INF:
            h.push((get_fitness(b),tuple(b)))
        else:
            h.push(bx)

        while h.size() < POPULATION_SIZE:
            TempSet = copy(Nodes)
            chromosome = []
            count += 1
            while len(TempSet) > 0:
                index = (int)(getProb() * len(TempSet))
                chromosome.append(TempSet.pop(index))
            h.push((get_fitness(chromosome),tuple(chromosome)))
        count = count + 1
        if h[0][0] < minimum_chrom[0]:
            minimum_chrom = h[0]


    print_tuple(minimum_chrom[1])
    print(count)



def create_data_array():
    locations = arrayofTuples[0]


    demands = arrayofEccentricity[0]


    for i in range(1,len(locations)):
        c = Node(i)
        c.setPosition(locations[i][0],locations[i][1])
        c.setDemand(demands[i])
        Nodes.append(c)

    i = 0
    c = Node(i)
    c.setPosition(locations[i][0],locations[i][1])
    c.setDemand(demands[i])
    global DEPOT
    DEPOT = c

    for j in range(TRUCKS-1):
        Nodes.append(DEPOT)






Nodes = []
population = set()

if __name__ == '__main__':
    create_data_array()
    initialize_population()

    newListofNodes = []
    h = getPopulationFitness(population)
    sys.stdout = open("testingMaterial0.txt", "w")
    Genetic_Algo()



def create_data_array():
    locations = arrayofTuples[1]


    demands = arrayofEccentricity[1]


    for i in range(1,len(locations)):
        c = Node(i)
        c.setPosition(locations[i][0],locations[i][1])
        c.setDemand(demands[i])
        Nodes.append(c)

    i = 0
    c = Node(i)
    c.setPosition(locations[i][0],locations[i][1])
    c.setDemand(demands[i])
    global DEPOT
    DEPOT = c

    for j in range(TRUCKS-1):
        Nodes.append(DEPOT)






Nodes = []
population = set()

if __name__ == '__main__':
    create_data_array()
    initialize_population()

    newListofNodes = []
    h = getPopulationFitness(population)
    sys.stdout = open("testingMaterial1.txt", "w")
    Genetic_Algo()


def create_data_array():
    locations = arrayofTuples[2]


    demands = arrayofEccentricity[2]


    for i in range(1,len(locations)):
        c = Node(i)
        c.setPosition(locations[i][0],locations[i][1])
        c.setDemand(demands[i])
        Nodes.append(c)

    i = 0
    c = Node(i)
    c.setPosition(locations[i][0],locations[i][1])
    c.setDemand(demands[i])
    global DEPOT
    DEPOT = c

    for j in range(TRUCKS-1):
        Nodes.append(DEPOT)






Nodes = []
population = set()

if __name__ == '__main__':
    create_data_array()
    initialize_population()

    newListofNodes = []
    h = getPopulationFitness(population)
    sys.stdout = open("testingMaterial2.txt", "w")
    Genetic_Algo()


def create_data_array():
    locations = arrayofTuples[3]


    demands = arrayofEccentricity[3]


    for i in range(1,len(locations)):
        c = Node(i)
        c.setPosition(locations[i][0],locations[i][1])
        c.setDemand(demands[i])
        Nodes.append(c)

    i = 0
    c = Node(i)
    c.setPosition(locations[i][0],locations[i][1])
    c.setDemand(demands[i])
    global DEPOT
    DEPOT = c

    for j in range(TRUCKS-1):
        Nodes.append(DEPOT)






Nodes = []
population = set()

if __name__ == '__main__':
    create_data_array()
    initialize_population()

    newListofNodes = []
    h = getPopulationFitness(population)
    sys.stdout = open("testingMaterial3.txt", "w")
    Genetic_Algo()



def create_data_array():
    locations = arrayofTuples[4]


    demands = arrayofEccentricity[4]


    for i in range(1,len(locations)):
        c = Node(i)
        c.setPosition(locations[i][0],locations[i][1])
        c.setDemand(demands[i])
        Nodes.append(c)

    i = 0
    c = Node(i)
    c.setPosition(locations[i][0],locations[i][1])
    c.setDemand(demands[i])
    global DEPOT
    DEPOT = c

    for j in range(TRUCKS-1):
        Nodes.append(DEPOT)






Nodes = []
population = set()

if __name__ == '__main__':
    create_data_array()
    initialize_population()

    newListofNodes = []
    h = getPopulationFitness(population)
    sys.stdout = open("testingMaterial4.txt", "w")
    Genetic_Algo()


df1 = df [[1, 3]].copy()
col_list = list(df1)

col_list[0] = "lat"
col_list[1] = "long"

df1.columns = col_list

df1["D"] = df1[["long","lat"]].apply(tuple, axis=1)
df1.head

df2 = df1[["D"]].copy()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

df = pd.read_table('tests1/testingMaterial0.txt', header=None, sep=" ")
df1 = df[[1, 3]].copy()
col_list = list(df1)

col_list[0] = "lat"
col_list[1] = "long"

df1.columns = col_list

df1["D"] = df1[["long", "lat"]].apply(tuple, axis=1)
df1.head

df2 = df1[["D"]].copy()

listnew = []

listnew = df2['D'].to_list()

coordslist0 = listnew

map_geocode = folium.Map(location=[38.961880, -77.006330], tiles='cartodbpositron', zoom_start=13)
coords = listnew

client = ors.Client(key='5b3ce3597851110001cf6248fc30f10b77b5410dab564eac271c1b0d')  # Specify your personal API key
# routes = client.directions(coords)

routes = client.directions(coords, optimize_waypoints=True, format='geojson')
# optimization requires at least 4 or more coordinates.
# Take the entire coords of the city itself

print(routes)

map_directions = folium.Map(location=[38.940783, -76.997869], zoom_start=15)

folium.GeoJson(routes, name='routes').add_to(map_directions)
folium.LayerControl().add_to(map_directions)
map_directions

map_directions.save(outfile="File0.html")

df = pd.read_table('tests1/testingMaterial1.txt', header=None, sep=" ")
df1 = df[[1, 3]].copy()
col_list = list(df1)

col_list[0] = "lat"
col_list[1] = "long"

df1.columns = col_list

df1["D"] = df1[["long", "lat"]].apply(tuple, axis=1)
df1.head

df2 = df1[["D"]].copy()

listnew = []

listnew = df2['D'].to_list()
coordslist1 = listnew
map_geocode = folium.Map(location=[38.961880, -77.006330], tiles='cartodbpositron', zoom_start=13)
coords = listnew

client = ors.Client(key='5b3ce3597851110001cf6248fc30f10b77b5410dab564eac271c1b0d')  # Specify your personal API key
# routes = client.directions(coords)

routes = client.directions(coords, optimize_waypoints=True, format='geojson')
# optimization requires at least 4 or more coordinates.
# Take the entire coords of the city itself

print(routes)

map_directions = folium.Map(location=[38.940783, -76.997869], zoom_start=15)

folium.GeoJson(routes, name='routes').add_to(map_directions)
folium.LayerControl().add_to(map_directions)
map_directions

map_directions.save(outfile="File1.html")

df = pd.read_table('tests1/testingMaterial2.txt', header=None, sep=" ")
df1 = df[[1, 3]].copy()
col_list = list(df1)

col_list[0] = "lat"
col_list[1] = "long"

df1.columns = col_list

df1["D"] = df1[["long", "lat"]].apply(tuple, axis=1)
df1.head

df2 = df1[["D"]].copy()

listnew = []

listnew = df2['D'].to_list()
coordslist2 = listnew
map_geocode = folium.Map(location=[38.961880, -77.006330], tiles='cartodbpositron', zoom_start=13)
coords = listnew

client = ors.Client(key='5b3ce3597851110001cf6248fc30f10b77b5410dab564eac271c1b0d')  # Specify your personal API key
# routes = client.directions(coords)

routes = client.directions(coords, optimize_waypoints=True, format='geojson')
# optimization requires at least 4 or more coordinates.
# Take the entire coords of the city itself

print(routes)

map_directions = folium.Map(location=[38.940783, -76.997869], zoom_start=15)

folium.GeoJson(routes, name='routes').add_to(map_directions)
folium.LayerControl().add_to(map_directions)
map_directions

map_directions.save(outfile="File2.html")

df = pd.read_table('tests1/testingMaterial3.txt', header=None, sep=" ")
df1 = df[[1, 3]].copy()
col_list = list(df1)

col_list[0] = "lat"
col_list[1] = "long"

df1.columns = col_list

df1["D"] = df1[["long", "lat"]].apply(tuple, axis=1)
df1.head

df2 = df1[["D"]].copy()

listnew = []

listnew = df2['D'].to_list()
coordslist3 = listnew
map_geocode = folium.Map(location=[38.961880, -77.006330], tiles='cartodbpositron', zoom_start=13)
coords = listnew

client = ors.Client(key='5b3ce3597851110001cf6248fc30f10b77b5410dab564eac271c1b0d')  # Specify your personal API key
# routes = client.directions(coords)

routes = client.directions(coords, optimize_waypoints=True, format='geojson')
# optimization requires at least 4 or more coordinates.
# Take the entire coords of the city itself

print(routes)

map_directions = folium.Map(location=[38.940783, -76.997869], zoom_start=15)

folium.GeoJson(routes, name='routes').add_to(map_directions)
folium.LayerControl().add_to(map_directions)
map_directions

map_directions.save(outfile="File3.html")

df = pd.read_table('tests1/testingMaterial4.txt', header=None, sep=" ")
df1 = df[[1, 3]].copy()
col_list = list(df1)

col_list[0] = "lat"
col_list[1] = "long"

df1.columns = col_list

df1["D"] = df1[["long", "lat"]].apply(tuple, axis=1)
df1.head

df2 = df1[["D"]].copy()

listnew = []

listnew = df2['D'].to_list()
coordslist4 = listnew
map_geocode = folium.Map(location=[38.940783, -76.997869], tiles='cartodbpositron', zoom_start=13)
coords = listnew

client = ors.Client(key='5b3ce3597851110001cf6248fc30f10b77b5410dab564eac271c1b0d')  # Specify your personal API key
# routes = client.directions(coords)

routes = client.directions(coords, optimize_waypoints=True, format='geojson')
# optimization requires at least 4 or more coordinates.
# Take the entire coords of the city itself

print(routes)

map_directions = folium.Map(location=[38.940783, -76.997869], zoom_start=15)

folium.GeoJson(routes, name='routes').add_to(map_directions)
folium.LayerControl().add_to(map_directions)
map_directions

map_directions.save(outfile="File4.html")

