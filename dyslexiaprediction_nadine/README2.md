# ePodium: EEGs and dyslexia risk in children 

The code notebooks in this folder accompany original research by Nadine Prins. 
The code relies on the eegyolk library.


<p align="center">
    <img style="width: 30%; height: 30%" src="https://github.com/NLeSC/ePodium/blob/main/eegyolk_logo.png">
</p>

# eegyolk

[![PyPI](https://img.shields.io/pypi/v/eegyolk.svg)](https://pypi.python.org/pypi/eegyolk/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6865762.svg)](https://doi.org/10.5281/zenodo.6865762)
[![Anaconda-Server Badge](https://anaconda.org/eegyolk/eegyolk/badges/version.svg)](https://anaconda.org/eegyolk/eegyolk)
[![Sanity](https://github.com/eegyolk-ai/eegyolk/actions/workflows/on-commit.yml/badge.svg)](https://github.com/eegyolk-ai/eegyolk/actions/workflows/on-commit.yml)
[![Sanity](https://github.com/eegyolk-ai/eegyolk/actions/workflows/on-tag.yml/badge.svg)](https://github.com/eegyolk-ai/eegyolk/actions/workflows/on-tag.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


This library contains functions, scripts and notebooks for machine learning related to EEGs (electroencephalograms). 

## Notebooks
The notebooks in this folder have a specific order, since the output of one notebook will be used as input for another notebook. 

Data preparation on raw EEGs: 
- `data_prep_eeg.ipynb`
- `data_analysis.ipynb`
Output: `metadata.csv`

Model data preparation: 
- `Input_mmr_prep.ipynb`
- `Input_connectivity_prep.ipynb`
Output: `df_avg_mmr.csv` and `df_connectivity.csv`

Machine Learning models: 
- `ML_on_mmr_data.ipynb`
- `ML_on_connectivity_data.ipynb`


## Data sets

Collection of newer data acquired to detect dyslexia on a different protocol ended in 2022. This data is not yet public, however, there are many public EEG datasets to which the functions in this library can be applied.

NLeSC employees can download some additional data from [surfdrive](https://surfdrive.surf.nl/files/index.php/s/mkwBAisnYUaPRhy).
Contact Candace Makeda Moore (c.moore@esciencecenter.nl) to discuss additional access to the data.

## Getting started 

How to get the notebooks running? Assuming the raw data set and metadata is available.

1. Install all Python packages required, using conda and the environment-march-update2.yaml file.
    Run the following line on your machine: `conda env create -f current_enviro2.yml` and switch to this environment running command: `conda activate mne-marchez`.
2. Install eegyolk: pip install the eegyolk library in the suggested version in the notebooks 
   (you can also clone the repo and   work locally but this requires a few additional manuevers of code in terms of imports)
3. Update the configuration by examining config.py and adding a .eegyolk folder on your server as implied (see general readme file for clarification)
4. Run the data preperation notebook `data_prep_eeg.ipynb`. Make sure that the folder names are correctly adjusted. 
5. The `data_prep_eeg.ipynb` notebook gives as output the file `metadata.csv`. This file can be used for the `data_analysis.ipynb` notebook to analyze the data. 
6. 'metadata.csv` is the input for the `Input_mmr_prep.ipynb` and the 'Input_connectivity_prep.csv'. The notebooks generate the data which will be used as input for the ML models. The first notebook is based on the mismatch response between a standard stimulus and a deviant stimulus. The second notebook calculates the connectivity between sensors. 
7. The generated files `df_avg_mmr.csv` and `df_connectivity.csv` can be used as input for the Machine Learning notebooks `ML_on_mmr_data.ipynb` and `ML_on_connectivity_data.ipynb` respectively. 

