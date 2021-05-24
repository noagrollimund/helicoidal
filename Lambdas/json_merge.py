from json_modifications import update_json_dict
import os
import json
from folders import * 

json_folder_noa = os.path.join(folder, json_folder)
json_folder_chloe = "web/data/json_chloe"

def is_valid(json_filename, folder):
    json_path = os.path.join(folder, json_filename)
    with open(json_path, "r") as f : 
        json_dict = json.loads(f.read())
    return json_dict["valid"]

for json_filename in os.listdir(json_folder_chloe):
    if json_filename[-5:] == ".json" :
        print(json_filename)
        if is_valid(json_filename, json_folder_chloe) :
            if is_valid(json_filename, json_folder_noa) :
                raise Exception(json_filename + "is valid in both folders")
            else : 
                print("valid by chloe")
                os.remove(os.path.join(json_folder_noa, json_filename))
                os.rename(os.path.join(json_folder_chloe, json_filename), os.path.join(json_folder_noa, json_filename))
        else :
            if is_valid(json_filename, json_folder_noa) :
                print("valid by noa")
            else : 
                raise Exception(json_filename + "is not valid in both folders")