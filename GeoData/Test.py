
import pandas as pd 
import geopandas as gpd
import atlite as at

path=gpd.read_file('gadm_410-levels-ADM_1-JPN.gpkg')
#print(path.NAME_1)
Level1=gpd.read_file("gadmJPN-Level1Areas.json")
Level1['ISO_1'].iloc[26]='JP-42'
Level1['ISO_1'].iloc[12]='JP-28'
path['ISO_1']=Level1['ISO_1']
path.merge(Level1, on = 'ISO_1')


path['ISO_1']= path['ISO_1'].str.extract('(\d+)')

print(path.loc[path['ISO_1'] == 1])
#Region2= path.loc[]
#data = data.str.extract('(\d+)')

#print(path.ISO)
#print(path['ISO'=='NA'])
