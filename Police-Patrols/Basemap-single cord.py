#!/usr/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

#my data
data = pd.read_csv('Shootings.csv')
# example coordinates to test with
sample_cords = [38.9719980,-76.9219820]

# Zoom from coordinates
zoom_scale = 1

# Boundaries for box, zoom and map
bbox = [sample_cords[0] - zoom_scale, sample_cords[0] + zoom_scale, \
        sample_cords[1] - zoom_scale, sample_cords[1] + zoom_scale]

plt.figure(figsize=(12,6))
# Define the projection, scale, bounds of map, and the resolution.
map = Basemap(projection='merc', llcrnrlat=bbox[0], urcrnrlat=bbox[1], \
              llcrnrlon=bbox[2], urcrnrlon=bbox[3], lat_ts=10, resolution='i')

# Draw coastlines and fill continents and water with color
map.drawcoastlines()
map.fillcontinents(color='green', lake_color='blue')

# draw parallels, meridians, and color boundaries
map.drawparallels(np.arange(bbox[0], bbox[1], (bbox[1] - bbox[0]) / 5), labels=[1, 0, 0, 0])
map.drawmeridians(np.arange(bbox[2], bbox[3], (bbox[3] - bbox[2]) / 5), labels=[0, 0, 0, 1], rotation=45)
map.drawmapboundary(fill_color='lightblue')

# build and plot coordinates onto map
lat, long = map(sample_cords[1], sample_cords[0])
map.plot(lat, long, marker='D', color='r')
plt.title("Area according to specifed coordinate")
plt.savefig('SampleArea.png', format='png', dpi=500)
plt.show()
