import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import json
from typing import List
from copy import deepcopy
from scipy.signal import find_peaks

from folders import * 

def first_analysis_all_tubes():
    # Convert all files in source from tiff to png and saving them in the input file
    for image_path in get_list_images_path(os.path.join(source_folder), ".tiff"):
        image = cv2.imread(os.path.join(image_path), cv2.IMREAD_GRAYSCALE)
        file_name = image_path.split("/")[-1].split(".tiff")[0]  
        input_path = os.path.join(folder, input_folder, file_name + ".png")
        cv2.imwrite(input_path, image)

    tubes_examples = get_tubes_examples()
    
    for image_path in get_list_images_path(os.path.join(folder, input_folder), ".png") :
        print(image_path)
        image = cv2.imread(os.path.join(image_path), cv2.IMREAD_GRAYSCALE)
        coordinates = detect_matches_coordinates(tubes_examples, image)
        borders = find_tube(coordinates)
        tube_image = crop_to_tube(image, borders)
        water = find_water(tube_image)
        save_json(image_path, coordinates, borders, water)
        trace_tube(image_path)
    print("Done !")

def recalculate_water_positions(image_path, x1, x2):
    borders = [x1, x2]
    image = cv2.imread(os.path.join(image_path), cv2.IMREAD_GRAYSCALE)
    tube_image = crop_to_tube(image, borders)
    water = find_water(tube_image)
    return [int(drop) for drop in water]


def get_tubes_examples():
    tubes_examples = []
    for filename in os.listdir(os.path.join(folder, tube_folder)) :
        if filename[-5:] == '.tiff' :
            tubes_examples.append(cv2.imread(os.path.join(folder, tube_folder, filename), cv2.IMREAD_GRAYSCALE))
    return tubes_examples

def get_list_images_path(searched_folder, format = ".tiff"):
    list_images = [os.path.join(searched_folder, image) for image in os.listdir(searched_folder) if image[-len(format):] == format]
    return list_images


def detect_matches_coordinates(tubes_examples:List[np.array], image:np.array, tolerance = 0.75):
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1 = kp1, des1 = sift.detectAndCompute(tubes_examples[0],None)
    for tube in tubes_examples[1:] :
        kp12, des12 = sift.detectAndCompute(tube,None)
        kp1 = kp1 + kp12
        des1 = np.concatenate((des1, des12))

    kp2, des2 = sift.detectAndCompute(image,None)
    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2,k=2)
    # Apply ratio test
    good_matches = []
    for m,n in matches:
        if m.distance < tolerance*n.distance:
            good_matches.append(m)

    coordinates = []
    for match in good_matches :
        idx = match.trainIdx
        keypoint = kp2[idx]
        coordinates.append((int(keypoint.pt[0]), int(keypoint.pt[1])))

    return coordinates

def find_tube(coordinates, min_tube_size:int = 25) -> List[int]:
    list_x = [coordinate[0] for coordinate in coordinates]

    borders = []
    n, bins = np.histogram(list_x, bins = 100)
    while len(borders) < 2 :
        idx_max = np.where(n == max(n))[0][0]
        border = int(bins[idx_max])
        if len(borders) == 0 or abs(borders[-1] - border) > min_tube_size :
            borders.append(border)
        n = np.delete(n, idx_max)

    borders.sort()

    return borders

def crop_to_tube(image, borders):
    x1, x2 = borders
    y1 = 0
    y2 = image.shape[1]
    return image[y1:y2, x1:x2]

def find_threshold(list_prominences, n, epsilon = 5, show = False):
    if show :
        heights, bins, _ = plt.hist(list_prominences, bins = 50)
    else :
        heights, bins = np.histogram(list_prominences, bins = 50)
    i = len(heights) - 1
    sum = 0
    while sum < n :
        sum += heights[i]
        i-=1
    if show :
        plt.plot([bins[i], bins[i]], [0, heights[0]], "--")
        plt.title("Histogramme des prominences")
    #après ce premier traitement bins[i] est une premiere approximation du seuil : on prend ensuite le seuil le plus cohérent dans le voisinage
    chosen_square = i
    for j in range(i-epsilon, i+epsilon+1):
        if j < len(heights) and heights[chosen_square] > heights[j]:
            chosen_square = j
    if show :
        plt.plot([bins[chosen_square], bins[chosen_square]], [0, heights[chosen_square]])
    return bins[chosen_square] * 0.5 + bins[chosen_square + 1] * 0.5

def find_water(tube_image, number_searched = 10, show = False):
    middle = tube_image[:,tube_image.shape[1]//2] #take the middle line
    middle = -1 * middle
    _, data = find_peaks(middle, prominence = (0, None))
    list_prominences = data["prominences"]
    threshold = find_threshold(list_prominences, number_searched)
    peaks, properties = find_peaks(middle, prominence = (threshold, None))
    peaks_to_check = check_peaks_spaces(peaks)
    if len(peaks_to_check) > 0 :
        to_delete = []
        for duo in peaks_to_check :
            duo.sort(key = lambda x : data['prominences'][np.where(peaks == x)])
            to_delete.append(duo[0])
        peaks = np.delete(peaks, to_delete)
    if show :
        f, [ax1, ax2] = plt.subplots(nrows = 1, ncols = 2)
        ax2.plot(middle, [i for i in range(len(middle))])
        ax2.plot(middle[peaks], peaks, "x")
        ax2.hlines(y=peaks, xmin=middle[peaks] - properties["prominences"],
            xmax = middle[peaks], color = "C1")
        ax2.set_ylim(0,len(middle))
        ax2.invert_yaxis()
        ax1.imshow(tube_image)
        plt.show()
    return peaks

def check_peaks_spaces(peaks, minimal_distance= 50):
    distances = [peaks[i + 1] - peaks[i] for i in range(len(peaks) - 1)]
    peaks_to_check = []
    for i, distance in enumerate(distances) :
        if distance < minimal_distance :
            peaks_to_check.append([i, i+1])
    return peaks_to_check

def save_json(image_path:np.array, coordinates:List[cv2.DMatch], borders:List[int], water):
    json_dict = {
        "name":image_path,  
        "valid":False,   
        "ruler":[
            {"x":-1,
            "y":-1},
            {"x":-1,
            "y":-1}],
        "ruler_value":1
    }
    json_dict["tube"] = {"x1":borders[0], "x2":borders[1], "matches":[]}
    # for coordinate in coordinates:
    #     json_dict["tube"]["matches"].append({"x":coordinate[0], "y":coordinate[1]})
    json_dict["water"] = [int(drop) for drop in water]
    file_name = image_path.split("/")[-1].split(".png")[0] #filename
    json_path = os.path.join(folder, json_folder, file_name + ".json")
    with open(json_path, "w+") as f :
        f.write(json.dumps(json_dict, indent=4))


def trace_tube(image_path):
    file_name = image_path.split("/")[-1].split(".png")[0]
    new_image = cv2.imread(os.path.join(folder, input_folder, file_name + ".png"))
    file_name = image_path.split("/")[-1].split(".png")[0]  #filename
    json_path = os.path.join(folder, json_folder, file_name + ".json")
    with open(json_path, "r") as f : 
        json_dict = json.loads(f.read())


    # for coordinate_dict in json_dict["tube"]["matches"] :
    #     new_image = cv2.circle(new_image, (coordinate_dict["x"], coordinate_dict["y"]), radius=5, color=(255, 255, 255), thickness=-1)
    for border in [json_dict["tube"]["x1"], json_dict["tube"]["x2"]] :
        new_image = cv2.line(new_image, (border, 0), (border, new_image.shape[1]), (138, 124, 44), thickness = 3)
    for drop in json_dict["water"] :
         new_image = cv2.line(new_image, (json_dict["tube"]["x1"], drop), (json_dict["tube"]["x2"], drop), (255,0,144), thickness = 3)
    ruler_complete = True
    for ruler_point in json_dict["ruler"]:
        if ruler_point["x"] != -1 and ruler_point["y"] != -1 : 
            new_image = cv2.circle(new_image, (ruler_point["x"], ruler_point["y"]), radius=5, color=(255, 255, 0), thickness=-1)
        else : 
            ruler_complete = False
    if ruler_complete : 
        x1 = json_dict["ruler"][0]["x"]
        y1 = json_dict["ruler"][0]["y"]
        x2 = json_dict["ruler"][1]["x"]
        y2 = json_dict["ruler"][1]["y"]
        new_image = cv2.line(new_image, (x1, y1), (x2, y2), (0,255,0), thickness = 3)

    file_name = image_path.split("/")[-1].split(".png")[0]  #filename
    output_path = os.path.join(folder, output_folder, file_name + ".png")
    cv2.imwrite(output_path, new_image)



if __name__ == "__main__":
    first_analysis_all_tubes()