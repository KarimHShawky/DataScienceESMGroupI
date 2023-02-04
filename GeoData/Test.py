#%% IMPORTS
import pandas as pd 
import numpy as np
import geopandas as gpd

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import cartopy as cp
import cartopy.crs as ccrs

import atlite
from atlite.gis import shape_availability, ExclusionContainer

import rasterio
from rasterio.plot import show
from rasterio.transform import from_origin
from rasterio.features import geometry_mask

import pyomo as po
import pyomo.environ as pe

import pypsa as psa

from shapely.geometry import LineString

from vresutils.graph import voronoi_partition_pts

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
powerplants = powerplants.drop_duplicates()
# Drop all Hydros pre 1970
powerplants_hydro= powerplants[powerplants['primary_fuel'] == 'Hydro']
powerplants_hydro.to_csv('Powerplants_hydro.csv')
powerplants_gdf = gpd.GeoDataFrame(powerplants, geometry=gpd.points_from_xy(powerplants.longitude, powerplants.latitude))
ComY=pd.read_csv('ComissioningYears.csv',sep=";")
powerplants_hydro = powerplants_hydro.merge(ComY, on='name')
powerplants_hydro['commissioning_year_y']=powerplants_hydro['commissioning_year_y'].astype(int)
powerplants_hydro = powerplants_hydro.loc[powerplants_hydro['commissioning_year_y'] >= 1970]

#%% Defining Regions

path['ISO_1']= path['ISO_1'].str.extract('(\d+)')
path['ISO_1'] = path['ISO_1'].astype(int)

                                                                    # Pop. %
Region1= path.loc[path['ISO_1'] == 1]                               # 4.26%
Region2= path.loc[(path['ISO_1'] >1) & (path['ISO_1'] < 8)]         # 7.01%
Region3= path.loc[(path['ISO_1'] >7) & (path['ISO_1'] < 24)]        # 50.99%
Region4= path.loc[(path['ISO_1'] >23) & (path['ISO_1'] < 40)]       # 26.48%
Region5= path.loc[(path['ISO_1'] >39) ]                             # 11.27%


#%% Plotting the Regions

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


#%%Region distance

#point1 = Geo1.representative_point()
#point2 = Geo2.representative_point()
#point3 = Geo4.representative_point()
#point4 = Geo4.representative_point()
#point4 = Geo5.representative_point()
#Jpoints= pd.DataFrame[point1, point2, point3, point4, point5]
#distances = pd.concat({k: points.distance(p) for k, p in points.items()}, axis=1).div(1e3) # km
#distances.loc["DEU", "NLD"]


#<<<<<<< HEAD
#import pygeos

#geometries = gdf["geometry"].values
#merged = pygeos.unary_union(geometries)

#=======
#>>>>>>> 73e6ead37b1b30b933169569c139fe3b0cf0b408

#%% separate Powerplants into Regions 
#powerplants_gdf['Region'] = None
#for i, row in powerplants_gdf.iterrows():
#    for j, geo in enumerate(['Geo1', 'Geo2', 'Geo3', 'Geo4', 'Geo5']):
#        if row['geometry'].within(eval(geo)['geometry'].unary_union):
#            powerplants_gdf.at[i, 'Region'] = geo

# create DF from regions (Geo1-Geo5) to compare geometry 

#union = Geo1.unary_union
#Geo1 = union.envelope

Geo1_gdf = gpd.GeoDataFrame(gpd.GeoSeries(Geo1))
Geo2_gdf = gpd.GeoDataFrame(gpd.GeoSeries(Geo2))
Geo3_gdf = gpd.GeoDataFrame(gpd.GeoSeries(Geo3))#.to_crs(54009)
Geo4_gdf = gpd.GeoDataFrame(gpd.GeoSeries(Geo4))#.to_crs(4087)
Geo5_gdf = gpd.GeoDataFrame(gpd.GeoSeries(Geo5))#.to_crs(4087)

#Geo1_gdf = Geo1_gdf.rename(columns={0:'geometry'}).set_geometry('geometry').to_crs(4087)
GeoRegions_gdf = Geo1_gdf.append(Geo2_gdf, ignore_index=True)
GeoRegions_gdf = GeoRegions_gdf.append(Geo3_gdf, ignore_index=True)
GeoRegions_gdf = GeoRegions_gdf.append(Geo4_gdf, ignore_index=True)
GeoRegions_gdf = GeoRegions_gdf.append(Geo5_gdf, ignore_index=True)
GeoRegions_gdf = GeoRegions_gdf.rename(columns={0:'geometry'}).set_geometry('geometry')#.to_crs(4087)

powerplants_geometry= powerplants_gdf
powerplants_geo_gdf = gpd.GeoDataFrame((powerplants_geometry)).set_crs(4326, allow_override = True)#, crs=4326)



#powerplants_geo_gdf = powerplants_geo_gdf.to_crs(crs="4326", inplace = True)
#powerplants_geo_gdf.to_crs(crs = "4326", inplace = True)

powerplants_geo_gdf = powerplants_geo_gdf.rename(columns={0:'geometry'}).set_geometry('geometry')


#print("\nGeoDataFrame :\n", GeoRegions_gdf)
powerplants_w_Reg = gpd.sjoin(powerplants_geo_gdf, GeoRegions_gdf, how="left", op='within')
powerplants_w_Reg['index_right']+=1
powerplants_w_Reg.rename(columns={'index_right':'Georegion'}, inplace = True) 

# Realised, some Points ARE nan, menans we dont have 
# the whole landscape of Japan (missing islands?)

#%% Plot function

def plot_area(masked, transform, shape):
    fig, ax = plt.subplots(figsize=(27,27))
    ax = show(masked, transform=transform, cmap='Greens', vmin=0, ax=ax)
    shape.plot(ax=ax, edgecolor='k', color='None', linewidth=2)
    
#%% ExclusionContainer
excluder = ExclusionContainer(crs=3035, res=300)

#%% Excluders - Onwind

#excluder.add_geometry('ne_10m_roads.gpkg', buffer=300)          #Roads (dosent work :( , but the exclusion should be cover by the code 50 of PROBAV)

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
excluder.add_raster("GEBCO_2014_2D-JP.nc", codes=lambda x: x<2000, crs=4326, invert=True)


#onwind
#wind-ex=[1,2,3,4,5,6,7,8,9,10,11,15,16,17,22,23,24,25,27,30,31,34,35,36,37,38,39,40,41,42,43,44]
#wind-in=[12,13,14,18,19,20,21,26,28,29,32,33]
#exclude 6 (airports) with buffer 10km
#exclude 4 (roads) with buffer 300m
#exclude 1,2,3,7,8,9,11 (built up areas) with buffer 1000m

#%% Are these needed? shouldn't they be called once in the end?

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

#%% OFFWIND ALTERNATIVE
#excluder = ExclusionContainer(crs=3035, res=300)

eez = gpd.read_file("eez_v11.gpkg", crs=3035)

eez = eez.query("ISO_TER1 == 'JPN' and POL_TYPE == '200NM'")

gadm = gpd.read_file('gadm_410-levels-ADM_1-JPN.gpkg').set_index("NAME_1")

eez.plot()

eez_shape = eez.geometry

#%% Excluders - Offwind
excluder = ExclusionContainer(crs=3035, res=300)

#no natural protection areas
excluder.add_raster('WDPA_Oct2022_Public_shp-JPN.tif', crs=3035)

#10k min distance to shore
# excluder.add_geometry('eez_boundaries_v11.gpkg', buffer=20000)
excluder.add_geometry('gadm_410-levels-ADM_1-JPN.gpkg', buffer=10000)

#up to water depth of 50m + within EEZ
excluder.add_raster("GEBCO_2014_2D-JP.nc", codes=lambda x: x<-60, crs=4326)#, invert=True)

#excluder.add_raster("GEBCO_2014_2D-JP.nc", crs=4326)#, invert=True)

shape = eez_shape.to_crs(excluder.crs)
#shape[0]
band, transform = shape_availability(shape, excluder)
plot_area(band, transform, shape)
powerplants_gdf.plot(ax=ax, marker='o', color='black', markersize=5)

#%% Excluders - Solar
excluder = ExclusionContainer(crs=3035, res=300)

excluder.add_geometry('ne_10m_airports.gpkg', buffer=10000)     #Airports

# no natural protection areas

excluder.add_raster('WDPA_Oct2022_Public_shp-JPN.tif', crs=3035) 
#codes=[1,2,3,7,8,9,11],buffer=1000

# only on suitable land cover classes
excluder.add_raster('PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326-JP.tif',
                    codes=[10,15,16,17,22,23,24,25,27,30,31,34,39,40,43,44], crs=3035)
#Copernicus Global Land Service: Land Cover at 100 m 

#%% Add exclusions to each region and plot it (solar)

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


#%% Transmission lines 

# Define the transmission lines
transmission_lines = pd.DataFrame({'start_x': [Geo1.centroid.x, Geo2.centroid.x, Geo3.centroid.x,Geo4.centroid.x],
                                  'start_y': [Geo1.centroid.y, Geo2.centroid.y, Geo3.centroid.y, Geo4.centroid.y],
                                  'end_x': [Geo2.centroid.x, Geo3.centroid.x, Geo4.centroid.x,Geo5.centroid.x],
                                  'end_y': [Geo2.centroid.y, Geo3.centroid.y, Geo4.centroid.y, Geo5.centroid.y]})

# Create a geometry column for the transmission lines
transmission_lines['geometry'] = transmission_lines.apply(lambda x: LineString([(x.start_x, x.start_y), (x.end_x, x.end_y)]), axis=1)

# Create a GeoDataFrame for the transmission lines
transmission_lines_gdf = gpd.GeoDataFrame(transmission_lines, geometry='geometry')

#%% length of Transmission lines and afterwards marginal cost 
print(transmission_lines_gdf['geometry'][0].length, 'Transmission lines Region1-2 in 100km')
print(transmission_lines_gdf['geometry'][1].length, 'Transmission lines Region2-3 in 100km')
print(transmission_lines_gdf['geometry'][2].length, 'Transmission lines Region3-4 in 100km')
print(transmission_lines_gdf['geometry'][3].length, 'Transmission lines Region4-5 in 100km')

transmission_lines_gdf['Cost transmission line not specific per MW (still missing ADD LATER)']=transmission_lines_gdf['geometry'].length*100*1.5*400 # *(MW)  Cost = 1.5*400€/MW/length
print(transmission_lines_gdf['Cost transmission line not specific per MW (still missing ADD LATER)'])

#%%
# Plot the transmission lines on top of the regions
fig = plt.figure(figsize=(13,7))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.7)
ax.add_feature(cp.feature.BORDERS, color="grey", linewidth=0.3)

Geo1.plot(ax=ax, color="red")
Geo2.plot(ax=ax, color="gold")
Geo3.plot(ax=ax, color="green")
Geo4.plot(ax=ax, color="blue")
Geo5.plot(ax=ax, color="gray")
transmission_lines_gdf.plot(ax=ax, color='black', linewidth=2)

#%% Eligibility

print(band.any())
print(transform)

eligible_cells = band.sum()
cell_area = excluder.res**2
eligible_area = cell_area * eligible_cells
country_area = shape.geometry.area[11]
print(eligible_area / country_area * 100, '%')

Eligibility1 = band.sum() * (excluder.res)**2 / (shape.geometry.area[11] * 100)
#Eligibility2 = (band.sum() * (excluder.res**2)) / ((shape2.geometry.area[0]) * 100)
#Eligibility3 = (band.sum() * (excluder.res**2)) / ((shape3.geometry.area[0]) * 100)
#Eligibility4 = (band.sum() * (excluder.res**2)) / ((shape4.geometry.area[0]) * 100)
#Eligibility5 = (band.sum() * (excluder.res**2)) / ((shape5.geometry.area[0]) * 100)
