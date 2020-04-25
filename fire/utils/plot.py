import numpy as np
import rasterio as rio # for dataset reading
import pyproj # for projection stuff
from affine import Affine # class for transform matrices

import cartopy.crs as ccrs # cartopy CRSs
import matplotlib.pyplot as plt
import matplotlib as mpl


def plot_onto_map(src: rio.DataSetReader, crs: ccrs, 
                  override_raster: Optional[np.ndarray] = None,
                  bands: List[int]=None, factor: float=None, tf: Affine=None,
                  figsize=(10,10), cmap=None
                 ) -> "cartopy.mpl.geoaxes.GeoAxesSubplot":
    """
    Quick and dirty plot function.
    Args:
        factor: hacky way to plot classification maps (e.g.) (low values)
        bands: 0-based! Works definitely with lists of length 3, e.g. [0,0,0].
        override_raster: overrides raster read from src, but still uses geo 
            properties from src. If not None, bands and factor is ignored. 
            Defaults to None.
    """
    if isinstance(src, rio.DatasetReader):
        # read image into ndarray
        im = src.read()
        
        # transpose the array from (band, row, col) to (row, col, band)
        im = np.transpose(im, [1,2,0])
    elif isinstance(src, np.ndarray): # format (row, col, band)
        im = src
    else:
        raise TypeError("src wrong type")
        
    if override_raster is not None:
        im = override_raster
    else:
        if bands:
            im = im[:,:,bands]
            print(im.shape)
        if factor:
            im *= factor
    
    # create figure
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': crs})
    ax.set_xmargin(0.05) # doesn't do anything???
    ax.set_ymargin(0.10) # doesn't do anything???
    
    # plot raster
    plt.imshow(im, origin='upper', 
               extent=[src.bounds.left, src.bounds.right, 
                       src.bounds.bottom, src.bounds.top], 
               transform=crs, interpolation='nearest', cmap=cmap)
    
    # plot coastlines
    ax.coastlines(resolution='10m', color='red', linewidth=1)
    
    return ax