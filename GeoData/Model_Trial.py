
import pypsa as psa
import numpy as np
import pandas as pd
import geopandas as gpd


year = 2050
url = f"https://raw.githubusercontent.com/PyPSA/technology-data/master/outpus/costs_{year}.csv"
costs = pd.read_csv(url, index_col=[0,1])


hydro_power=0

network=psa.Network()

point1=np.array[43, 40]
point2=np.array[43, 40]
point3=np.array[43, 40]
point4=np.array[43, 40]
point5=np.array[43, 40]

for i in range (5):
    network.add('Bus', f"Region{i}", x=f"point{i}"[0],y=f"point{i}"[1], v_nom=400, carrier= 'AC')

for i in range(5):
    network.add("Store", f"battery_R{i}", bus=f"Region{i}", 
                 carrier="electricity",
                 capacity_p_max=10,
                 efficiency=0.9)

for i in range(5):
    network.add("Store", f"hydrogen_R{i}", bus=f"Region{i}", 
                 carrier="hydrogen",
                 capacity_p_max=20,
                 efficiency=0.8)



carriers = ["onwind", "offwind", "solar",  "hydrogen storage underground", "battery storage", "hydro power"]

network.madd(
    "Carrier",
    carriers, 
    color=["dodgerblue", "aquamarine", "gold",  "magenta", "yellowgreen"],
    co2_emissions=[costs.at[c, "CO2 intensity"] for c in carriers]
)


for i in range(5):

    for tech in ["onwind", "offwind", "solar"]:
        network.add(
            "Generator",
            tech,
            bus=f"Region{i}",
            carrier=tech,
            #p_max_pu=ts[tech], Potential!!!
            capital_cost=costs.at[tech, "capital_cost"],
            marginal_cost=costs.at[tech, "marginal_cost"],
            efficiency=costs.at[tech, "efficiency"],
           p_nom_extendable=True,
           )
    network.add( "Generator",
     'hydro power',
     bus=f"Region{i}",
     carrier='hydro power',
     p_nom= hydro_power[i] , 
     capital_cost=0,
     marginal_cost=0,
     efficiency=costs.at[tech, "efficiency"],
    p_nom_extendable=True,
    )
    
    
    
    network.add(
            "StorageUnit",
            "battery storage",
            bus=f"Region{i}",
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
        "hydrogen storage underground",
        bus=f"Region{i}",
        carrier="hydrogen storage underground",
        max_hours=504,
        capital_cost=capital_costs,
        efficiency_store=costs.at["electrolysis", "efficiency"],
        efficiency_dispatch=costs.at["fuel cell", "efficiency"],
        p_nom_extendable=True,
        cyclic_state_of_charge=True,
        )

for i in range(4):
    network.add("Line", f"Line{i}-{i+1}", bus_0=f"Region{i}", bus_1=f"Region{i+1}",
                capital_costs=0, length= 0
                 )

    network.add("Line", f"Line{i+1}-{i}", bus_0=f"Region{i+1}", bus_1=f"Region{i}",
                 capital_costs=0, length= 0
                  )











