
import pypsa as psa
import numpy as np
import pandas as pd
import geopandas as gpd


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
    network.add("Store", f"hydro_R{i}", bus=f"Region{i}", 
                 carrier="hydro",
                 capacity_p_max=20,
                 efficiency=0.8)























