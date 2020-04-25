import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as mp
from matplotlib.colors import ListedColormap

def plot_density():

    ##### DEFINE MAP FIGURE
    fig = mp.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-10, 0, 41, 44.5], crs=ccrs.PlateCarree())

    ##### ADD GEOGRAPHIC FEATURES FOR BACKGROUND
    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', '10m'), facecolor=cfeature.COLORS['land'], zorder=0)
    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'ocean', '10m'), facecolor=cfeature.COLORS['water'], zorder=0)
    ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_1_states_provinces', '10m'), facecolor='none', edgecolor='k', zorder=0)
    ax.gridlines()

    ##### DUMMY DATA!
    x = np.linspace(-10, 0, 100)
    y = np.linspace(41, 45, 30)
    lon, lat = np.meshgrid(x, y)
    z = np.random.uniform(size=lon.shape)

    ##### SET CMAP WITH ALPHA
    cmap = mp.cm.plasma
    mycmap = cmap(np.arange(cmap.N))
    mycmap[:,-1] = np.linspace(0, 0.9, cmap.N)
    mycmap = ListedColormap(mycmap)

    ##### PLOT CONTOUR
    ax.contourf(lon, lat, z, 20, cmap=mycmap, transform=ccrs.PlateCarree(), zorder=2)
    mp.savefig('')
