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
compression_rod_diameter = compression_rod_parser(compression_selected)[0]

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
uplift_rod_diameter = uplift_rod_parser(uplift_selected)[0]

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

extra_rod_diameter = 20.0 #cm
extra_rod_spacing = 0.45  #m
extra_rod_length = uplift_rod_length/2 + (h4-2*buffer)*2 + 0.25*2
extra_rod_number = np.ceil((uplift_rod_length/2/extra_rod_spacing+1)*2)

#-------------------------------------------
#### Πίνακας οπλισμών (DataFrame)      ####
#-------------------------------------------

Ogkos_ekskafis = A**2*H  # m3
Ogkos_betou = V_styliskos + volume(A, h4) + volume(A, h5)  # m3
Ogkos_epixosis = (A**2 - C1**2)*(h3 + prostheti_epixosi)  # m3

#columns = ['Χαρακτηρισμός','Οπλισμός','Τεμάχια','Μήκος','Διάκενο','Βάρος/τεμ. (kg)','Συνολικό βάρος (kg)'] 

rows = []

#### 1. Οπλισμοί θλίψης πλάκας ####
comp_diameter, comp_spacing_cm = compression_rod_parser(compression_selected)
comp_w_kg_per_m = rebar_kg_per_m(comp_diameter)
comp_weight_per_piece = comp_w_kg_per_m * compression_rod_length

rows.append({
    'Χαρακτηρισμός': 'Πλάκα - οπλισμός θλίψης',
    'Οπλισμός': f'#Φ{comp_diameter}/{comp_spacing_cm}',
    'Τεμάχια': int(compression_rod_number),
    'Μήκος': compression_rod_length,          # m, μήκος κάθε ράβδου
    'Διάκενο': comp_spacing_cm,               # cm
    'Βάρος/τεμ. (kg)': comp_weight_per_piece,
    'Συνολικό βάρος (kg)': comp_weight_per_piece * compression_rod_number
})

#### 2. Οπλισμοί εφελκυσμού πλάκας ####
upl_diameter, upl_spacing_cm = uplift_rod_parser(uplift_selected)
upl_w_kg_per_m = rebar_kg_per_m(upl_diameter)
upl_weight_per_piece = upl_w_kg_per_m * uplift_rod_length

rows.append({
    'Χαρακτηρισμός': 'Πλάκα - οπλισμός εφελκυσμού',
    'Οπλισμός': f'#Φ{upl_diameter}/{upl_spacing_cm}',
    'Τεμάχια': int(uplift_rod_number),
    'Μήκος': uplift_rod_length,
    'Διάκενο': upl_spacing_cm,
    'Βάρος/τεμ. (kg)': upl_weight_per_piece,
    'Συνολικό βάρος (kg)': upl_weight_per_piece * uplift_rod_number
})

#### 3. Διαμήκεις ράβδοι στυλίσκου ####
# Πρώτη διάμετρος
if styliskos_rod_number1 > 0:
    st1_d = styliskos_rod_diameter1
    st1_n = styliskos_rod_number1
    st1_w_kg_per_m = rebar_kg_per_m(st1_d)
    st1_weight_per_piece = st1_w_kg_per_m * styliskos_rod_length

    rows.append({
        'Χαρακτηρισμός': 'Στυλίσκος - διαμήκης οπλισμός',
        'Οπλισμός': f'{int(st1_n)}Φ{st1_d}',
        'Τεμάχια': int(st1_n),
        'Μήκος': styliskos_rod_length,
        'Διάκενο': None,
        'Βάρος/τεμ. (kg)': st1_weight_per_piece,
        'Συνολικό βάρος (kg)': st1_weight_per_piece * st1_n
    })

# Δεύτερη διάμετρος (αν υπάρχει)
if styliskos_rod_number2 > 0:
    st2_d = styliskos_rod_diameter2
    st2_n = styliskos_rod_number2
    st2_w_kg_per_m = rebar_kg_per_m(st2_d)
    st2_weight_per_piece = st2_w_kg_per_m * styliskos_rod_length

    rows.append({
        'Χαρακτηρισμός': 'Στυλίσκος - διαμήκης οπλισμός',
        'Οπλισμός': f'{int(st2_n)}Φ{st2_d}',
        'Τεμάχια': int(st2_n),
        'Μήκος': styliskos_rod_length,
        'Διάκενο': None,
        'Βάρος/τεμ. (kg)': st2_weight_per_piece,
        'Συνολικό βάρος (kg)': st2_weight_per_piece * st2_n
    })

#### 4. Τσέρκια στυλίσκου ####
ts_d = styliskos_tserki_diameter
ts_spacing_cm = styliskos_tserki_spacing
ts_n = int(styliskos_tserki_number)
ts_w_kg_per_m = rebar_kg_per_m(ts_d)
ts_weight_per_piece = ts_w_kg_per_m * styliskos_tserki_length

rows.append({
    'Χαρακτηρισμός': 'Στυλίσκος - τσέρκια',
    'Οπλισμός': f'Φ{ts_d}/{ts_spacing_cm}',
    'Τεμάχια': ts_n,
    'Μήκος': styliskos_tserki_length,
    'Διάκενο': ts_spacing_cm,
    'Βάρος/τεμ. (kg)': ts_weight_per_piece,
    'Συνολικό βάρος (kg)': ts_weight_per_piece * ts_n
})

#### 5. Αποστάτες  ####
apostates_diameter = 20  # mm
ap_n = int(apostates_number)
ap_w_kg_per_m = rebar_kg_per_m(apostates_diameter)
ap_weight_per_piece = ap_w_kg_per_m * apostates_length

rows.append({
    'Χαρακτηρισμός': 'Αποστάτες',
    'Οπλισμός': f'Φ{apostates_diameter}/m2',
    'Τεμάχια': ap_n,
    'Μήκος': apostates_length,
    'Διάκενο': None,
    'Βάρος/τεμ. (kg)': ap_weight_per_piece,
    'Συνολικό βάρος (kg)': ap_weight_per_piece * ap_n
})

#### 6. Πρόσθετοι οπλισμοί εφελκυσμού (αν χρειάζονται) ####

if A>5.0:
        ex_d = extra_rod_diameter
        ex_spacing_cm = extra_rod_spacing * 100.0  # από m σε cm για να είναι συμβατό με τα άλλα
        ex_n = int(extra_rod_number)
        ex_w_kg_per_m = rebar_kg_per_m(ex_d)
        ex_weight_per_piece = ex_w_kg_per_m * extra_rod_length

        rows.append({
        'Χαρακτηρισμός': 'Πλάκα - πρόσθετος οπλισμός εφελκυσμού',
        'Οπλισμός': f'#Φ{int(ex_d)}/{ex_spacing_cm}',
        'Τεμάχια': ex_n,
        'Μήκος': extra_rod_length,
        'Διάκενο': ex_spacing_cm,
        'Βάρος/τεμ. (kg)': ex_weight_per_piece,
        'Συνολικό βάρος (kg)': ex_weight_per_piece * ex_n
        })


#### Build DataFrame ####

columns = ['Χαρακτηρισμός','Οπλισμός','Τεμάχια','Μήκος','Διάκενο',
           'Βάρος/τεμ. (kg)','Συνολικό βάρος (kg)']

df_rods = pd.DataFrame(rows, columns=columns)
df_rods['Βάρος/τεμ. (kg)'] = df_rods['Βάρος/τεμ. (kg)'].round(2)
df_rods['Συνολικό βάρος (kg)'] = df_rods['Συνολικό βάρος (kg)'].round(2)

# Optional: print or export
print(df_rods)
# df_rods.to_excel('oplismoi_podias.xlsx', index=False)


#### run module ####
if __name__ == "__main__":  
        pass