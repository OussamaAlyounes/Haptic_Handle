import numpy as np
import matplotlib.pyplot as plt
import datetime

names = ["Milad", "Giuseppe", "Bernardo", "Luis", "Manish", "MicheleP", "Anjum", "Nico", "Vittoria", "MicheleG", ""]
num = 7
data_min = np.load(f"Data\{names[num]}_min.npz", allow_pickle=True)
data_max = np.load(f"Data\{names[num]}_max.npz", allow_pickle=True)
# for d in data.files:
#     print(d)
#     print(data[d])
sex_min = data_min["sex"]
print(sex_min)
print(data_max["dominant_hand"])
poses_min = data_min['poses_motor']
poses_max = data_max['poses_motor']
steps_min = data_min['steps_distance']
steps_max = data_max['steps_distance']
print(steps_min)
print(poses_min)
# iterations_min = data_min['iterations']
# print(iterations_min)
iterations_max = data_max['iterations']
answers_max = data_max["answers"]
print(answers_max)
answers_min = data_min["answers"]
print(answers_min)

plt.figure()
plt.plot(range(len(steps_max)), poses_max, marker = 'o', color = 'darkgreen')
plt.grid()

# plt.figure()
# plt.plot(range(len(steps_min)), poses_min, marker = 'o')
# plt.grid()

# Labels, title, grid
plt.xlabel("Attempt", fontname="Times New Roman", fontsize=14)
plt.ylabel("Distance (mm)", fontname="Times New Roman", fontsize=14)
# plt.title("Peltier Hysteresis Temperature Control", fontname="Times New Roman", fontsize=16)
plt.grid(True, linestyle="--", alpha=0.6)

plt.ylim(2.5,6.5)
plt.xticks(fontname="Times New Roman", fontsize=12)
plt.yticks(fontname="Times New Roman", fontsize=12)

plt.show()
