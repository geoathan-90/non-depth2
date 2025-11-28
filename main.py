#print("Hello World!")

import pandas as pd
import numpy as np

#### basic functions ####

def volume(side, height):               # όγκος (πλευρά, ύψος)
    return side**2 * height             #        = πλευρά^2 * ύψος

def weight(density, volume):            # βάρος (πυκνότητα, όγκος)  
    return density * volume             #       = πυκνότητα * όγκος 

####  Known data  ####

water_density = 1000  # kg/m3           # ειδικό βάρος νερού
concrete_density = 2400  # kg/m3        # ειδικό βάρος οπλισμένου σκυροδέματος
aoplo_density = 2000  # kg/m3           # ειδικό βάρος άοπλου σκυροδέματος
epixosi_density = 1600  # kg/m3         # ειδικό βάρος επίχωσης

h1 = 0.05  # m στυλίσκος μέχρι κόμβο
h5 = 0.10  # m ύψος άοπλου μπετού

#### conditions ####

Tower = "T5"

sed_allowed = 0.5  # kg/cm2
water_height = 1.1  # m

buffer = 0.05 # m επικάλυψη οπλισμού

#### variables ####

prostheti_epixosi = 0.25  # m
H = 1.70  # m  Βάθος εκσκαφής μέχρι κάτω από το μπλοκέτο
h2 = 1.45  # m  ύψος στυλίσκου μέχρι κόμβο (σχεδόν)
h4 = 0.80  # m  ύψος κεφαλόδεσμου

C1 = 0.80  # m  πλευρά στυλίσκου
A = 8.10  # m πλευρά κεφαλόδεσμου

#### fundamental calcs ####

h3 = H-h4-h5 # m  ύψος επίχωσης

B = A/2 # m ημιπλευρά κεφαλόδεσμου
Pr = (A - C1)/2  # m μήκος "πρόβολου" κεφαλόδεσμου

loads = pd.read_csv('fortia_pyrgon.csv')

P = loads[Tower][0]
Zul = loads[Tower][1]
Zwo = loads[Tower][2]
Hul = loads[Tower][3]
Hp = loads[Tower][4]

# Όγκος στυλίσκου
V_styliskos = volume(C1, h2 + h3) + volume(C1, 0.05/3)

V_betoy= V_styliskos + volume(A, h4)

# Συνολικό βάρος θεμελίωσης = βάρος στυλίσκου + βάρος κεφαλόδεσμου + βάρος επίχωσης + βάρος πρόσθετης + βάρος άοπλου - βάρος νερού
Btot    = weight(concrete_density, V_styliskos)\
        + weight(concrete_density, volume(A, h4))\
        + weight(epixosi_density, volume(A, h3 + prostheti_epixosi))\
        - weight(epixosi_density, volume(C1, h3 + prostheti_epixosi))\
        + weight(aoplo_density, volume(A, h5))\
        - weight(water_density, volume(A, water_height))

# Ενεργό βάρος θεμελίωσης = Συνολικό - βάρος άοπλου
Bactive = Btot - weight(aoplo_density, volume(A, h5))

# Checks #

sed = (P + Btot)/(A**2)/10000  # kg/cm2


