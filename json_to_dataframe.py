import os
import json

import pandas as pd
from folders import * 
from json_modifications import distance


def create_dataframe():
    df_list = []
    for json_filename in os.listdir(os.path.join(folder, json_folder)):
        if json_filename[-5:] == ".json" :
            json_path = os.path.join(folder, json_folder, json_filename)
            with open(json_path, "r") as f : 
                one_line = get_data_from_name(json_filename)
                json_dict = json.loads(f.read())
                one_line.append(get_water_list(json_dict, one_line[1]))
                df_list.append(one_line)
    df = pd.DataFrame(df_list, columns=['angle', 'Dc', 'Dj', 'Q', 'lambda'])
    return df


def get_data_from_name(json_filename):
    # Two cases, degree or not degree
    parameter_list = json_filename[:-5].split(" ")
    if "°" in json_filename : 
        degree = float(parameter_list[0][:-1])
        cylinder = int(parameter_list[1])
        tip = conversion_tip(parameter_list[2])
        flow = float(parameter_list[4])
    else : 
        degree = 33.5
        cylinder = int(parameter_list[0])
        tip = conversion_tip(parameter_list[1])
        flow = float(parameter_list[2])
    return [degree, cylinder, tip, flow]
    

def get_water_list(json_dict, cylinder):
    #ruler distance in px       # real ruler distance
    #water distance in px       # real water distance

    # real water distance = real ruler distance * water distance in px / ruler distance in px

    x1 = json_dict["ruler"][0]["x"]
    y1 = json_dict["ruler"][0]["y"]
    x2 = json_dict["ruler"][1]["x"]
    y2 = json_dict["ruler"][1]["y"]
    if x1 == -1 or x2 == -1 or y1 == -1 or y2 == -1 : 
        print("tube de merde : ", json_dict["name"])
        ruler_distance_in_px = distance(json_dict["tube"]["x1"], 0, json_dict["tube"]["x2"], 0)
        real_ruler_distance = cylinder / 10
    else : 
        ruler_distance_in_px = distance(x1, y1, x2, y2)
        real_ruler_distance = float(json_dict["ruler_value"])
    water_distance_in_px = sorted(json_dict["water"])
    real_water_distance = [(water - water_distance_in_px[0]) * real_ruler_distance / ruler_distance_in_px for water in water_distance_in_px]
    return real_water_distance
        


def conversion_tip(tip_string):
    """Associe à chaque couleur d'embout son diamètre"""
    tip_diameters = {'18G':0.61, '21G':0.84, '22G':1.2, '18':0.61, '21':0.84, '22':1.2}
    if tip_string in tip_diameters.keys():
        return tip_diameters[tip_string]
    else:
        print('\n Attention : embout inconnu dans le dataframe ! \n')
        return None


if __name__ == "__main__":
    df = create_dataframe()
    print(df)
    df.to_csv("lambdas.csv", sep = ",")