# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 20:07:05 2023

@author: Athaanatos
"""
import geopandas as gpd

import matplotlib.pyplot as plt

from atlite.gis import shape_availability, ExclusionContainer

import rasterio
from rasterio.plot import show
from rasterio.features import geometry_mask

import os

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


path=gpd.read_file('gadm_410-levels-ADM_1-JPN.gpkg') #layer 1 admin regions jpn
Level1=gpd.read_file("gadmJPN-Level1Areas.json")
Level1['ISO_1'].iloc[26]='JP-42'
Level1['ISO_1'].iloc[12]='JP-28'
path['ISO_1']=Level1['ISO_1']
path.merge(Level1, on = 'ISO_1')
Region1= path.loc[path['ISO_1'] == 1] 
Geo1 = Region1['geometry']

load=gpd.read_file('load.csv')
powerplants=gpd.read_file('global_power_plant_database.csv')
powerplants = powerplants[powerplants['country'] == 'JPN']
powerplants = powerplants.drop_duplicates()
powerplants_gdf = gpd.GeoDataFrame(powerplants, geometry=gpd.points_from_xy(powerplants.longitude, powerplants.latitude))
#%%


excluder = ExclusionContainer(crs=3035)


#Airports + 10km
excluder.add_geometry('ne_10m_airports.gpkg', buffer=10000)       

#Protected Areas
excluder.add_raster('WDPA_Oct2022_Public_shp-JPN.tif',crs=3035)

# other non suitable areas
excluder.add_raster('PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326-JP.tif',
                    codes=[10,15,16,17,22,23,24,25,27,30,31,34,35,36,37,38,39,40,41,42,43,44] , crs=3035)

# 300m buffer from built up areas + roads
excluder.add_raster('PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326-JP.tif',
                    codes=[50], buffer=1000, crs=3035)

# maximum elevation of 2000m
df = gpd.read_file('eez_boundaries_v11.gpkg')

df = df[df['TERRITORY1'] == 'Japan']

eez_polygons = df['geometry']

with rasterio.open('GEBCO_2014_2D-JP.nc') as src:
    elevation = src.read(1)

mask = geometry_mask(eez_polygons, transform=src.transform, out_shape=src.shape)
elevation_within_eez = elevation.copy()
elevation_within_eez[~mask] = -9999

elevation_within_eez[elevation_within_eez > -2000] = -9999

try:
    os.remove("elevation_within_eez.tif")
except PermissionError:
    print("File deletion failed: Permission denied")
except FileNotFoundError:
    print("File not found, no need to delete")

try:
    with rasterio.open('elevation_within_eez.tif', 'w', driver='GTiff',
                       height=elevation_within_eez.shape[0],
                       width=elevation_within_eez.shape[1],
                       count=1, dtype=elevation_within_eez.dtype,
                       crs=src.crs, transform=src.transform) as dst:
        dst.write(elevation_within_eez, 1)
except Exception as e:
    print(f"An error occurred while creating the file: {e}")

excluder.add_raster('elevation_within_eez.tif', crs=3035)



def plot_area(masked, transform, shape):
    fig, ax = plt.subplots(figsize=(17,17))
    ax = show(masked, transform=transform, cmap='Greens', vmin=0, ax=ax)
    shape.plot(ax=ax, edgecolor='k', color='None', linewidth=2)


shape = Geo1.to_crs(excluder.crs)
#shape[0]

band, transform = shape_availability(shape, excluder)
plot_area(band, transform, shape)
powerplants_gdf.plot(ax=ax, marker='o', color='black', markersize=5)