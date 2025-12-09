import numpy as np
import pandas as pd
from helpers import *
from main import *

# variables

# pre-limiting variables

# pre limit h2 based on Kh_st>8.4

# cost function

cost = concrete_price*(volume(A, h4 + h5)+V_styliskos) + steel_price * total_steel_weight

# coarse grid search

# local area fine-search

# checks

print(Bactive/1000 > Zul) 
print(sed<sed_allowed)
print(Kh_st>8.4)
print(h3>0)
print(h2>=0.45 and h2<=0.45+float(epimikinsi_styliskoy))
print(prostheti_epixosi>=0.0)
print(prostheti_epixosi<=1.0 and prostheti_epixosi<=h2-0.1)