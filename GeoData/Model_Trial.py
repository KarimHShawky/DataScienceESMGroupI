
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

network.add('Bus', "R1", x=point1[0],y=point1[1], v_nom=400, carrier= 'AC')
network.add('Bus', "R2", x=point2[0],y=point2[1], v_nom=400, carrier= 'AC')
network.add('Bus', "R3", x=point3[0],y=point3[1], v_nom=400, carrier= 'AC')
network.add('Bus', "R4", x=point4[0],y=point4[1], v_nom=400, carrier= 'AC')
network.add('Bus', "R5", x=point5[0],y=point5[1], v_nom=400, carrier= 'AC')


























