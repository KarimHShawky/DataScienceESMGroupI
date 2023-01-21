
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
path=gpd.read_file('gadm_410-levels-ADM_1-JPN.gpkg') #layer 1 admin regions jpn
#print(path.NAME_1)
Level1=gpd.read_file("gadmJPN-Level1Areas.json")
Level1['ISO_1'].iloc[26]='JP-42'
Level1['ISO_1'].iloc[12]='JP-28'
path['ISO_1']=Level1['ISO_1']
path.merge(Level1, on = 'ISO_1')

#%% read csv data (load  & Powerplants)
load=gpd.read_file('load.csv')
powerplants=gpd.read_file('global_power_plant_database.csv')
powerplants = powerplants[powerplants['country'] == 'JPN']
powerplants_gdf = gpd.GeoDataFrame(powerplants, geometry=gpd.points_from_xy(powerplants.longitude, powerplants.latitude))
#%%

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
def plot_area(masked, transform, shape):
    fig, ax = plt.subplots(figsize=(5,5))
    ax = show(masked, transform=transform, cmap='Greens', vmin=0, ax=ax)
    shape.plot(ax=ax, edgecolor='k', color='None', linewidth=2)

excluder = ExclusionContainer(crs=3035)
#excluder.add_geometry('gadm_410-levels-ADM_1-JPN.gpkg') # wurde oben verwendet
excluder.add_geometry('eez_boundaries_v11.gpkg') #marine regions
excluder.add_geometry('ne_10m_roads.gpkg')          #roeads
excluder.add_geometry('ne_10m_airports.gpkg')       #airports
excluder.add_raster('WDPA_Oct2022_Public_shp-JPN.tif', codes=[1,2,3,4,5,6], buffer=1200, crs=3035)
excluder.add_raster('PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326-JP.tif', codes=[1,2,3,4,5,6], buffer=1200, crs=3035) #copernicus land 100 m 
# PORBAV doesen't make any difference in the plot ??
shape = Geo1.to_crs(excluder.crs)
#shape[0]

band, transform = shape_availability(shape, excluder)
plot_area(band, transform, shape)
powerplants_gdf.plot(ax=ax, marker='o', color='black', markersize=5)

shape2 = Geo2.to_crs(excluder.crs)
#shape[0]

band, transform = shape_availability(shape2, excluder)
plot_area(band, transform, shape2)

shape3 = Geo3.to_crs(excluder.crs)
#shape[0]

band, transform = shape_availability(shape3, excluder)
plot_area(band, transform, shape3)

shape4 = Geo4.to_crs(excluder.crs)
#shape[0]

band, transform = shape_availability(shape4, excluder)
plot_area(band, transform, shape4)

shape5 = Geo5.to_crs(excluder.crs)
#shape[0]

band, transform = shape_availability(shape5, excluder)
plot_area(band, transform, shape5)


