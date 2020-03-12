## Data 
- Raw data Downloaded as per `download_conus_2016.sh` from https://data.fs.usda.gov/geodata/rastergateway/treecanopycover/index.php
- There are additioanlly some files (e.g. lower resolution shapefiles) that were processed by a script and can be found (with additional documentation) here: https://www.kaggle.com/zwrankin/usfs-tree-canopy-cover. This was largely to accomodate Kaggle Datasets 20GB limit. 
- TODO - add scripts that manipulated the data 

## Docker notes
Due to complex GDAL dependencies, the Kaggle [Docker image](https://github.com/Kaggle/docker-python/blob/master/Dockerfile) does not include `rasterio`. For using the regular tcc shapefiles (e.g. the ones in the Kaggle dataset), you can use the normal Kaggle docker (which includes e.g. `geopandas` and `fiona`) as the instruction in the main blog README. However, if you want to use the raw raw CONUS_2016 data (which has the highest resolution 30x30meter grid), here is a `Dockerfile` that can be used for all necessary dependencies. 
```
RUN pip install GDAL==2.4.2 && \
    pip install geopandas && \
    pip install rasterio && \ 
    pip install darkskylib && \ 
    pip install sklearn && \ 
    pip install geojson && \ 
    pip install folium && \
    pip install seaborn && \
    sudo apt-get install libgeos-dev
```