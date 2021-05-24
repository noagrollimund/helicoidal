import os
import json
from math import sqrt

from folders import * 
from tube_detection import recalculate_water_positions



def distance(x1, y1, x2, y2):
    return(sqrt((x1 - x2) **2 + (y1 - y2) **2))

def get_json_dict(image_path):
    file_name = image_path.split("/")[-1].split(".png")[0]  #filename
    json_path = os.path.join(folder, json_folder, file_name + ".json")
    with open(json_path, "r") as f : 
        json_dict = json.loads(f.read())
    return json_dict

def update_json_dict(image_path, json_dict):
    file_name = image_path.split("/")[-1].split(".png")[0]  #filename
    json_path = os.path.join(folder, json_folder, file_name + ".json")
    with open(json_path, "w+") as f :
        f.write(json.dumps(json_dict, indent=4))

def add_ruler_point(x, y, image_path):
    json_dict = get_json_dict(image_path)
    x1 = json_dict["ruler"][0]["x"]
    y1 = json_dict["ruler"][0]["y"]
    x2 = json_dict["ruler"][1]["x"]
    y2 = json_dict["ruler"][1]["y"]
    # If there no point in the json, you draw the first one
    if x1 == -1 and y1 == -1 and x2 == -1 and y2 == -1 :
        json_dict["ruler"][0]["x"] = x
        json_dict["ruler"][0]["y"] = y
    # If there's one point already, you draw the second one
    elif x1 != -1 and y1 != -1 and x2 == -1 and y2 == -1 :
        json_dict["ruler"][1]["x"] = x
        json_dict["ruler"][1]["y"] = y
    # if there are already two points, you move the closest
    elif x1 != -1 and y1 != -1 and x2 != -1 and y2 != -1 :
        if distance(x, y, x1, y1) < distance(x, y, x2, y2):
            json_dict["ruler"][0]["x"] = x
            json_dict["ruler"][0]["y"] = y
        else : 
            json_dict["ruler"][1]["x"] = x
            json_dict["ruler"][1]["y"] = y
    update_json_dict(image_path, json_dict)

def delete_ruler_point(x, y, image_path):
    json_dict = get_json_dict(image_path)
    x1 = json_dict["ruler"][0]["x"]
    y1 = json_dict["ruler"][0]["y"]
    x2 = json_dict["ruler"][1]["x"]
    y2 = json_dict["ruler"][1]["y"]
    #If there are two points in the json
    if x1 != -1 and y1 != -1 and x2 != -1 and y2 != -1 :
        # We delete the closest
        if distance(x, y, x1, y1) < distance(x, y, x2, y2):
            json_dict["ruler"][0]["x"] = json_dict["ruler"][1]["x"]
            json_dict["ruler"][0]["y"] = json_dict["ruler"][1]["y"]
            json_dict["ruler"][1]["x"] = -1
            json_dict["ruler"][1]["y"] = -1
        else : 
            json_dict["ruler"][1]["x"] = -1
            json_dict["ruler"][1]["y"] = -1
    # Else we delete the first point (wether it exists or not)
    else : 
        json_dict["ruler"][0]["x"] = -1
        json_dict["ruler"][0]["y"] = -1
    update_json_dict(image_path, json_dict)

def move_tube_side(x, y, image_path):
    json_dict = get_json_dict(image_path)
    x1 = json_dict["tube"]["x1"]
    x2 = json_dict["tube"]["x2"]
    if distance(x, 0, x1, 0) < distance(x, 0, x2, 0):
        json_dict["tube"]["x1"] = x
        x1 = x
    else : 
        json_dict["tube"]["x2"] = x
        x2 = x
    json_dict["water"] = recalculate_water_positions(image_path, x1, x2)
    update_json_dict(image_path, json_dict)

def add_water(x, y, image_path):
    json_dict = get_json_dict(image_path)
    x1 = json_dict["tube"]["x1"]
    x2 = json_dict["tube"]["x2"]
    if x1 < x and x2 > x :
        json_dict["water"].append(y)
    update_json_dict(image_path, json_dict)

def delete_water(x, y, image_path):
    json_dict = get_json_dict(image_path)
    x1 = json_dict["tube"]["x1"]
    x2 = json_dict["tube"]["x2"]
    if x1 < x and x2 > x and len(json_dict["water"]) > 0 :
        best_drop_id = find_closest_drop_id(y, json_dict["water"])
        json_dict["water"].pop(best_drop_id)
    update_json_dict(image_path, json_dict)


def find_closest_drop_id(y, water):
    best_distance = abs(y - water[0])
    best_drop_id = 0
    for i, drop in enumerate(water) :
        if abs(y - drop) < best_distance :
            best_distance = abs(y - drop)
            best_drop_id = i
    return best_drop_id


