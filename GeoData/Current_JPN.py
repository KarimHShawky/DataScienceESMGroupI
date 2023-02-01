


import pandas as pd
import matplotlib.pyplot as plt

csv='global_power_plant_database.csv'
globalpowerplants= pd.read_csv(csv)
#globalpowerplants= globalpowerplants.dropna(subset='generation_data_source')
#globalpowerplants= globalpowerplants.loc[globalpowerplants['country']!= 'USA']
#globalpowerplants= globalpowerplants.loc[globalpowerplants['country']!= 'AUS']
#print(globalpowerplants['country_long'].unique())

japan_power=globalpowerplants.loc[globalpowerplants['country']== 'JPN']
japan_power=japan_power.drop(columns='country')
japan_power=japan_power.drop(columns='country_long')

japan_power=japan_power.reset_index()


jfuel= pd.DataFrame(japan_power.groupby('primary_fuel')['capacity_mw'].sum())


#jfuel['capacity_mw'].plot.pie(autopct='%1.1f', figsize=(7,7))

japan_power['capacity_factor'] = (japan_power.estimated_generation_gwh_2017 / japan_power.capacity_mw.div(1e3).mul(8760))

jfuel['average_capacity_factor']=japan_power.groupby('primary_fuel')['capacity_factor'].mean()
jfuel['estimated_generation_2017']=japan_power.groupby('primary_fuel')['estimated_generation_gwh_2017'].sum()
jfuel['estimated_generation_2017'].plot.pie(autopct='%1.1f', figsize=(7,7))

jpload= pd.read_csv('load.csv', usecols=['time', 'JP'], index_col=0, parse_dates=True )

jpload1=jpload.resample('3H').sum()




#%%
'Costs'
battery_storage_c= 187+ 215 # euro/kWh Battery storage + Inverter

offwind_c=1602.34 # euro/kWh
onwind_c= 	1077.17 # euro/kWh

solar_c=797.07 # euro/kWh solar_rooftop
solar_floating=942.86 #?

hydrogen_storage_c= 	3.6 *169.79 / 10.8e3 #  3.6 * euro/m^3 * 1/(kJ/m^3)
fuel_cell_c= 1200.0 #euro/kWh
electrolysis_c=550.0 # euro/kWh














