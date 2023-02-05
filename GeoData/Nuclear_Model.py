
import pypsa as psa
import numpy as np
import pandas as pd
import geopandas as gpd
import gurobipy as gupy
import Prep




year = 2050
url = f"https://raw.githubusercontent.com/PyPSA/technology-data/master/outputs/costs_{year}.csv"
costs = pd.read_csv(url, index_col=[0,1])
costs.loc[costs.unit.str.contains("/kW"), "value"] *= 1e3
costs.unit = costs.unit.str.replace("/kW", "/MW")
defaults = {
    "FOM": 0,
    "VOM": 0,
    "efficiency": 1,
    "fuel": 0,
    "investment": 0,
    "lifetime": 25,
    "CO2 intensity": 0,
    "discount rate": 0.07,
}
costs = costs.value.unstack().fillna(defaults)

def annuity(r, n):
    return r / (1.0 - 1.0 / (1.0 + r) ** n)

costs["marginal_cost"] = costs["VOM"] + costs["fuel"] / costs["efficiency"]

annuity = costs.apply(lambda x: annuity(0.07, x["lifetime"]), axis=1)

costs["capital_cost"] = (annuity + costs["FOM"] / 100) * costs["investment"]
 
#%%



network=psa.Network()

network.set_snapshots(Prep.load3.index)



#%%
for i in range (5):
    network.add('Bus', f"Region{i+1}", x= Prep.Geos[i].centroid.x ,y=Prep.Geos[i].centroid.y, v_nom=400, carrier= 'AC')
network.add('Bus', 'offwindRegion', )
#%%

for i in range(5):
    network.add("Store", f"battery_R{i+1}", bus=f"Region{i+1}", 
                 carrier="electricity")

for i in range(5):
    network.add("Store", f"hydrogen_R{i+1}", bus=f"Region{i+1}", 
                 carrier="hydrogen")

#%%

carriers = ["onwind", "offwind", "solar",  "hydrogen storage underground", "battery storage", "hydro power"]

network.madd(
    "Carrier",
    carriers, 
    color=["dodgerblue", "aquamarine", "gold",  "magenta", "yellowgreen", "green"],
   
)

#%%
network.add(
    'Generator',
    'offwind',
    bus= 'offwindRegion',
    carrier='offwind',
    capital_cost=costs.at['offwind', "capital_cost"],
    marginal_cost=costs.at['offwind', "marginal_cost"],
    efficiency=costs.at['offwind', "efficiency"],
    p_nom_extendable=True,
    #p_nom_max=
    )
for i in range(5):

    for tech in ["onwind",  "solar"]:
        network.add(
            "Generator",
            f'{tech}{i+1}' ,
            bus=f"Region{i+1}",
            carrier=tech,
            #p_nom_max=tech[i], Potential!!!
            capital_cost=costs.at[tech, "capital_cost"],
            marginal_cost=costs.at[tech, "marginal_cost"],
            efficiency=costs.at[tech, "efficiency"],
           p_nom_extendable=True,
           )
        
    network.add( "Generator",
     f'hydro power{i+1}',
     bus=f"Region{i+1}",
     carrier='hydro power',
     p_nom= Prep.hydro_sum.iloc[i] , 
     p_min_pu=0.136,
     p_max_pu=0.33,
     capital_cost=0,
     marginal_cost=0,
     
    p_nom_extendable=False,
    )
    
    
    
    network.add(
            "StorageUnit",
            f"battery storage{i+1}",
            bus=f"Region{i+1}",
            carrier="battery storage",
        max_hours=6,
        capital_cost=costs.at["battery inverter", "capital_cost"] + 6 * costs.at["battery storage", "capital_cost"],
        efficiency_store=costs.at["battery inverter", "efficiency"],
        efficiency_dispatch=costs.at["battery inverter", "efficiency"],
        p_nom_extendable=True,
        cyclic_state_of_charge=True,
        )




    capital_costs = (
        costs.at["electrolysis", "capital_cost"] +
        costs.at["fuel cell", "capital_cost"] +
        504 * costs.at["hydrogen storage underground", "capital_cost"]
        )

    network.add(
        "StorageUnit",
        f"hydrogen storage underground{i+1}",
        bus=f"Region{i+1}",
        carrier="hydrogen storage underground",
        max_hours=504,
        capital_cost= capital_costs,
        efficiency_store=costs.at["electrolysis", "efficiency"],
        efficiency_dispatch=costs.at["fuel cell", "efficiency"],
        p_nom_extendable=True,
        cyclic_state_of_charge=True,
        )
    
    
    network.add(
        "Load",
    f"demand{i+1}",
    bus=f"Region{i+1}",
    p_set=Prep.load3.JP*Prep.pop[i]
    )
    
    network.add(
        'Link', f'offwind{i+1}', bus0='offwindRegion', bus1=f'Region{i+1}', carrier='DC')

    network.add(
        "Generator",
        f'nuclear{i+1}' ,
        bus=f"Region{i+1}",
        carrier='nuclear',
        #p_max_pu=ts[tech], Potential!!!
        capital_cost=costs.at['nuclear', "capital_cost"],
        marginal_cost=costs.at['nuclear', "marginal_cost"],
        efficiency=costs.at['nuclear', "efficiency"],
       p_nom_extendable=True,
       )
    

#%%
for i in range(4):
    network.add("Line", f"Line{i+1}-{i+2}", bus0=f"Region{i+1}", bus1=f"Region{i+2}",
                capital_cost=400, length= 1.5*Prep.transmission_lines_gdf['geometry'][i].length*100
                 )

    network.add("Line", f"Line{i+2}-{i+1}", bus0=f"Region{i+2}", bus1=f"Region{i+1}",
                 capital_cost=400, length= 1.5*Prep.transmission_lines_gdf['geometry'][i].length*100
                  )
#%%
network.lopf(solver_name='gurobi')

Range=[0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3]


for k in Range:
    for j in range(5):
        network.generators.loc[f"nuclear{j+1}", "capital_costs"] = k* costs.at['nuclear', "capital_cost"]
        network.generators.loc[f"nuclear{j+1}", "marginal_costs"] = k*costs.at['nuclear', "marginal_cost"]
    network.lopf()
    network.export_to_csv_folder(f'nuclear{k}')





