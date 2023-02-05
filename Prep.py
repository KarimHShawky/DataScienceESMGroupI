
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

load3=jpload.resample('3H').sum() #MWh

pop=[0.0426, 0.0701, 0.5099, 0.2648, 0.1127]

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
for i in range(5):
    
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



#%%
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

Geo_gdf= list(range(len(Regions)))
for i in range(5):
    Geo_gdf[i] = gpd.GeoDataFrame(gpd.GeoSeries(Geos[i]))
  
GeoTotal_gdf = Geo_gdf[0].append(Geo_gdf[1], ignore_index=True)

for i in range(4):
        GeoTotal_gdf=GeoTotal_gdf.append(Geo_gdf[i+1], ignore_index=True)


powerplants_geometry= powerplants_gdf
powerplants_geo_gdf = gpd.GeoDataFrame((powerplants_geometry)).set_crs(4326, allow_override = True)#, crs=4326)



#powerplants_geo_gdf = powerplants_geo_gdf.to_crs(crs="4326", inplace = True)
#powerplants_geo_gdf.to_crs(crs = "4326", inplace = True)

powerplants_geo_gdf = powerplants_geo_gdf.rename(columns={0:'geometry'}).set_geometry('geometry')


#print("\nGeoDataFrame :\n", GeoRegions_gdf)
powerplants_w_Reg = gpd.sjoin(powerplants_geo_gdf, GeoTotal_gdf, how="left", op='within')
powerplants_w_Reg['index_right']+=1
powerplants_w_Reg.rename(columns={'index_right':'Georegion'}, inplace = True) 
powerplants_w_Reg['capacity_mw']=powerplants_w_Reg['capacity_mw'].astype(float)
hydro_sum = powerplants_w_Reg.groupby('Georegion')['capacity_mw'].sum()

# Realised, some Points ARE nan, menans we dont have 
# the whole landscape of Japan (missing islands?)

#%%

onwind2020=list(range(len(Regions)))
solar2020=list(range(len(Regions)))

onwind2019=list(range(len(Regions)))
solar2019=list(range(len(Regions)))

onwind2013=list(range(len(Regions)))
solar2013=list(range(len(Regions)))

p_nom_on=list(range(len(Regions)))
p_nom_sol=list(range(len(Regions)))

for i in range(5):

    onwind2020[i]=pd.read_csv(f'onwind{i+1}_2020.csv',  index_col=0, parse_dates=True)
    solar2020[i]=pd.read_csv(f'solar{i+1}_2020.csv', index_col=0,parse_dates=True)

    solar2019[i]=pd.read_csv(f'solar{i+1}_2019.csv', index_col=0,parse_dates=True)
    onwind2019[i]=pd.read_csv(f'onwind{i+1}_2019.csv',  index_col=0, parse_dates=True)
    
    onwind2013[i]=pd.read_csv(f'onwind{i+1}_2013-1.csv',  index_col=0, parse_dates=True)
    solar2013[i]=pd.read_csv(f'solar{i+1}_2013-1.csv', index_col=0,parse_dates=True)
    
    on=pd.read_csv(f'onwind{i+1}_2020MW.csv',  index_col=0, parse_dates=True)
    sol=pd.read_csv(f'solar{i+1}_2020MW.csv', index_col=0,parse_dates=True)
    
    p_nom_on[i]=1/(onwind2020[i].iloc[0]/on.iloc[0])
    p_nom_sol[i]=1/(solar2020[i].iloc[0]/sol.iloc[0])

offwind2020=pd.read_csv('Offwind_2020.csv', index_col=0 ,parse_dates=True)
offwind2019=pd.read_csv('Offwind_2019.csv', index_col=0 ,parse_dates=True)

offwind2013=pd.read_csv('Offwind_2013-1.csv', index_col=0 ,parse_dates=True)

#onwind2020[0].plot(figsize=(27,27))

off=pd.read_csv('Offwind_2020-MW.csv', index_col=0 ,parse_dates=True)

p_nom_off=1/(offwind2020.iloc[0]/off.iloc[0])

print(solar2020[0].iloc[:,0])
