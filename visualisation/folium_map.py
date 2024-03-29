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
# %% PLOT KDE ON SET
################################################################################

def plot_kde(map, data, limits, name, cmap):

    lat_min, lat_max, lon_min, lon_max = limits

    ##### GET KDES
    bandwidth = 5e-4
    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth, metric='haversine', atol=0.1)
    kde.fit(np.pi/180.0*data[['lat', 'lon']])

    x = np.linspace(lon_min, lon_max, 500)
    y = np.linspace(lat_min, lat_max, 200)
    lon, lat = np.meshgrid(x, y)

    score = np.exp(kde.score_samples(np.pi/180.0*np.array([lat.reshape(-1), lon.reshape(-1)]).T))
    score = score.reshape(lon.shape)/25e6

    ##### SET CMAP WITH ALPHA
    mycmap = cmap(np.arange(cmap.N))
    mycmap[:,-1] = np.linspace(0, 0.9, cmap.N)
    mycmap = ListedColormap(mycmap)

    ##### CREATE CONTOUR THROUGH MPL
    contour = plt.contour(lon, lat, score, 30, cmap=mycmap)

    ##### CONVERT  CONTOUR TO GEOJSON OBJECT
    geojson = geojsoncontour.contour_to_geojson(
        contour=contour,
        min_angle_deg=1.0,
        ndigits=10,
        stroke_width=2,
        #fill_opacity=0.8
        )

    ##### ADD GEOJSON OBJECT TO PLOT
    folium.GeoJson(
        geojson,
        style_function=lambda x: {
            'color':     x['properties']['stroke'],
            'weight':    x['properties']['stroke-width'],
            #'fillColor': None,#x['properties']['fill'],
            'opacity':   1.0,
            #'fillOpacity': 0.0,
        }).add_to(folium.FeatureGroup(name=name).add_to(map))


################################################################################
# %% PLOT MAP
################################################################################

##### MAP LIMITS
lat_min = 41.7
lat_max = 43.8
lon_min = -9.4
lon_max = -4.3
limits = [lat_min, lat_max, lon_min, lon_max]

##### CREATE MAP OBJECT
map = folium.Map(
        location=((lat_max+lat_min)/2, (lon_max+lon_min)/2),
        tiles = "Stamen Terrain",
        zoom_start=9,
        min_zoom=7,
        max_zoom=10
    )

##### PULL POINT DATA
raw_data = pd.read_csv('../tourism/data.csv', index_col=0)
raw_data = raw_data.append(pd.read_csv('../tourism/data_asturias.csv', index_col=0))
raw_data = raw_data.append(pd.read_csv('../tourism/data_castilla_y_leon.csv', index_col=0))
fire_data = pd.read_csv('../fire/data/fires_spain_since_2010.csv')
fire_data = fire_data[
np.logical_and(
    np.logical_and(
        fire_data['lat']>lat_min,
        fire_data['lat']<lat_max),
    np.logical_and(
        fire_data['lon']>lon_min,
        fire_data['lon']<lon_max
    ))]

raw_data = raw_data[
np.logical_and(
    np.logical_and(
        raw_data['lat']>lat_min,
        raw_data['lat']<lat_max),
    np.logical_and(
        raw_data['lon']>lon_min,
        raw_data['lon']<lon_max
    ))]

##### LIMIT TO TOURIST DATA
tourism_data = raw_data.loc[raw_data['type'] == 'tourism']
non_tourism_data = raw_data.loc[raw_data['type'] != 'tourism']

##### GRADIENT FOR FIRES
gradient_b = {.33: 'red', .66: 'brown', 1: 'yellow'}
gradient_g = {.33: 'lightgreen', .66: 'blue', 1: 'navy'}
gradient_p = {.33: 'orange', .66: 'red', 1: 'pink'}

##### PLOT HEAT MAPS
HeatMap(data=tourism_data[['lat', 'lon']], radius=10).add_to(folium.FeatureGroup(name='Tourism').add_to(map))
HeatMap(data=non_tourism_data[['lat', 'lon']], radius=4).add_to(folium.FeatureGroup(name='Non-Tourism').add_to(map))
HeatMap(data=fire_data[['lat', 'lon']], gradient=gradient_b, radius=12).add_to(folium.FeatureGroup(name='Forest Fires').add_to(map))

##### GET KDES
bandwidth = 5e-4
kde_tourism = KernelDensity(kernel='gaussian', bandwidth=bandwidth, metric='haversine', atol=0.1)
kde_tourism.fit(np.pi/180.0*tourism_data[['lat', 'lon']])
score_tourism = np.exp(kde_tourism.score_samples(np.pi/180.0*fire_data[['lat', 'lon']]))

kde_non_tourism = KernelDensity(kernel='gaussian', bandwidth=bandwidth, metric='haversine', atol=0.1)
kde_non_tourism.fit(np.pi/180.0*non_tourism_data[['lat', 'lon']])
score_non_tourism = np.exp(kde_non_tourism.score_samples(np.pi/180.0*fire_data[['lat', 'lon']]))

##### TOURISM
HeatMap(data=fire_data.loc[score_tourism > score_non_tourism][['lat', 'lon']], gradient=gradient_g, radius=12).add_to(folium.FeatureGroup(name='Tourism Correlated Fires').add_to(map))
HeatMap(data=fire_data.loc[score_tourism < score_non_tourism][['lat', 'lon']], gradient=gradient_p, radius=12).add_to(folium.FeatureGroup(name='Non-Tourism Correlated Fires').add_to(map))

##### TOURISM
cmap = plt.cm.plasma
name = "KDE-Tourism"
plot_kde(map, tourism_data, limits, name, cmap)

##### NON-TOURISM
cmap = plt.cm.plasma
name = "KDE-Non-Tourism"
plot_kde(map, non_tourism_data, limits, name, cmap)

##### ADD LAYER CONTROL
folium.LayerControl().add_to(map)

##### SAVE!
map.save('folium_map.html')
