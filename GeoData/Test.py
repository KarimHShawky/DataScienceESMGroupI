
import pandas as pd 
import geopandas as gpd
import atlite as at
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


Region1=path.loc[path['ISO_1'] == 1] # Pop.%  4.26%
Region2= path.loc[(path['ISO_1'] >1) & (path['ISO_1'] < 8)] # 7.01%
Region3= path.loc[(path['ISO_1'] >7) & (path['ISO_1'] < 24)]# 50.99%
Region4= path.loc[(path['ISO_1'] >23) & (path['ISO_1'] < 40)]# # 26.48%
Region5= path.loc[(path['ISO_1'] >39) ]# 11.27%


#%%

#import geopandas as gpd

# Load the GeoDataFrame
#gdf = gpd.read_file("file.geojson")

# Use the dissolve method to merge the polygons
#merged_gdf = gdf.dissolve(by=None, aggfunc='first', as_index=True)

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






