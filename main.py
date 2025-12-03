#print("Hello World!")

import pandas as pd
import numpy as np
from helpers import *

####  Known data  ####

concrete_price = 110  # €/m3
steel_price = 1.5  # €/kg

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

P = loads[Tower][0]*1000
Zul = loads[Tower][1]*1000
Zwo = loads[Tower][2]*1000
Hul = loads[Tower][3]*1000
Hp = loads[Tower][4]*1000

# Όγκος στυλίσκου
V_styliskos = volume(C1, h2 + h3) + volume(C1, 0.05/3)

# Συνολικό βάρος θεμελίωσης = βάρος στυλίσκου + βάρος πλάκας + βάρος επίχωσης + βάρος πρόσθετης + βάρος άοπλου - βάρος νερού
Btot    = weight(concrete_density, V_styliskos)\
        + weight(concrete_density, volume(A, h4))\
        + weight(epixosi_density, volume(A, h3 + prostheti_epixosi))\
        - weight(epixosi_density, volume(C1, h3 + prostheti_epixosi))\
        + weight(aoplo_density, volume(A, h5))\
        - weight(water_density, volume(A, water_height))

# Ενεργό βάρος θεμελίωσης = Συνολικό - βάρος άοπλου
Bactive = Btot - weight(aoplo_density, volume(A, h5))

# Καταπόνηση εδάφους
sed = (P + Btot)/(A**2)/10000  # kg/cm2
sed_worst_case = (P + Btot + weight(water_density, volume(A, water_height)))/(A**2)/10000

#-----------------------------
#### ΟΠΛΙΣΜΟΙ ΘΛΙΨΗΣ ####
#-----------------------------

Mp = 1/2*(sed*10)*Pr**2
Kh_c = (h4*100-5)/np.sqrt(Mp)

factor_c = 1.0  # συντελεστής για διπλούς οπλισμούς θλίψης
if Kh_c<9.4:
    factor_c = 2.0

kh_bins   = [8.40, 9.70, 12.55, 18.80, 25.90, np.inf]
kh_labels = [0.47, 0.46, 0.45, 0.44, 0.43]

Ke_c = pd.cut(pd.Series([Kh_c]), bins=kh_bins, labels=kh_labels, right=True).astype(float)

fex_c = Ke_c*Mp/(h4-0.05)

compression_options = compression_rod_selection(fex_c[0])
compression_selected =  compression_options[5].values[0]  

compression_rod_length = A - 2*buffer
compression_rod_spacing = compression_rod_parser(compression_selected)[1]
compression_rod_number = int((compression_rod_length)/(compression_rod_spacing/100)+1)*2*factor_c

#-----------------------------
#### ΟΠΛΙΣΜΟΙ ΕΦΕΛΚΥΣΜΟΥ ####
#-----------------------------

# βάρος επίχωσης ανά μονάδα επιφάνειας
qep = (weight(epixosi_density, volume(A, h3 + prostheti_epixosi))\
        - weight(epixosi_density, volume(C1, h3 + prostheti_epixosi)))/(A**2-C1**2)

# βάρος πλάκας ανά μονάδα επιφάνειας
qb = weight(concrete_density, volume(A, h4))/(A**2)

Mul = 0.5*Pr**2*(qep + qb)/1000

Kh_u = (h4*100-5)/np.sqrt(Mul)

factor_u = 1.0  # συντελεστής για διπλούς οπλισμούς εφελκυσμού
if Kh_u<9.4: 
        factor_u = 2.0

Ke_u = pd.cut(pd.Series([Kh_u]), bins=kh_bins, labels=kh_labels, right=True).astype(float)

fex_u = Ke_u*Mul/(h4-0.05)

uplift_options = uplift_rod_selection(fex_u[0])
uplift_selected =  uplift_options[5].values[0]   

uplift_rod_length = A - 2*buffer
uplift_rod_spacing = uplift_rod_parser(uplift_selected)[1]
uplift_rod_number = int((uplift_rod_length)/(uplift_rod_spacing/100)+1)*2*factor_u


#-----------------------------
#### ΟΠΛΙΣΜΟΙ ΣΤΥΛΙΣΚΟΥ ####
#-----------------------------

Mst = (h1 + h2 + h3)*Hul/1000

Kh_st = (C1*100-5)/np.sqrt(Mst/C1)

Ke_st = pd.cut(pd.Series([Kh_st]), bins=kh_bins, labels=kh_labels, right=True).astype(float)

fex_st = Ke_st*Mst/(C1 - 0.05)

styliskos_options = styliskos_rod_selection(fex_st[0])
styliskos_selected_main = styliskos_options[0].values[0]
styliskos_selected_aux  = styliskos_options[1]

styliskos_rod_length = H + h1 + h2 - h5 - 0.15

styliskos_rod_number1= styliskos_rod_parser(styliskos_selected_main)[0]
styliskos_rod_diameter1= styliskos_rod_parser(styliskos_selected_main)[1]
styliskos_rod_number2= styliskos_rod_parser(styliskos_selected_main)[2]
styliskos_rod_diameter2= styliskos_rod_parser(styliskos_selected_main)[3]

styliskos_tserki_length = (C1 - 2*buffer)*4 + 0.10*2 
styliskos_tserki_diameter, styliskos_tserki_spacing = styliskos_tserki_parser(styliskos_selected_aux)
styliskos_tserki_number = np.ceil((styliskos_rod_length)/(styliskos_tserki_spacing/100)+1)

#----------------------------
####      ΑΠΟΣΤΑΤΕΣ      ####
#----------------------------

apostates_length = (h4 - 2*buffer)+0.10*2
apostates_number = int((A-2*buffer)**2)

#-------------------------------------------
#### ΠΡΟΣΘΕΤΟΙ ΟΠΛΙΣΜΟΙ ΕΦΕΛΚΥΣΜΟΥ      ####
#-------------------------------------------

extra_rod_diameter = 20.0 #cn
extra_rod_spacing = 0.45  #m
extra_rod_length = uplift_rod_length/2 + (h4-2*buffer)*2 + 0.25*2
extra_rod_number = np.ceil((uplift_rod_length/2/extra_rod_spacing+1)*2)

#-------------------------------------------
####          Kostos          ####
#-------------------------------------------

Ogkos_ekskafis = A**2*H  # m3
Ogkos_betou = V_styliskos + volume(A, h4) + volume(A, h5)  # m3
Ogkos_epixosis = (A**2 - C1**2)*(h3 + prostheti_epixosi)  # m3

columns = ['Χαρακτηρισμός','Οπλισμός','Τεμάχια','Μήκος','Βάρος/τεμ. (kg)','Συνολικό βάρος (kg)'] 


#### run module ####
if __name__ == "__main__":
    
        pass