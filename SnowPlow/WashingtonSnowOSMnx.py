import osmnx as ox
import pandas as pd
city = ox.geocode_to_gdf('Washington, D.C.')
ax = ox.project_gdf(city).plot()
_ = ax.axis('off')
G = ox.graph_from_place('Washington, D.C.', network_type='drive')
ox.plot_graph(G)
G2 = ox.consolidate_intersections(G, tolerance=10, rebuild_graph=True, dead_ends=True)
G = ox.project_graph(ox.graph_from_place('Washington D.C., USA', network_type='drive'))
G2 = ox.consolidate_intersections(G, tolerance=10, rebuild_graph=True, dead_ends=True)
G = ox.graph_from_xml("district-of-columbia-latest.osm.bz2")
fig, ax = ox.plot_graph(G, node_color="r")
# define a bounding box in DC
north, south, east, west = 38.937679, 38.941212, -77.075133, -77.066525

# create network from that bounding box
G = ox.graph_from_bbox(north, south, east, west, network_type="drive_service")
fig, ax = ox.plot_graph(G, node_color="r")
df = pd.DataFrame()
Nodes = []
for i in G.nodes:
    Nodes.append(i)

df = pd.DataFrame(Nodes)
df.rename(columns = {0:'Nodes'}, inplace = True)
lats = []
longs = []
for i in Nodes:
    lats.append(G.nodes[i].get('y'))
    longs.append(G.nodes[i].get('x'))

df['Latitude'] = lats
df['Longitude'] = longs
df.head()