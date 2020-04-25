import numpy as np
import rasterio as rio # for dataset reading
import pyproj # for projection stuff
from affine import Affine # class for transform matrices

from typing import List, Tuple

# CONSTANTS
CRS_LATLON = pyproj.CRS.from_epsg(4326)


def get_coords_for_pixels(dataset: rio.DatasetReader, 
                          rows: np.array, 
                          cols: np.array, 
                          dst_crs: Optional[pyproj.crs.CRS] = None
                         ) -> Tuple[List[float], List[float]]:
    """
    Args:
        dataset (rasterio.DatasetReader): must be opened (?) #todo
        rows (numpy.array): indices of the rows of the pixels of interest
        cols (numpy.array): indices of the columns of the pixels of interest
        dst_crs (pyproj.CRS): CRS to project coordinates to. If None, 
            EPSG:4326 (lat lon) will be used. Defaults to None.
    
    Returns:
        tuple: two lists of floats, xs and ys. If dst_crs is default, output 
            will be lon, lat. #todo or lat lon??
    """
    # sanity check
    assert len(rows) == len(cols), \
        "rows and cols must be lists or arrays of same length"
    
    # set destination CRS (projection) to lat lon, if not given
    if dst_crs is None:
        dst_crs = CRS_LATLON

    # get projection info about dataset
    src_tf:  Affine         = dataset.transform
    src_crs: pyproj.crs.CRS = pyproj.CRS.from_wkt(dataset.crs.to_wkt())
    
    # get coordinates of pixel ijs in src projection
    src_xs, src_ys = rio.transform.xy(rio_mod_sds.transform, rows, cols)
    src_xs, src_ys = np.array(src_xs), np.array(src_ys)
    
    # reproject coordinates to destination CRS (projection)
    dst_xs, dst_ys = pyproj.transform(src_crs, dst_crs, src_xs, src_ys, 
                                      errcheck=True, always_xy=True, 
                                      skip_equivalent=True)
    
    return dst_xs, dst_ys