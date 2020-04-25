import rasterio as rio

def get_subdataset_path(src_filepath: str, i: int) -> str:
    with rio.open(src_filepath, mode="r") as rio_file:
        sds_path = rio_file.subdatasets[i]
    return sds_path