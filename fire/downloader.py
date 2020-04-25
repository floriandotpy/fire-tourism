import numpy as np
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests #todo: use either requests or urllib if possible
from netrc import netrc
import io
import os
from queue import Queue
from threading import Thread
from typing import List, Set, Dict, Tuple, Optional, Union, Any

# own utils
import fire.utils.etc as uetc
import fire.utils.io as uio


def collect_hyperlinks(page_url: str) -> List[str]:
    """
    Gets all URLs from hyperlinks (a href) on a given webpage.
    
    Args:
        page_url: The url of the page from which to scrape hyperlinks.
    
    Returns:
        List of str; URLs found in <a href=...> fields on the page.
    """
    urls = []
    page = urlopen( page_url ).read()
    soup = BeautifulSoup(page, "lxml")
    soup.prettify()
    
    for anchor in soup.findAll('a', href=True):
        complete_url = urljoin(page_url, anchor['href'])
        if complete_url not in urls:
            urls.append(complete_url)
    
    return urls

def collect_hdf_urls_from_lpdaac(
    product_root_url : str, 
    hdf_regex  : str = r"\.hdf$",
    date_regex : str = r"/\d{4}\.\d{2}\.\d{2}/?$",
    min_date : Optional[datetime] = None,
    max_date : Optional[datetime] = None,
    verbose : bool = True
) -> List[str]:
    """
    Gets the download URLs of all hdf-files for a given 
    product directory in the LP DAAC Data Pool [1]. 
    
    [1] https://lpdaac.usgs.gov/tools/data-pool/
    
    Args:
        product_root_url: 
            URL of the page refering to the product for
            which you want to collect all hdf URLs. This
            is the page which presents all the dates for
            which there is data as subdirectories.
            E.g. for MOD14A1 it would be (2020-02-11):
            https://e4ftl01.cr.usgs.gov/MOLT/MOD14A1.006/
        hdf_regex:
            Regex-pattern used to filter the URLs found on
            all the pages for hdf-files.
        verbose:
            Whether or not to show a progress bar.
        min_date, max_date (datetime): Dates to use for filtering
            which directories to fetch. Not too accurate, since
            the dates are usually only the start dates of the 8-day
            hdf files. 
            
    Returns:
        List (of str) of URLs pointing to hdf-files.

    Details:
        Not parallelized yet, thus pretty slow. #todo
    """
    hdf_urls  = []
    date_urls = collect_hyperlinks(product_root_url)
    date_urls = [u for u in date_urls 
                 if uetc.like(u, date_regex)]

    if min_date:
        date_urls = [u for u in date_urls 
                     if _get_dir_date_from_lpdaac_url(u) >= min_date]

    if max_date:
        date_urls = [u for u in date_urls 
                     if _get_dir_date_from_lpdaac_url(u) <= max_date]
    
    if verbose:
        progr = uetc.ProgressDisplay(len(date_urls))\
                    .start_timer()
    
    for d in date_urls: #todo => parallel loop! / Threading
        hdf_urls += [u for u in collect_hyperlinks(d)
                     if uetc.like(u, hdf_regex)]
        if verbose:
            progr.update_and_print()
    
    if verbose:
        progr.stop()
    
    return hdf_urls

def _get_dir_date_from_lpdaac_url(url: str) -> datetime:
    date_str = uetc.extract(url, r"[12][0-9]{3}\.[01][0-9]\.[0-3][0-9]")
    return datetime.strptime(date_str, r"%Y.%m.%d")
    
    
def fetch_hdf_files_from_lpdaac(urls: List[str],
                                target_paths: List[str],
                                auth: Any) -> None:
    """
    """
    # 
    pass

            
def fetch_file(url:str, target_path:str, auth:object,
               overwrite_existing:bool=True, 
               return_if_exists:bool=True,
               verbose:bool=True, log:bool=True) -> Union[bool, io.BytesIO]:
    """
    Downloads a file from url and writes it to target_path.
    
    Args:
        url:
            URLs to download
        target_path:
            The downloaded content will be written 
            to this path. 
        auth: 
            As expected by requests.get, e.g. a 
            Tuple[str, str] with values (user, password)
        return_if_exists:
            If there already is a file at the target path
            and overwriting is not enabled, this value is
            returned. If you want to keep track of what files you
            have locally, set to True. If you want to know
            what has been downloaded during this function call, 
            set to False. 
        verbose:
            Overrides log if verbose is set to False.
        log:
            If True and verbose True as well, warnings
            (file already exists or bad response) are written
            to logger instead of being printed to the console.
    Returns:
        True or False indicating whether the file was success-
        fully fetched and written to the target path. 
    """
    if (os.path.exists(target_path) 
        and not overwrite_existing):
        if verbose:
            msg = f"File already exists. {target_path}"
            logging.info(msg) if log else print(msg)
        return return_if_exists
    
    with requests.get(url, stream=True, auth=auth) as response:
        # check for bad response
        if response.status_code != 200:
            if verbose:
                msg = "Bad response while trying to fetch "\
                      f"(status code: {response.status_code})"
                logging.warning(msg) if log else print(msg)
            return False
        else:
            uio.makedirs(target_path)
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            return True


#todo: log
#todo: bad response => which one? resp. code
#todo: return results
#todo: catch requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
#todo: catch http.client.RemoteDisconnected: Remote end closed connection without response
#todo: urllib3.exceptions.ProtocolError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
def fetch_many_files(urls: List[str], target_paths:List[str], auth: Any,
                     n_parallel_downloads: int=10, overwrite_existing: bool=False, 
                     return_fetched_urls: bool=True, verbose: bool=True
                    ) -> List[str]:
    """
    
    Args:
        n_parallel_downloads:
            Number of downloads to run in parallel (as threads).
            #todo Beware: Content is downloaded in batches of size
            n_threads and all content of one batch is held in 
            memory until this batch is processed. Only then the
            content is written to disk #todo. 
            
    Details:
        With a lot of help of https://www.shanelynn.ie/using-python-threading-for-multiple-results-queue/
    """
    # check for duplicates in target_paths
    # these would raise problems when files are written 
    # (because of possible mutliple writes to one file at once)
    if (len(target_paths)) != len(set(target_paths)):
        raise ValueError("duplicates in target_paths") # or sth else?
    
    # set up queue
    q = Queue(maxsize=0) # infinite max queue size
    
    # init results list
    n = len(urls)
    results = [None] * n
    
    # fill queue with tasks, i.e. urls and corresponding targets
    enumerated_url_target_tuples = zip(range(n), urls, target_paths)
    for iut_tuple in enumerated_url_target_tuples:
        q.put(iut_tuple) # (i, url, target_path)
        
    # progress display
    if verbose:
        print(f"Downloading {n} files.\n")
        progr = uetc.ProgressDisplay(n).start_timer()
    else:
        progr = None
        
    # start worker threads
    for _ in range(n_parallel_downloads):
        worker = Thread(target=_fetch_files_worker,
                        args=(q, auth, results, overwrite_existing, progr))
        worker.setDaemon(True) # allows to exit a hanging thread
        worker.start()
        
    # wait until finished
    q.join()
    
    # end progress display
    if verbose:
        progr.stop()
        print("")
        print(f"\n{np.sum(results)}/{n} files downloaded successfully "
              f"({np.round(100*np.sum(results)/n,2)} %)")
    
    return results


def _fetch_files_worker(q:Queue, auth:object,
                        results:List[Union[str, io.BytesIO]],
                        overwrite_existing:bool=False,
                        progress_display=None
                       ) -> None:
    while not q.empty():
        # get unfinished task from tuple
        task = q.get() # task is a tuple (i, url, target_path)
        i, url, target_path = task
        
        # process task, thus a single url
        results[i] = fetch_file(url, target_path, auth, 
                                overwrite_existing=overwrite_existing,
                                verbose=False)
        
        # notify queue that task has been processed
        q.task_done()
        
        # update progress display
        if progress_display is not None:
            progress_display.update_and_print()
    return True
    
    
def get_auth_from_netrc(netrc_token:str, netrc_path:str="~/.netrc") -> Tuple[str,str]:
    """
    Get user and password from netrc file.
    
    Args:
        netrc_token: in netrc files called "machine name"
        
    Returns:
        Tuple[str,str] with values (user,password)
    """
    netrc_path = os.path.expanduser(netrc_path)
    usr = netrc(netrc_path).authenticators(netrc_token)[0]
    pwd = netrc(netrc_path).authenticators(netrc_token)[2]
    return (usr, pwd)
    
