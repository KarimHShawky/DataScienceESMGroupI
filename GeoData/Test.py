
import pandas as pd 
import geopandas as gpd
import atlite as at

path=gpd.read_file('gadm_410-levels-ADM_1-JPN.gpkg')
print(path.geometry)