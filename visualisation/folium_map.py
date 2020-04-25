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

################################################################################
# %% PLOT MAP
################################################################################

map = folium.Map(
        location=(42.5, -5.0),
        tiles = "Stamen Terrain",
        zoom_start=8,
        min_zoom=8,
        max_zoom=8
    )

raw_data = pd.read_csv('../tourism/data.csv', index_col=0)
fire_data = pd.read_csv('../fire/samples_fires.csv')

tourism_data = raw_data.loc[raw_data['type'] == 'tourism']

gradient = {.33: 'red', .66: 'brown', 1: 'yellow'}

HeatMap(data=tourism_data[['lat', 'lon']], radius=8).add_to(folium.FeatureGroup(name='Tourism').add_to(map))
HeatMap(data=fire_data[['lat', 'lon']], gradient=gradient, radius=12).add_to(folium.FeatureGroup(name='Forest Fires').add_to(map))

folium.LayerControl().add_to(map)

map.save('folium_map.html')
