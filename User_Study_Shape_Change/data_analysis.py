import numpy as np
import matplotlib.pyplot as plt
import datetime
import glob

import seaborn as snc
import pandas as pd

def get_first_change(array):
    value_prev = None
    for index,value in enumerate(array):
        if value == 'r':
            continue
        if value != 'r' and value_prev!= None and value!=value_prev:
            return index
        value_prev = value    
    return -1

def calculate_jnd(data, start): # calculate the jnd with a reference to the min pose as the origin
    poses = np.array(data["poses_motor"])[start+1:] # poses are in mm
    condition = np.array(data["answers"])[start+1:]
    jnd = np.mean(poses, where=(condition!='r'))
    # print(jnd)
    return jnd

def analyse_data(data_list):
    pose_motor_jnd_list = []
    sucessful_num = 0
    hand_length_list = []
    # age = 0
    for data_name in data_list:
        # print(data_name)
        data = np.load(data_name, allow_pickle=True)
        # data_all.append(data)\
        # for k in data.keys():
        #     print(k)
        if(data['successful']):
            sucessful_num+=1
            # print(type(data["hand_length"]))
            hand_length_list.append(float(data["hand_length"]))
            # print([hand_length_list])
            ind_answer_change = get_first_change(data["poses_motor"]) # starting point of changing the answer
            pose_motor_jnd_list.append(float(calculate_jnd(data, ind_answer_change))) # covert to floar because if not, it is a list of np.float64(num)
    # print(type(pose_motor_jnd_list[0]))
    print(hand_length_list)
    print("hand_length_avg =", np.mean(np.array(hand_length_list)))
    print("hand_length_avg =", np.std(np.array(hand_length_list)))
    return pose_motor_jnd_list

if __name__ == "__main__":
    pose_motor_base = 6 # mm for each side
    circumfrance_min = 125.75 # mm the minimum circumfrance of the device
    circumfrance_base = circumfrance_min + 4*6 # mm the base circumfrance of the device is 6mm added in 4 places
    gear_diameter = 15

    data_name_list_min = glob.glob("Data\*_min.npz")
    data_name_list_max = glob.glob("Data\*_max.npz")
    data_name_list_all = data_name_list_min + data_name_list_max
    # print(data_name_list_all)

    # get list of poses for the data min, max and all
    pose_list_min = analyse_data(data_name_list_min)
    pose_list_max = analyse_data(data_name_list_max)
    pose_list_all = pose_list_min + pose_list_max
    
    # calculate the mean of positions for min, max and all
    pose_distance_min = np.mean(pose_list_min)
    pose_distance_max = np.mean(pose_list_max)
    pose_distance_all = np.mean(pose_list_all)

    # print(pose_distance_min, len(pose_list_min))
    # print(pose_distance_max, len(pose_list_max))
    # print(pose_distance_all, len(pose_list_all))

    # calculate the MP in mm (difference between motor position and the motor base position)
    mp_distance_min = pose_motor_base - pose_distance_min
    mp_distance_max = pose_motor_base - pose_distance_max
    mp_distance_all = pose_motor_base - pose_distance_all
    
    print("MP in mm: ", 2*mp_distance_min, 2*mp_distance_max, 2*mp_distance_all)# show the MP of the whole distance which is cause by two motions

    # calculate the required minimum motor angle (calculate it from the min as origin)
    pose_degree_min = pose_distance_min/(np.pi*gear_diameter)*360
    pose_degree_max = pose_distance_max/(np.pi*gear_diameter)*360
    pose_degree_all = pose_distance_all/(np.pi*gear_diameter)*360
    
    # print(pose_degree_min, pose_degree_max, pose_degree_all)

    # calculate the MP in degrees minimum motor angle (difference between motor position and the motor base position)
    mp_degree_min = mp_distance_min/(np.pi*gear_diameter)*360
    mp_degree_max = mp_distance_max/(np.pi*gear_diameter)*360
    mp_degree_all = mp_distance_all/(np.pi*gear_diameter)*360
    
    print("MP in deg: ", mp_degree_min, mp_degree_max, mp_degree_all)

    # calculate the cicumfrance of the mean motor pose
    circumfrance_min = circumfrance_min + 4*pose_distance_min
    circumfrance_max = circumfrance_min + 4*pose_distance_max
    circumfrance_all = circumfrance_min + 4*pose_distance_all

    # calculate Weber's coefficient from the MP
    weber_coeff_min = (4*mp_distance_min)/circumfrance_base
    weber_coeff_max = (4*mp_distance_max)/circumfrance_base
    weber_coeff_all = (4*mp_distance_all)/circumfrance_base
    
    # calculate the expected MP for the base_min postion depending of weber's coefficient *divide by 4 since the distance is added 4 times for the circumfrance
    mp_distance_min_expected = weber_coeff_min*circumfrance_min/4
    mp_distance_max_expected = weber_coeff_max*circumfrance_min/4
    mp_distance_all_expected = weber_coeff_all*circumfrance_min/4

    # calculate the expected motor position for the base_min postion from the expected MP
    pose_distance_min_expected = mp_distance_min_expected + pose_motor_base
    pose_distance_max_expected = mp_distance_max_expected + pose_motor_base
    pose_distance_all_expected = mp_distance_all_expected + pose_motor_base
    
    print("MP expected in degree: ", pose_distance_min_expected, pose_distance_max_expected, pose_distance_all_expected)

    # calculate the expected motor angle for the base_min
    pose_degree_min_expected = pose_distance_min_expected/(np.pi*gear_diameter)*360
    pose_degree_max_expected = pose_distance_max_expected/(np.pi*gear_diameter)*360
    pose_degree_all_expected = pose_distance_all_expected/(np.pi*gear_diameter)*360

    # print("MP expected in degree: ", pose_degree_min_expected, pose_degree_max_expected, pose_degree_all_expected)

    ##############################
    # plotting the results
    ##############################
    # plot box plot of the mp
    # labels = ["min", "max", "all"]
    # plt.boxplot([pose_list_min, pose_list_max, pose_list_all], tick_labels=labels)
    # plt.show()

    # plot box plot of the mp2base
    mp_distance_list_min = pose_motor_base - np.array(pose_list_min)
    mp_distance_list_max = pose_motor_base - np.array(pose_list_max)
    mp_distance_list_all = pose_motor_base - np.array(pose_list_all)
    
    values = np.concatenate([mp_distance_list_min, mp_distance_list_max, mp_distance_list_all])
    labels = (["min"] * len(mp_distance_list_min) +
              ["max"] * len(mp_distance_list_max) + 
              ["all"] * len(mp_distance_list_all))
    print(len(labels))
    df = pd.DataFrame({"distance": values, "category":labels})
    
    
    palette_colors = ['#ff9999', '#99ff99', '#9999ff']
    snc.boxplot(x = "category", y = "distance", data = df, showmeans = True, palette = palette_colors,
                meanprops={"markerfacecolor":"black", 
                           "markeredgecolor":"black",
                           "markersize":"7"})

    plt.ylabel("Minimum Perception (mm)", fontname='Times New Roman', fontsize=14)
    plt.xlabel(" ", fontsize=14)
    plt.xticks(fontname='Times New Roman', fontsize=14)
    
    # show the MP of the whole distance which is cause by two motions
    # plt.boxplot([2*mp_distance_list_min, 2*mp_distance_list_max, 2*mp_distance_list_all], tick_labels=labels, showmeans=True, patch_artist=True)

    plt.show()


    ######################################
    # distance_detect_mean = pose_motor_base - pose_motor_jnd # difference with the motor base position
    # print("minimum perception distance pose for max = ", distance_detect_mean)
    # circumfrance_detect_mean = circumfrance_min + 4*pose_motor_jnd
    # print("circumfrance_detect_mean = ", circumfrance_detect_mean)
    # weber_coeff = (circumfrance_base - circumfrance_detect_mean)/circumfrance_base
    # print("weber = ", weber_coeff)
    # print("minimum perception distance pose for min = ", (weber_coeff*circumfrance_min)/4)
    # print("minimum_resolution_deg", (weber_coeff*circumfrance_min)/4)

