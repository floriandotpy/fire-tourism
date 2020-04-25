import numpy as np
import re
import time

from typing import List



def max_precision(x) -> float:
    """
    Returns x as numpy.float128 if possible, otherwise as 
    numpy.float64 (depends on OS whether float128 is supported)
    """
    if hasattr(np, "float128"):
        return np.float128(x)
    return np.float64(x)

def like(x:str, pattern:str) -> bool:
    """
    Checks whether a regex-pattern matches a string.
    """
    return re.search(pattern, x) is not None

def extract(x:str, pattern:str) -> str:
    """
    Extracts a regex-match from a string or returns 
    None if there is no match.
    """
    match_obj = re.search(pattern, x)
    if match_obj is None:
        return None
    else:
        return match_obj.group()
    
def into_chunks(l, n) -> List: 
    """ 
    Split up a list into chunks of size n (or smaller for the last bit)
    
    stolen from
    https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
    """
    for i in range(0, len(l), n):  
        yield l[i:i + n] 
    
class ProgressDisplay():
    """
    Prints a progress bar.
    
    How to:
    1) set up progress display 
        progr = ProgressDisplay(ntotal)
    2) start timer
        progr.start_timer()
    3) after each step (with ntotal steps)
        progr.update_and_print()
    4) when finished
        progr.stop()
        
    Developed during ML Lab Course.
    """
    def __init__(self, ntotal, nprocessed = 0, unit="m", eol = "\r"):
        self.ntotal = ntotal
        self.nprocessed = nprocessed
        self.eol = eol
        self.nleft = ntotal
        self.unit = unit
        self.len_of_last_line = 1
        
    def start_timer(self):
        self.tstart = time.time()
        return self
    
    def update(self, nnew):
        """
        nnew: number of tasks processed since last update
        """
        self.nprocessed += nnew
        self.nleft -= nnew
    
    def compute_estimated_time_left(self):
        time_passed = time.time() - self.tstart
        time_left   = time_passed * self.nleft / self.nprocessed
        
        return self.calc_time_in_unit(time_left)
    
    def calc_time_in_unit(self, t):
        if self.unit == "m":
            t = t / 60
        elif self.unit == "h":
            t = t / 3600
        elif self.unit == "s":
            t = t
        else:
            raise
        return round(t, 2)
        
    def print_status(self):
        progress_display = f"{self.nprocessed}/{self.ntotal}"
        if self.nprocessed == 0:
            timeleft_display = "unknown"
        else:
            time_left = self.compute_estimated_time_left()
            timeleft_display = f"{time_left} {self.unit}"
        
        print("\r", " "*self.len_of_last_line, end="\r") # flush line
        display = f"\rprocessed {progress_display}, est. time left: {timeleft_display}"
        print("\r", display, end="\r")
        self.len_of_last_line = len(display)
        
    def update_and_print(self, nnew=1):
        self.update(nnew)
        self.print_status()
    
    def stop(self):
        total_time = self.calc_time_in_unit( time.time()-self.tstart )
        print(f"\n   total time: {total_time} {self.unit}\n")