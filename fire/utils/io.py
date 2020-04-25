import rasterio as rio
from typing import List

def get_subdataset_path(src_filepath: str, i: int) -> str:
    with rio.open(src_filepath, mode="r") as rio_file:
        sds_path = rio_file.subdatasets[i]
    return sds_path

def write_list(l:list, fpath:str) -> None:
    """
    Args:
        l: list to write to fpath
        fpath: path of file to write to
    """
    dirpath = os.path.dirname(fpath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    
    with open(fpath, "w") as f:
        for elem in l:
            f.write("%s\n" % elem)
            
def read_lines(fpath:str) -> List[str]:
    """
    Reads lines from file as text and returns
    these as a list.
    """
    with open(fpath, "rt") as f:
        file_content = f.readlines()
    # remove "\n" at the end of each line
    file_content = [line.rstrip("\n") for line in file_content]
    return file_content