import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt 

#Base Map of the city
city = ox.geocode_to_gdf('Fuquay Varina, NC, USA')
ax = ox.project_gdf(city).plot()
_ = ax.axis('off')

#Depicting base roads and maps
G = ox.graph_from_place('Fuquay Varina, NC, USA', network_type='drive')
ox.plot_graph(G)

#Depicting the co-ordinates
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='lightgray', node_size=5)

# Creating a bounding box in the city
north, south, east, west = 35.581304,35.585510,-78.795250,-78.803511

# creating a network from that box
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='lightgray', node_size=5)

#Extracting Node Values from G
Nodes = []
for i in G.nodes:
    Nodes.append(i)
    
#Storing Node Values in the Dataframe    
data = pd.DataFrame(Nodes)
data.rename(columns = {0:'Nodes'}, inplace = True)

#Extracting Latitude and Longitude from G
lat1 = []
long1 = []
for i in Nodes:
    lat1.append(G.nodes[i].get('y'))
    long1.append(G.nodes[i].get('x'))
    
#Storing Latitude and Longitude in the Dataframe    
data['Latitude'] = lat1
data['Longitude'] = long1
print('Co-ordinate Details\n')
print(data)

