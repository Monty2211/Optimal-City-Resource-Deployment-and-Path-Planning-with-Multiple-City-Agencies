# Optimal-City-Resource-Deployment-and-Path-Planning-with-Multiple-City-Agencies
## Sanket Waghmare, Rochelle Allan, Prasad Chavan

OP_Routes is a offline-storage compatible, path optimizing tool for city planners. 
Generates paths based on synthetic graphs and number of vehicles 
- Jupyter_Notebooks
    - A_Star.ipynb  
    - Evaluation-Results1.ipynb
    - Evaluation.ipynb
    - Routes with synthetic graph.ipynb
    - coordinates from address.ipynb
- PyFiles
    - Evaluation.py
    - LPRoute.py
    - routes_geoJson.py
- Results
    - Evaluation-Results.ipynb
    - trial_loops1.html
- Datasets
    - Garbage Pickup
        - Garbage-Pickup-Data.csv
    - Police Patrol
        - Homicide_Incidents_Persons.csv
        - RPD_-_Part_I_Crime_14_Days.csv
        - RPD_Police_Personnel.csv
        - Shootings.csv
    - SnowPlowData
        - dcopendata-adbfd35fb1044826a785d87ec766b8cb-21.zip 
        - dcopendata-adbfd35fb1044826a785d87ec766b8cb-21
            - Snow_Removal_Zones.cpg
            - Snow_Removal_Zones.dbf
            - Snow_Removal_Zones.prj
            - Snow_Removal_Zones.shp
            - Snow_Removal_Zones.shx
            - Snow_Removal_Zones.xml
            - resource_links.md
            - snow-removal-zones-1.xml
            - snow-removal-zones-2-1.geo
        - Snow_Removal_Routes.geojson
        - Snow_Removal_Routes.kml
        - Snow_Removal_Routes__All.csv
- AdditionalFiles
    - images
        - el_tigre.png
    - locations.csv
    - trial_Loop.json
- DoxygenOutput




## Installation & Running

OP-Routes requires [Python](https://www.python.org/downloads/)  3.5+ to run.
Extract the zipped files

Install the following for [LPRoute.py](https://github.com/Monty2211/Optimal-City-Resource-Deployment-and-Path-Planning-with-Multiple-City-Agencies/blob/main/PyFiles/LPRoute.py) 
```
pip install pandas numpy pulp networkx haversine matplotlib
```
This file uses synthetic graphs (which are in the form of Random Geometric Graphs RGG) as its input and prints the routes that can be taken by 'V' vehicles. In addition to the route paths for each vehicle this code also indicates whether or not there is an optimal solution given a synthetic graph and if there isn't one, it prints "infeasible solution". 
It also generates the enumerated nodes, total number of iterations, time taken in terms  of CPU seconds and wall clock seconds.
Once the required tools are installed, you can edit the number of vehicles to be deployed in this file by changing the value of 'V'.

Running [LPRoute.py](https://github.com/Monty2211/Optimal-City-Resource-Deployment-and-Path-Planning-with-Multiple-City-Agencies/blob/main/PyFiles/LPRoute.py)  
To run this file, enter the following in command line
```
python LPRoute.py
```
To see these paths and outputs in more detail, see Routes with synthetic graph.ipynb which can be found in the Jupyter_Notebook folder in the parent directory.


Install the following for [Evaluation.py](https://github.com/Monty2211/Optimal-City-Resource-Deployment-and-Path-Planning-with-Multiple-City-Agencies/blob/main/PyFiles/Evaluation.py)

```
pip install pandas numpy pulp networkx haversine matplotlib ortools
```
This file demonstrates the model and the results that are generated for the same. 
Before running the file, you will have to download all the dependencies - OR-tools is the most important here.

Running [Evaluation.py](https://github.com/Monty2211/Optimal-City-Resource-Deployment-and-Path-Planning-with-Multiple-City-Agencies/blob/main/PyFiles/Evaluation.py)  
To run this file, enter the following in command line
```
python Evaluation.py
```
After running, first you will see the synthetic graph that is created. After closing that, the model will start running and will give you the output in the form of another figure, in which you will see the paths that connect all the nodes with their coordinates. After this, you will then see the evaluation model being run.This evaluation is done with the help of Google's OR-Tools. At the end, you will see the paths that were evaluated using OR-Tools. You can see the paths created from our model as well.
This code is running both our model and Google's model on the same synthetic graph.
For graphs and figures that explain more about results, see Evaluation-Results.ipynb which can be found in the Jupyter_Notebook folder in the parent directory.
To see these paths and outputs in more detail, see Routes with synthetic graph.ipynb which can be found in the Jupyter_Notebook folder in the parent directory.


Install the following for [routes_geoJson.py](https://github.com/Monty2211/Optimal-City-Resource-Deployment-and-Path-Planning-with-Multiple-City-Agencies/blob/main/PyFiles/routes_geoJson.py)
```
pip install folium os base64
```
This file uses json file stored in the AdditionalFiles folder and makes a route for the given coordinates. The route connecting the nodes will be highlighted on the map along with the starting point saved a marker. 
Once the required tools are installed, you can edit the coordinates passed to this file by changing the value of 'routeData' and appending a different CSV file to it. 

Running [routes_geoJson.py](https://github.com/Monty2211/Optimal-City-Resource-Deployment-and-Path-Planning-with-Multiple-City-Agencies/blob/main/PyFiles/routes_geoJson.py)
To run this file, enter the following in command line
```
python routes_geoJson.py
```
To see these paths and outputs, open the Hyper-Text Markup Language <html> file that is created in the AdditionalFiles folder by the name of indexFinal.


