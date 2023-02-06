
import pypsa as psa
import numpy as np
import pandas as pd
import geopandas as gpd
import gurobipy as gupy
import Prep

offwind_ts=Prep.offwind2013
onwind_ts=Prep.onwind2013
solar_ts=Prep.solar2013

offwind_ts=offwind_ts.clip(0.001,1)#, 
                               # a_min=0.001, 
                               # a_max=1)
for i in range (5):
    onwind_ts[i]=onwind_ts[i].clip(0.001,1)#, 
#    onwind_ts[i]=onwind_ts[i].drop(pd.Timestamp('2020-02-29 03:00:00')).clip(0.001,1)#,
 #   onwind_ts[i]=onwind_ts[i].drop(pd.Timestamp('2020-02-29 06:00:00')).clip(0.001,1)#, 
  #  onwind_ts[i]=onwind_ts[i].drop(pd.Timestamp('2020-02-29 09:00:00')).clip(0.001,1)#, 
  #  onwind_ts[i]=onwind_ts[i].drop(pd.Timestamp('2020-02-29 12:00:00')).clip(0.001,1)#, 
   # onwind_ts[i]=onwind_ts[i].drop(pd.Timestamp('2020-02-29 15:00:00')).clip(0.001,1)#, 
   # onwind_ts[i]=onwind_ts[i].drop(pd.Timestamp('2020-02-29 18:00:00')).clip(0.001,1)#, 
    
                                      #a_min=0.001, 
                                      #a_max=1))
    solar_ts[i]=solar_ts[i].clip(0.001,1)#, 
                                     #a_min=0.001, 
                                     #a_max=1))
#np.clip(onwind_ts, a_min=0.001, a_max=1)
#np.clip(offwind_ts, a_min=0.001, a_max=1)
#np.clip(solar_ts, a_min=0.001, a_max=1)

p_nom_max_off=Prep.p_nom_off
p_nom_max_on=Prep.p_nom_on
p_nom_max_sol=Prep.p_nom_sol

z = 1.66

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
network.snapshot_weightings.loc[:,:]=3

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
    p_nom_max = p_nom_max_off* z,
    p_max_pu= offwind_ts.iloc[:,0]
    
    )
for i in range(5):

    
    network.add(
            "Generator",
            f'onwind{i+1}' ,
            bus=f"Region{i+1}",
            carrier='onwind',
            p_max_pu= onwind_ts[i].iloc[:,0] ,
            p_nom_max=p_nom_max_on[i]* z ,
            capital_cost=costs.at['onwind', "capital_cost"],
            marginal_cost=costs.at['onwind', "marginal_cost"],
            efficiency=costs.at['onwind', "efficiency"],
           p_nom_extendable=True,
           )
    network.add(
            "Generator",
            f'solar{i+1}' ,
            bus=f"Region{i+1}",
            carrier='solar',
            p_max_pu= solar_ts[i].iloc[:,0],
            p_nom_max=p_nom_max_sol[i]* z ,
            capital_cost=costs.at['solar', "capital_cost"],
            marginal_cost=costs.at['solar', "marginal_cost"],
            efficiency=costs.at['solar', "efficiency"],
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

#%%
for i in range(4):
    network.add("Line", f"Line{i+1}-{i+2}", bus0=f"Region{i+1}", bus1=f"Region{i+2}",
                capital_cost=400, length= 1.5*Prep.transmission_lines_gdf['geometry'][i].length*100
                 )

network.generators_t.p_max_pu.plot(figsize=(6,2), ylabel="CF")
#%%
network.lopf(solver_name='gurobi')

network.export_to_csv_folder('Base_Model')

#%%
import matplotlib.pyplot as plt
def plot_dispatch(n, time="2013-09"):
    
    p_by_carrier = n.generators_t.p.groupby(n.generators.carrier, axis=1).sum().div(1e3)
    
    if not n.storage_units.empty:
        sto = n.storage_units_t.p.groupby(n.storage_units.carrier, axis=1).sum().div(1e3)
        p_by_carrier = pd.concat([p_by_carrier, sto], axis=1)
    
    fig, ax = plt.subplots(figsize=(6, 3))
    
    color = p_by_carrier.columns.map(n.carriers.color)
    
    p_by_carrier.where(p_by_carrier>0).loc[time].plot.area(
        ax=ax,
        linewidth=0,
        color=color,
    )
    
    charge = p_by_carrier.where(p_by_carrier<0).dropna(how='all', axis=1).loc[time]
    
    if not charge.empty:

        charge.plot.area(
            ax=ax,
            linewidth=0,
            color=charge.columns.map(n.carriers.color),
        )
    
    n.loads_t.p_set.sum(axis=1).loc[time].div(1e3).plot(ax=ax, c='k')

    plt.legend(loc=(1.05,0))
    ax.set_ylabel("GW")
    ax.set_ylim(-1000, 1400)
plot_dispatch(network)
#%%
line = network.lines
G = network.generators
B = network.buses
L = network.loads
network.loads_t.p_set.plot()

network.generators.p_nom_opt.div(1e3)
