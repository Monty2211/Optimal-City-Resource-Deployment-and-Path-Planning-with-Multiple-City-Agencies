import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt

# Rough map of Rochester
rochester_city = ox.geocode_to_gdf('Rochester, NY, USA')
ax = ox.project_gdf(rochester_city).plot()
_ = ax.axis('off')

# Node visibility
rochester_graph = ox.graph_from_place('Rochester, NY, USA', network_type='drive')
ox.plot_graph(rochester_graph)

# Setting background and edge colours in the map
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(rochester_graph, bgcolor='#FFFFFF', node_color=colors[0], edge_color='gray', node_size=5)


# Sample bounding box in Rochester, NY - River Bend Shelter - Highland park boxed area
north, south, east, west = 43.12671,43.13403,-77.63630,-77.60385

# create a network from the above bounded box
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ox.plot.plot_graph(G, bgcolor='#FFFFFF', node_color=colors[0], edge_color='gray', node_size=5)

# Number of nodes within the selected area
count=0
for i in G.nodes:
    count=count+1
print("The number of nodes within the selected location: River Bend Shelter - Highland park boxed area")
print(count)

# Storing nodes in dataframe
cords = pd.DataFrame()
loc= []
for i in G.nodes:
    loc.append(i)

# Create a column name Location in the dataframe for nodes where
loc_data=pd.DataFrame(loc)
loc_data.rename(columns = {0:'Locations'}, inplace = True)

# Appending lats and longitudes
latitude = []
longitude = []
for i in loc:
    latitude.append(G.nodes[i].get('y'))
    longitude.append(G.nodes[i].get('x'))

# create 2 columns in the dataframe latitude and longitude and add the respective lists to the dataframe
loc_data['Latitudes'] = latitude
loc_data['Longitudes'] = longitude

# Print updated dataframe
print(loc_data)