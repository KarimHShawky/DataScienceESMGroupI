
import pandas as pd 
import geopandas as gpd
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import cartopy as cp
import cartopy.crs as ccrs
from atlite.gis import shape_availability, ExclusionContainer
from rasterio.plot import show
import pyomo as po
import pyomo.environ as pe
import pypsa as psa
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


#Total Population ca. 124.840.000
path=gpd.read_file('gadm_410-levels-ADM_1-JPN.gpkg')
#print(path.NAME_1)
Level1=gpd.read_file("gadmJPN-Level1Areas.json")
Level1['ISO_1'].iloc[26]='JP-42'
Level1['ISO_1'].iloc[12]='JP-28'
path['ISO_1']=Level1['ISO_1']
path.merge(Level1, on = 'ISO_1')


path['ISO_1']= path['ISO_1'].str.extract('(\d+)')
path['ISO_1'] = path['ISO_1'].astype(int)


Region1= path.loc[path['ISO_1'] == 1] # Pop.%  4.26%
Region2= path.loc[(path['ISO_1'] >1) & (path['ISO_1'] < 8)] # 7.01%
Region3= path.loc[(path['ISO_1'] >7) & (path['ISO_1'] < 24)]# 50.99%
Region4= path.loc[(path['ISO_1'] >23) & (path['ISO_1'] < 40)]# # 26.48%
Region5= path.loc[(path['ISO_1'] >39) ]# 11.27%


#%%

# Use the dissolve method to merge the polygons
Geo1 = Region1['geometry']
Geo2 = Region2.dissolve(by=None, aggfunc='first', as_index=True)
Geo3 = Region3.dissolve(by=None, aggfunc='first', as_index=True)
Geo4 = Region4.dissolve(by=None, aggfunc='first', as_index=True)
Geo5 = Region5.dissolve(by=None, aggfunc='first', as_index=True)


Geo2= Geo2['geometry']
Geo3= Geo3['geometry']
Geo4= Geo4['geometry']
Geo5= Geo5['geometry']


fig = plt.figure(figsize=(13,7))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.7)
ax.add_feature(cp.feature.BORDERS, color="grey", linewidth=0.3)


Geo1.plot(ax=ax, color="red")
Geo2.plot(ax=ax, color="gold")
Geo3.plot(ax=ax, color="green")
Geo4.plot(ax=ax, color="blue")
Geo5.plot(ax=ax, color="gray")

#%%

#from shapely.ops import unary_union

# Get the geometries from the geometry column
#geometries = gdf['geometry']

# Use the unary_union method to merge the geometries
#merged_geometry = unary_union(geometries)

#%%

#import pygeos

#geometries = gdf["geometry"].values
#merged = pygeos.unary_union(geometries)

#%%

excluder = ExclusionContainer(crs=3035)
excluder.add_geometry('ne_10m_roads.gpkg')
excluder.add_geometry('ne_10m_airports.gpkg')

shape = path.to_crs(excluder.crs).geometry
shape[0]

band, transform = shape_availability(shape, excluder)

