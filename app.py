from re import I
import eel
import json
import os
import cv2
from tube_detection import trace_tube
from json_modifications import add_ruler_point, delete_ruler_point, move_tube_side, add_water, delete_water, get_json_dict, update_json_dict
from folders import * 

def is_valid(image_path):
    image_path = os.path.join(folder, input_folder, image_path)
    json_dict = get_json_dict(image_path)
    return json_dict["valid"]

eel.init('web', allowed_extensions=['.js', '.html'])

@eel.expose
def deal_with_click(percentage_x, percentage_y, mode, image_path):
    image_path = os.path.join("web", image_path)
    new_image = cv2.imread(image_path)
    x = int(percentage_x * new_image.shape[0])
    y = int(percentage_y * new_image.shape[1])
    if mode == "add_ruler_point":
        add_ruler_point(x, y, image_path)
    elif mode == "delete_ruler_point" :
        delete_ruler_point(x, y, image_path)
    elif mode == "move_tube_side" :
        move_tube_side(x, y, image_path)
    elif mode == "add_water" :
        add_water(x, y, image_path)
    elif mode == "delete_water" :
        delete_water(x, y, image_path)
    trace_tube(image_path)

@eel.expose
def get_list_image_path(valid):
    if valid in ["true", "false"]:
        valid = valid == "true"
    else : 
        raise Exception
    list_images_paths = os.listdir(os.path.join(folder, input_folder))
    result = []
    for image_path in list_images_paths:
        if image_path[-4:] == ".png" and is_valid(image_path) == valid : 
            result.append(os.path.join("data", output_folder, image_path))
    return result

@eel.expose
def change_image_validity(image_path, valid):
    if valid in ["true", "false"]:
        valid = valid == "true"
    else : 
        raise Exception
    image_path = os.path.join(folder, input_folder, image_path)
    json_dict = get_json_dict(image_path)
    json_dict["valid"] = valid
    update_json_dict(image_path, json_dict)

@eel.expose
def get_image_validity(image_path):
    image_path = os.path.join(folder, input_folder, image_path)
    json_dict = get_json_dict(image_path)
    valid = json_dict["valid"]
    if valid :
        return "true"
    else :
        return "false"


@eel.expose
def change_ruler_value(image_path, ruler_value):
    image_path = os.path.join(folder, input_folder, image_path)
    json_dict = get_json_dict(image_path)
    json_dict["ruler_value"] = ruler_value
    update_json_dict(image_path, json_dict)

@eel.expose
def get_ruler_value(image_path):
    image_path = os.path.join(folder, input_folder, image_path)
    json_dict = get_json_dict(image_path)
    return json_dict["ruler_value"]


eel.start('index.html')