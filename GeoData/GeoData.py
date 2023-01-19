import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import cartopy as cp
import cartopy.crs as ccrs
import pyomo as po
import pyomo.environ as pe
import pypsa as psa
import warnings
warnings.filterwarnings('ignore')


#initialize the GeoDataFrame
DTB = "https://tubcloud.tu-berlin.de/s/mb4mPpk8rDC9ZaP/download/global_power_plant_database.csv"
database = pd.read_csv(DTB, index_col = 0)._convert(numeric=True)
geometry = gpd.points_from_xy(database["longitude"], database["latitude"])
geo_database = gpd.GeoDataFrame(database, geometry=geometry, crs=4326)