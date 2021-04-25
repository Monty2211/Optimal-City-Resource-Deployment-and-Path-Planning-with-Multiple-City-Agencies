# routes_geoJson  
# This file is used to create the path from the coordinates found in the json files
# This helps in displaying the nodes and the paths to be taken by the deployed vehicles.

import folium
from folium import IFrame
import os
import base64

## m: The map attributes are saved here, such as the location where the map will start out and the zoom level where the map will load at 
m = folium.Map(location=[43.08826653741596, -77.6734558492899], zoom_start=17)
## routeData : the coordinates from the json file are appended using the os package
routeData = os.path.join('../AdditionalFiles/trial_Loop.json')

## it is used to make the path using the folium library
folium.GeoJson(routeData, name='route1').add_to(m)



# Template to add a marker and image to the nodes
## tooltip: will display the hint message when the mouse is hovered on it 
tooltip = "Click here!!"
## html: adds the image 
html = '<img src="data:image/png;base64,{}">'.format
## picture1: the picture that is displayed when the node is clicked on
picture1 = base64.b64encode(open('../AdditionalFiles/images/el_tigre.png','rb').read()).decode()
## iframe1: inline frame used to load the html made earlier
iframe1 = IFrame(html(picture1), width=600+20, height=400+20)
## popup1: The iFrame will load here
popup1 = folium.Popup(iframe1, max_width=650)
## icon1: the icon that is used for the node
icon1 = folium.Icon(color="orange", icon="glyphicon-home")
## marker1: The marker which is depicted on the node. it contains the attributes of the node, such as the coordinates
marker1 = folium.Marker(location=[43.08826653741596, -77.6734558492899], popup=popup1, tooltip=tooltip, icon=icon1).add_to(m)
## the map is saved as indexFinal.html
m.save("../AdditionalFiles/indexFinal.html")