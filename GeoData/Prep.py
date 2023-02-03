
import pandas as pd 
import geopandas as gpd
import atlite
from atlite.gis import shape_availability, ExclusionContainer

from rasterio.plot import show
import pypsa as psa
from shapely.geometry import LineString

#Total Population ca. 124.840.000
path=gpd.read_file('gadm_410-levels-ADM_1-JPN.gpkg') #layer 1 admin regions jpn
#print(path.NAME_1)
Level1=gpd.read_file("gadmJPN-Level1Areas.json")
Level1['ISO_1'].iloc[26]='JP-42'
Level1['ISO_1'].iloc[12]='JP-28'
path['ISO_1']=Level1['ISO_1']
path.merge(Level1, on = 'ISO_1')


#%%
jpload= pd.read_csv('load.csv', usecols=['time', 'JP'], index_col=0, parse_dates=True ) #MW

load=jpload.resample('3H').sum() #MWh



#%% Defining Regions

path['ISO_1']= path['ISO_1'].str.extract('(\d+)')
path['ISO_1'] = path['ISO_1'].astype(int)

                                                                    # Pop. %
Region1= path.loc[path['ISO_1'] == 1]                               # 4.26%
Region2= path.loc[(path['ISO_1'] >1) & (path['ISO_1'] < 8)]         # 7.01%
Region3= path.loc[(path['ISO_1'] >7) & (path['ISO_1'] < 24)]        # 50.99%
Region4= path.loc[(path['ISO_1'] >23) & (path['ISO_1'] < 40)]       # 26.48%
Region5= path.loc[(path['ISO_1'] >39) ]                             # 11.27%

Regions= [Region1, Region2, Region3, Region4, Region5]
pop=[0.0426, 0.0701, 0.5099, 0.2648, 0.1127]
Geos= list(range(len(Regions)))
Geos[0] = Region1['geometry']
for i in range(4):
    
    Geos[i] = Regions[i].dissolve(by=None, aggfunc='first', as_index=True)
    Geos[i]= Geos[i]['geometry']


#%% Transmission lines 

# Define the transmission lines
transmission_lines = pd.DataFrame({'start_x': [Geos[0].centroid.x, Geos[1].centroid.x, Geos[2].centroid.x,Geos[3].centroid.x],
                                  'start_y': [Geos[0].centroid.y, Geos[1].centroid.y, Geos[2].centroid.y, Geos[3].centroid.y],
                                  'end_x': [Geos[1].centroid.x, Geos[2].centroid.x, Geos[3].centroid.x,Geos[4].centroid.x],
                                  'end_y': [Geos[1].centroid.y, Geos[2].centroid.y, Geos[3].centroid.y, Geos[4].centroid.y]})

# Create a geometry column for the transmission lines
transmission_lines['geometry'] = transmission_lines.apply(lambda x: LineString([(x.start_x, x.start_y), (x.end_x, x.end_y)]), axis=1)

# Create a GeoDataFrame for the transmission lines
transmission_lines_gdf = gpd.GeoDataFrame(transmission_lines, geometry='geometry')



















