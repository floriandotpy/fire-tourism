#
import numpy as np
import pandas as pd
from datetime import datetime

from typing import List, Tuple, Optional

# geo stuff
import rasterio as rio # for dataset reading
import pyproj # for projection stuff
from affine import Affine # class for transform matrices

# for plotting
import cartopy.crs as ccrs # cartopy CRSs
import matplotlib.pyplot as plt
import matplotlib as mpl

# own stuff
import fire.utils.modis as um
import fire.utils.io as uio
import fire.utils.geo as ugeo
from fire.utils.etc import ProgressDisplay



def get_fires(files: List[str]) -> pd.DataFrame:
    all_dfs = list()

    progress = ProgressDisplay(len(files))
    progress.start_timer()
    for f in files:
        firemask_sds_path = uio.get_subdataset_path(f, 0)
        all_dfs.append(_get_fires_from_single_subdataset(firemask_sds_path))
        progress.update_and_print()

    progress.stop()
    return pd.concat(all_dfs, axis=0).reset_index(drop=True)



def _get_fires_from_single_subdataset(sds: str) -> pd.DataFrame:
    rio_sds = rio.open(sds, mode="r")

    # get dates available in subdataset
    dates = rio_sds.get_tag_item("Dates").split()
    dates = [datetime.strptime(d, r"%Y-%m-%d") for d in dates]

    all_dfs = list() # will hold one DF for each date
    for i, d in enumerate(dates):
        raster_of_date_i = rio_sds.read()[i]
        pixel_is_fire    = raster_of_date_i >= 7

        if np.any(pixel_is_fire):
            # pixel locations of fires
            ii, jj     = np.where(pixel_is_fire)
            lons, lats = ugeo.get_coords_for_pixels(
                rio_sds, rows = ii, cols = jj)
            
            pixel_values = raster_of_date_i[ii, jj]

            all_dfs.append(pd.DataFrame({
                "lat": lats, 
                "lon": lons, 
                "fire_val": pixel_values, 
                "date": d
            }))

    if len(all_dfs) == 0:
        empty_df_with_correct_cols = pd.DataFrame({
            "lat": [], "lon": [], "fire_val": [], "date": []})
        return empty_df_with_correct_cols
    else:
        return pd.concat(all_dfs, axis=0)
