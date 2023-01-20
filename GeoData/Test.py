
import pandas as pd 
import geopandas as gpd
import atlite as at

path=gpd.read_file('gadm_410-levels-ADM_1-JPN.gpkg')
#print(path.NAME_1)
Level1=gpd.read_file("gadmJPN-Level1Areas.json")
path['ISO_1']=[]
path.merge(Level1, on = 'ISO_1')


path['ISO_1']= path['ISO_1'].str.extract('(\d+)')
#data = data.str.extract('(\d+)')

#print(path.ISO)
print(path['ISO'=='NA'])
