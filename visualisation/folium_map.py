"""

"""

################################################################################
# %% IMPORT PACKAGES
################################################################################

import folium
import pandas as pd
import numpy as np
from folium.plugins import HeatMap
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import geojsoncontour
from sklearn.neighbors import KernelDensity

################################################################################
# %% PLOT MAP
################################################################################

lat_min = 41.7
lat_max = 43.8
lon_min = -9.4
lon_max = -4.3


##### CREATE MAP OBJECT
map = folium.Map(
        location=(43, -7.0),
        tiles = "Stamen Terrain",
        zoom_start=9,
        min_zoom=5,
        max_zoom=10
    )

##### PULL POINT DATA
raw_data = pd.read_csv('../tourism/data.csv', index_col=0)
fire_data = pd.read_csv('../fire/data/fires_spain_since_2010.csv')
fire_data = fire_data[np.logical_and(fire_data['lat']>lat_min, fire_data['lon']<-lon_max)]

##### LIMIT TO TOURIST DATA
tourism_data = raw_data.loc[raw_data['type'] == 'tourism']

##### GRADIENT FOR FIRES
gradient = {.33: 'red', .66: 'brown', 1: 'yellow'}

##### PLOT HEAT MAPS
HeatMap(data=tourism_data[['lat', 'lon']], radius=10).add_to(folium.FeatureGroup(name='Tourism').add_to(map))
HeatMap(data=fire_data[['lat', 'lon']], gradient=gradient, radius=12).add_to(folium.FeatureGroup(name='Forest Fires').add_to(map))

##### GET KDES
kde = KernelDensity(kernel='gaussian', bandwidth=0.0005, metric='haversine')
kde.fit(np.pi/180.0*tourism_data[['lat', 'lon']])

x = np.linspace(lon_min, lon_max, 500)
y = np.linspace(lat_min, lat_max, 200)
lon, lat = np.meshgrid(x, y)

score = np.exp(kde.score_samples(np.pi/180.0*np.array([lat.reshape(-1), lon.reshape(-1)]).T))
score = score.reshape(lon.shape)*40

##### SET CMAP WITH ALPHA
cmap = plt.cm.plasma
mycmap = cmap(np.arange(cmap.N))
mycmap[:,-1] = np.linspace(0, 0.9, cmap.N)
mycmap = ListedColormap(mycmap)

##### CREATE CONTOUR THROUGH MPL
contourf = plt.contourf(lon, lat, score, 20, cmap=mycmap)

##### CONVERT  CONTOUR TO GEOJSON OBJECT
geojson = geojsoncontour.contourf_to_geojson(
    contourf=contourf,
    min_angle_deg=1.0,
    ndigits=10,
    stroke_width=1,
    fill_opacity=0.8)

##### ADD GEOJSON OBJECT TO PLOT
folium.GeoJson(
    geojson,
    style_function=lambda x: {
        'color':     x['properties']['stroke'],
        'weight':    x['properties']['stroke-width'],
        'fillColor': x['properties']['fill'],
        'opacity':   1.0,
        'fillOpacity': 0.1,
    }).add_to(folium.FeatureGroup(name='KDE-Tourism').add_to(map))

##### ADD LAYER CONTROL
folium.LayerControl().add_to(map)

##### SAVE!
map.save('folium_map.html')
