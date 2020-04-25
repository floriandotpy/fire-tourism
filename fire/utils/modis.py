"""
Functions for processing MODIS hdf files and filenames
"""
import os
import datetime
import warnings

from typing import List, Tuple, Optional

import numpy as np
import pandas as pd

from fire.utils.etc import max_precision, extract

# CONSTANTS
# ----------------------------------------------------
# from MODIS_C6_FIRE_USER_GUIDE_A.pdf, p. 27
R    = max_precision(6371007.181) # m, the radius of the idealized sphere 
                                  # representing the Earth
T    = max_precision(1111950) # m, the height and width of each MODIS 
                              # tile in the projection plane
XMIN = max_precision(-20015109) # m, the western limit of the projection plane
YMAX = max_precision( 10007555) # m, the northern limit of the projection plane
W    = max_precision(926.62543305)
#W    = T/1200 # = 926.62543305 m, the actual size of a "1-km" 
              # MODIS sinusoidal grid cell.
# ----------------------------------------------------


def navigate_forward(lat:float, lon:float, res:int=1) -> (int,int,int,int):
    """
    Args:
        lat: latitude of location in radians (phi in MODIS-Doc)
        lon: longitude of location in radians (lambda in MODIS-Doc)
        res: resolution of MODIS product; 
             1 for "1-km", 2 for "500-m", 4 for "250-m"
    
    Returns:
        (v, h, row, col), where 
            v:   vertical coordinate of MODIS tile; 0 ≤ v ≤ 17
            h:   horizontal coordinate of MODIS tile; 0 ≤ h ≤ 35
            row: row in MODIS tile (i in MODIS-Doc), 
                 0 ≤ row ≤ 1199 (at least for MOD14A2)
            col: column in MODIS tile (j in MODIS-Doc), 
                 0 ≤ col ≤ 1199 (at least for MOD14A2)
                     
    Details:
        See section "Forward Mapping" in MODIS_C6_FIRE_USER_GUIDE_A.pdf, p. 27.
        To double-check, see "Tile Calculator Tool" 
        https://landweb.modaps.eosdis.nasa.gov/cgi-bin/developer/tilemap.cgi
        
        * On a random sample very close to output of Tile Calculator Tool
          but might be too far off still for alignment with non-MODIS products
        * check: consistent with MODIS meta data?
        
    Consider: 
        * https://newsroom.gsfc.nasa.gov/sdptoolkit/HEG/HEGHome.html
        * compare to GeoTIFFs!
        * not floor-ing
        * can row (or col) be ==1200 ? Wouldn't this be a neighboring tile?
        
    """
    # Adjust w for tile size
    # w should be 231.65635826 for res=4, 
    #             463.31271653 for res=2, 
    #         and 926.62543305 for res=1
    w = W/res
    
    x = R * lon * np.cos(lat)
    y = R * lat
    
    h = int(np.floor( (x-XMIN)/T ))
    v = int(np.floor( (YMAX-y)/T ))
    
    i_nominator = (YMAX-y) % T
    i = int(np.floor( i_nominator/w - 0.5 ))
    
    j_nominator = (x-XMIN) % T
    j = int(np.floor( j_nominator/w - 0.5 ))
    
    return v, h, i, j


def navigate_inverse(v:int, h:int, row:int, col:int, res:int=1) -> (float, float):
    """
    Args:
        v:   vertical coordinate of MODIS tile; 0 ≤ V ≤ 17
        h:   horizontal coordinate of MODIS tile; 0 ≤ H ≤ 35
        row: row in MODIS tile (i in MODIS-Doc), 0 ≤ row ≤ 1199
        col: column in MODIS tile (j in MODIS-Doc), 0 ≤ col ≤ 1199
        res: resolution of MODIS product; 1 for "1-km", 2 for "500-m", 4 for "250-m"
    
    Returns:
        lat, lon: Latitude and longitude in degrees
        
    Details:
        See section "Inverse Mapping" in MODIS_C6_FIRE_USER_GUIDE_A.pdf, p. 28.
        To double-check, see "Tile Calculator Tool" 
        https://landweb.modaps.eosdis.nasa.gov/cgi-bin/developer/tilemap.cgi
        
    """
    # passing scalars and arrays at the same time to this function
    # is experimental. Check if that is the case and yield a warning
    inputs_are_arrays = [not np.isscalar(x) for x in [v,h,row,col]]
    if np.any(inputs_are_arrays) and not np.all(inputs_are_arrays):
        warnings.warn("Passing scalars and arrays at the same time "
                      "is experimental. Double check the shape of "
                      "the output or pass values as either (all) arrays "
                      "of the same length or as (all) scalars.")
    
    # to allow for a mixture of scalars and arrays as arguments
    # transform row to the shape of col, if row is a scalar
    # and col is not. Due to the following computations and
    # due to broadcasting in numpy, col does not have to be transformed.
    if np.isscalar(row) and not np.isscalar(col):
        row = np.ones(col.shape) * row
    
    # Adjust w for tile size
    # w should be 231.65635826 for res=4, 
    #             463.31271653 for res=2, 
    #         and 926.62543305 for res=1
    w = W/res
    
    x = (col + 0.5)*w + h*T + XMIN
    y = YMAX - (row + 0.5)*w - v*T
    
    lat = y / R
    lon = x / (R*np.cos(lat))
    
    return np.rad2deg(lat), np.rad2deg(lon)


def meta_from_hdf_filename(hdf_fname:str) -> dict:
    """
    Returns meta data that can be inferred from .hdf filenames.
    
    Args:
        hdf_name: 
            filename or -path to an MODIS HDF file. The filename
            must be the original name given by NASA, e.g.
            "MOD14A1.A2019257.h11v12.006.2019269172641.hdf"
            
    Returns:
        dict with key : type(value) : description
            "sat_name" : str : e.g. "MOD" or "MYD"
            "date"     : datetime.datetime : date parsed from filename
            "h"        : int : horizontal tile number
            "v"        : int : vertical tile number
    """
    meta = {
        "sat_name": sat_name_from_hdf_filename(hdf_fname),
        "date"    : date_from_hdf_filename(hdf_fname),
        "h"       : h_from_hdf_filename(hdf_fname),
        "v"       : v_from_hdf_filename(hdf_fname)
    }
    
    return meta

def product_name_from_hdf_filename(hdf_fname:str) -> str:
    hdf_fname = os.path.basename(hdf_fname)
    return extract(hdf_fname, r"^[^.]+")

def sat_name_from_hdf_filename(hdf_fname:str) -> str:
    hdf_fname = os.path.basename(hdf_fname) # drop path if it exists
    return hdf_fname[:3]

def date_from_hdf_filename(hdf_fname:str) -> datetime.datetime:
    hdf_fname = os.path.basename(hdf_fname) # drop path if it exists
    date_str = hdf_fname[9:16] # date is given in yyyyjjj, where jjj is day-of-year
    return datetime.datetime.strptime(date_str, "%Y%j")

def h_from_hdf_filename(hdf_fname:str) -> int:
    hdf_fname = os.path.basename(hdf_fname) # drop path if it exists
    return int(hdf_fname[18:20])

def v_from_hdf_filename(hdf_fname:str) -> int:
    hdf_fname = os.path.basename(hdf_fname) # drop path if it exists
    return int(hdf_fname[21:23])

def default_target_path_scheme(url:str, data_root_path:str) -> str:
    """
    Generates a file path to which a file from url will be
    written to. The scheme is as follows:
        {data_root_path}/{product}/{date}/{filename}
        
    E.g. the prameters
        url = 'https://e4ftl01.cr.usgs.gov/MOTA/MCD12Q1.006/2001.01.01/'
              'MCD12Q1.A2001001.h00v08.006.2018142182903.hdf'
        data_root_path = '/home/user/data/'
    will yield
        '/home/user/data/MCD12Q1.006/2001.01.01/'
        'MCD12Q1.A2001001.h00v08.006.2018142182903.hdf'
    """
    data_root_path      = os.path.expanduser(data_root_path)
    product_name        = product_name_from_hdf_filename(url)
    url_from_product_on = extract(url, product_name + r".+[/\\].+")
    target_path         = os.path.join(data_root_path, url_from_product_on)
    return target_path


def make_hdf_index_from_paths(hdf_paths: List[str], 
                              path_col_name: str = "url"
                             ) -> pd.DataFrame:
    hdf_index = ( pd
        .DataFrame({path_col_name: hdf_paths})
        .assign(fname      = lambda df: df.url.apply(os.path.basename),
                sat_name   = lambda df: df.fname.apply(sat_name_from_hdf_filename),
                fname_date = lambda df: df.fname.apply(date_from_hdf_filename),
                h          = lambda df: df.fname.apply(h_from_hdf_filename),
                v          = lambda df: df.fname.apply(v_from_hdf_filename)
        )
    )
    return hdf_index