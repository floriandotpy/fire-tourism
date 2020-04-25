fire-tourism
===

Exploring tourism and its relation to wild fire occurrences.

A hackathon project during 2020's AI For Good hackathon in Berlin, Germany.

## Python Setup

1. Install Anaconda or Miniconda on your platform: https://conda.io/projects/conda/en/latest/user-guide/install/index.html
2. Create an environment for Python 3.6 `conda create -n fire-tourism python=3.7`
3. Activate environment `conda activate fire-tourism`
4. Sanity check: Python should point to the correct version now. 
```
$ python -V
Python 3.7.7
```
5. Install dependencies `pip install -r requirements.txt`
6. Install dependencies that are better installed via conda `conda install -c conda-forge --file requirements_via_conda.txt`

You're now set to go.

## Run notebooks

```
jupyter notebook .
```

This should automatically open a browser. If not, do so yourself and head to `http://localhost:8888/tree`

Click on any notebook (`*.ipynb` file) and start playing.



## Fetch datasets

`sh download_datasets.sh`