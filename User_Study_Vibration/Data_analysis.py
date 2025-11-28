import numpy as np
import matplotlib.pyplot as plt
import glob, os
import seaborn as sns
import pandas as pd
import matplotlib.patches as mpatches
from sklearn.metrics import confusion_matrix

plt.rcParams["font.family"] = "Times New Roman"


def analyze_data(data_names_all):
    cover_labels = ["Fully Closed", "Half Open", "Fully Open"]
    pattern_labels = ["LR", "UD", "CI"]
    age_all = []
    responses_all = np.zeros((3,3,3))
    # confusion matrices variables
    vibration_responses_list = []
    vibration_references_list = []
    covers_references_list = []
    # time_all = np.zeros((3,3,3))
    time_all = []
    time_labels = []
    # print(responses_all)
    for data_name in data_names_all:
        data = np.load(data_name)
        age_all.append(float(data["age"]))
        for i, (response, vibration_ref, cover_pose, time) in enumerate(zip(data["vibration_responses"], 
                                                                            data["vibration_references"], 
                                                                            data["cover_references"], 
                                                                            data["time_responses"])):
            # print(i, response, vibration_ref, cover_pose)
            # print(type(str(response)))
            level = covers.index(cover_pose)
            row = patterns.index(vibration_ref)
            colomn = patterns.index(response)
            responses_all[level, row, colomn] +=1
            time_all.append(time)
            # time_labels.append(f"{level} {row} {colomn}")
            correctness = (row == colomn)
            time_labels.append(f"{level} {row} correct" if correctness else f"{level} {row} incorrect")

            # build the data for confusion matrix
            vibration_responses_list.append(response)
            vibration_references_list.append(vibration_ref)
            covers_references_list.append(cover_pose)

    print("age mean =", np.mean(age_all))
    print("age std =", np.std(age_all))

    responses_sum = responses_all.sum(axis=2)
    responses_all_rate = np.where(responses_sum == 0, 0, responses_all/responses_sum*100)
    time_df = pd.DataFrame({"time_label": time_labels,
                            "Times" : time_all})
    #########################
    # plotting
    #########################

    # plot the confusion matrix
    df_responses = pd.DataFrame({"responses": vibration_responses_list, 
                                 "references": vibration_references_list, 
                                 "covers": covers_references_list})
    fig, axs = plt.subplots(1,3, figsize=(10,4))
    for i, level in enumerate(covers):
        data = df_responses[df_responses["covers"]==level]
        # add the labels =patterns condition sort the data acording to the order we want
        confusion_mat = confusion_matrix(data["references"], data["responses"], normalize="true", labels=patterns)
        print(confusion_mat)
        ax = axs[i]
        map = sns.heatmap(confusion_mat, cmap="Blues", xticklabels= pattern_labels, yticklabels=pattern_labels, 
                          cbar = False, annot=True, square= True, ax=ax, vmin=0, vmax=1, annot_kws={'size': 15})
        ax.set_title(cover_labels[i])
    
    
    # plot success rate and time
    fig, axs = plt.subplots(3,3, figsize = (10,8))
    fig, axs2 = plt.subplots(3,3, figsize = (10,8))

    for i in range(3):
        for j in range(3):
            ax = axs[i,j]
            df = pd.DataFrame({"Patterns":pattern_labels, 
                               "Rate": responses_all_rate[i,j,:]})

            palette = ['seagreen' if color_ind==j else 'indianred' for color_ind in range(len(df))]
            # assigning x variable to hue to remove the warning that is given
            sns.barplot(data=df, x="Patterns", y="Rate", ax=ax, hue="Patterns", palette=palette, legend=False)
            # sns.barplot(data=df, x="Patterns", y="Rate", ax=ax, color=colors)
            ax.set_ylim(top = 100)

            ######################
            # plotting the time boxplot
            ax_time = axs2[i,j]
            # palette = ['chartreuse', 'salmon']
            palette = {f"{i} {j} correct": "seagreen", #chartreuse
                       f"{i} {j} incorrect": "indianred"} #salmon
            # puting the correct ones first and then the incorrect ones
            time_label_plot = time_df[time_df["time_label"].str.startswith(f"{i} {j}")]
            time_label_unique = time_label_plot["time_label"].unique() # it gets the different labels without any repetition
            time_label_sorted = sorted(time_label_unique, key=lambda x: (not x.endswith("correct"), x))
            sns.boxplot(data=time_label_plot, x="time_label", y="Times", 
                        ax=ax_time, showfliers= False, order= time_label_sorted, #showmeans = True, 
                        palette=palette, hue="time_label", legend= False)

            # set the new labels to be only correct or inccorrect without 0 1 correct
            # new_labels = [label.get_text().split()[-1] for label in ax_time.get_xticklabels()]
            # ax_time.set_xticklabels(new_labels)
            
            # remove the x ticks from the axis
            ax_time.set_xticklabels([])
            ax_time.tick_params(axis = "y", labelsize = 12)
            # set the y labels
            if j == 0:
                ax.set_ylabel(cover_labels[i], fontsize = 14)
                ax_time.set_ylabel("Time (sec)", fontsize = 14)
                ax.set_ylabel("Rate (%)", fontsize = 14)
            else:
                ax.set_ylabel("")
                ax_time.set_ylabel("")
            # set the x labels
            if i == 2:
                ax.set_xlabel(f"{pattern_labels[j]} reference", fontsize = 14)
                ax_time.set_xlabel(f"{pattern_labels[j]} reference", fontsize = 14)
            else:
                ax.set_xlabel("")
                ax_time.set_xlabel("")
            
            # add the level to the right subplots
            if j == 2:
                # for the time
                ax_time2 = ax_time.twinx()
                ax_time2.set_ylabel(f"{cover_labels[i]}", fontsize = 14)
                ax_time2.set_yticks([])
                # for the success rate
                ax2 = ax.twinx()
                ax2.set_ylabel(f"{cover_labels[i]}", fontsize = 14)
                ax2.set_yticks([])
            # add a text for the baseline or pattern reference
            # ax.text(0.33, 0.9, f"{pattern_labels[j]} reference", color = "darkgreen", fontsize = 12, transform=ax.transAxes)

    # add a legend for colors for the second figure
    correct_patch = mpatches.Patch(color="seagreen", label="Correct")
    incorrect_patch = mpatches.Patch(color="indianred", label="Incorrect")
    fig.legend(handles=[correct_patch, incorrect_patch], loc='lower center',ncol = 2, bbox_to_anchor=(0.5, 0.02))
            
    plt.show()
    

if __name__ == "__main__":
    patterns = ["lr", "ud", "ci"]
    covers = ["fc", "ho", "fo"]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_names = glob.glob(dir_path+"\\Data\\*.npz")
    # data_names = glob.glob("Data\\Ivan_1752834181.1634548.npz")
    print(data_names)
    # print(os.getcwd())
    analyze_data(data_names)
