import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import plotly_express as px
import networkx as nx
import osmnx as ox

ox.config(use_cache=True, log_console=True)

def create_graph(loc, dist, transport_mode, loc_type="address"):
    """Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’"""
    if loc_type == "address":
        G = ox.graph_from_address(loc, dist=dist, network_type=transport_mode)
    elif loc_type == "points":
        G = ox.graph_from_point(loc, dist=dist, network_type=transport_mode )
    return G

G = create_graph('Gothenburg', 2500, 'drive')
ox.plot_graph(G)

G = ox.add_edge_speeds(G) #Impute
G = ox.add_edge_travel_times(G) #Travel time
start = (57.715495, 12.004210)
end = (57.707166, 11.978388)
start_node = ox.get_nearest_node(G, start)
end_node = ox.get_nearest_node(G, end)
# Calculate the shortest path
route = nx.shortest_path(G, start_node, end_node, weight='travel_time')
#Plot the route and street networks
ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='k');

node_start = []
node_end = []
X_to = []
Y_to = []
X_from = []
Y_from = []
length = []
travel_time = []
for u, v in zip(route[:-1], route[1:]):
    node_start.append(u)
    node_end.append(v)
    length.append(round(G.edges[(u, v, 0)]['length']))
    travel_time.append(round(G.edges[(u, v, 0)]['travel_time']))
    X_from.append(G.nodes[u]['x'])
    Y_from.append(G.nodes[u]['y'])
    X_to.append(G.nodes[v]['x'])
    Y_to.append(G.nodes[v]['y'])


df = pd.DataFrame(list(zip(node_start, node_end, X_from, Y_from, X_to, Y_to, length, travel_time)),
columns =['node_start', 'node_end', 'X_from', 'Y_from', 'X_to', 'Y_to', 'length', 'travel_time'])
df.head()


def create_line_gdf(df):
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.X_from, df.Y_from))
    gdf['geometry_to'] = [Point(xy) for xy in zip(gdf.X_to, gdf.Y_to)]
    gdf['line'] = gdf.apply(lambda row: LineString([row['geometry_to'], row['geometry']]), axis=1)
    line_gdf = gdf[['node_start','node_end','length','travel_time', 'line']].set_geometry('line')
    return line_gdf
line_gdf = create_line_gdf(df)


start = df[df['node_start'] == start_node]
end = df[df['node_end'] == end_node]

px.scatter_mapbox(df, lon= 'X_from', lat='Y_from', zoom=12)


fig = px.scatter_mapbox(df, lon= 'X_from', lat='Y_from', zoom=13, width=1000, height=800, animation_frame=df.index,mapbox_style='dark')
fig.data[0].marker = dict(size = 12, color='black')
fig.add_trace(px.scatter_mapbox(start, lon= 'X_from', lat='Y_from').data[0])
fig.data[1].marker = dict(size = 15, color='red')
fig.add_trace(px.scatter_mapbox(end, lon= 'X_from', lat='Y_from').data[0])
fig.data[2].marker = dict(size = 15, color='green')
fig.add_trace(px.line_mapbox(df, lon= 'X_from', lat='Y_from').data[0])
fig