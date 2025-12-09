import numpy as np
import pandas as pd

#### basic functions ####

def volume(side, height):               # όγκος (πλευρά, ύψος)
    return side**2 * height             #        = πλευρά^2 * ύψος

def weight(density, volume):            # βάρος (πυκνότητα, όγκος)  
    return density * volume             #       = πυκνότητα * όγκος 

def rebar_kg_per_m(diameter, density=7850):      # βάρος οπλισμού ανά μέτρο (διάμετρος)
    area = (np.pi/4) * (diameter/1000)**2   # εμβαδό διατομής σε m2                  
    return area * density                   # βάρος ανά μέτρο = εμβαδό * πυκνότητα

def pick_label(value, bins, labels):
    """
    Mimic pd.cut(..., right=True) for a single value - no need to pass a Series arg
    """
    bins = np.asarray(bins, dtype=float)
    labels = np.asarray(labels)

    idx = np.searchsorted(bins, value, side='right') - 1
    # clamp just in case
    if idx < 0:
        idx = 0
    elif idx >= len(labels):
        idx = len(labels) - 1
    return labels[idx]

#### read data ####

plaka = pd.read_csv('oplismoi_plakas.csv',header=None)

#f10,space10,diat10,name10,f12,space12,diat12,name12,f14,space14,diat14,name14,f16,space16,diat16,name16,f18,space18,diat18,name18,f20,space20,diat20,name20

bins10 = plaka.iloc[:, 2].values[::-1] 
bins10 = np.concatenate(([0.0],bins10)).astype(float)  
labels10 = plaka.iloc[:, 3].values[::-1] 

bins12 = plaka.iloc[:, 7].values[::-1]
bins12 = np.concatenate(([0.0],bins12)).astype(float)   
labels12 = plaka.iloc[:, 8].values[::-1] 

bins14 = plaka.iloc[:, 12].values[::-1]
bins14 = np.concatenate(([0.0],bins14)).astype(float)
labels14 = plaka.iloc[:, 13].values[::-1] 

bins16 = plaka.iloc[:, 17].values[::-1]
bins16 = np.concatenate(([0.0],bins16)).astype(float)   
labels16 = plaka.iloc[:, 18].values[::-1] 

bins18 = plaka.iloc[:, 22].values[::-1]
bins18 = np.concatenate(([0.0],bins18)).astype(float)
labels18 = plaka.iloc[:, 23].values[::-1]  

bins20 = plaka.iloc[:, 27].values[::-1]
bins20 = np.concatenate(([0.0],bins20)).astype(float)          
labels20 = plaka.iloc[:, 28].values[::-1] 

# stylikos data

styliskos = pd.read_csv('oplismoi_styliskou.csv',header=None)

#name, tem, diat, tem2, diat2, diat3,name2,diat4,name3

bins_st = styliskos.iloc[:, 5].values[::-1]
bins_st = np.concatenate(([0.0],bins_st)).astype(float)

labels_st_main = styliskos.iloc[:, 0].values[::-1]

### ΕΠΙΛΟΓΗ ΟΠΛΙΣΜΟΥ ΘΛΙΨΗΣ ###

def compression_rod_selection(cuttoff_value=18.43):
    selection10 = pick_label(cuttoff_value, bins10, labels10)
    selection12 = pick_label(cuttoff_value, bins12, labels12)
    selection14 = pick_label(cuttoff_value, bins14, labels14)
    selection16 = pick_label(cuttoff_value, bins16, labels16)
    selection18 = pick_label(cuttoff_value, bins18, labels18)
    selection20 = pick_label(cuttoff_value, bins20, labels20)    
    return selection10, selection12, selection14, selection16, selection18, selection20 

def compression_rod_parser(s):
    parts = s.split('/')
    diameter = parts[0].replace('Φ','').replace('#','')
    spacing = parts[1]
    return int(diameter), float(spacing)

### ΕΠΙΛΟΓΗ ΟΠΛΙΣΜΟΥ ΕΦΕΛΚΥΣΜΟΥ ###

def uplift_rod_selection(cuttoff_value=14.39):
    selection10 = pick_label(cuttoff_value, bins10, labels10)
    selection12 = pick_label(cuttoff_value, bins12, labels12)
    selection14 = pick_label(cuttoff_value, bins14, labels14)
    selection16 = pick_label(cuttoff_value, bins16, labels16)
    selection18 = pick_label(cuttoff_value, bins18, labels18)
    selection20 = pick_label(cuttoff_value, bins20, labels20)
    return selection10, selection12, selection14, selection16, selection18, selection20

def uplift_rod_parser(s):
    parts = s.split('/')
    diameter = parts[0].replace('Φ','').replace('#','')
    spacing = parts[1]
    return int(diameter), float(spacing)

### ΕΠΙΛΟΓΗ ΟΠΛΙΣΜΟΥ ΣΤΥΛΙΣΚΟΥ ###

def styliskos_rod_selection(cuttoff_value=19.33):
    selection_main = pick_label(cuttoff_value, bins_st, labels_st_main)
    if cuttoff_value<=10.81:
        selection_aux = "Φ6/15"
    else: selection_aux = "Φ8/20"

    return selection_main, selection_aux

def styliskos_rod_parser(s):
    if "+" in s:
        parts = s.split("+")
        part1 = parts[0].strip().split("Φ")
        number1 = part1[0]
        diameter1 = part1[1]

        part2 = parts[1].strip().split("Φ")
        number2 = part2[0]
        diameter2 = part2[1]
    else:
        part1 = s.strip().split("Φ")
        number1 = part1[0]
        diameter1 = part1[1]
        number2 = 0
        diameter2 = 0
        
    return float(number1), int(diameter1), float(number2), int(diameter2)

def styliskos_tserki_parser(s):
    parts = s.split("/")
    diameter = parts[0].replace('Φ','')
    spacing = parts[1]
    return int(diameter), float(spacing)

#### run module ####
if __name__ == "__main__":
    #print(bins10)
    #print(labels10)
    #print(type(bins10))
    
    #print(uplift_rod_selection())
    #print(compression_rod_selection())
    
    #print(styliskos_rod_selection())

    print(styliskos_rod_parser("8Φ16+4Φ12"))
    print(styliskos_rod_parser("4Φ20")) 

    print(styliskos_tserki_parser("Φ8/20"))

    pass

