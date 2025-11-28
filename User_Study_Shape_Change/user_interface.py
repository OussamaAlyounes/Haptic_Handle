import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def submit_data(k):
    name = name_entry.get()
    # note = note_text.get("1.0", tk.END).strip()
    name = name_entry.get()
    print(name)
    # print(selected_option.get())
    if(selected_option.get()=="q"): print("I print")
    # messagebox.showinfo("You wrote: ", f"name: {name}\n Notes: {note}")
    name_entry.delete(0, tk.END)
    # note_text.delete("1.0", tk.END)
    k+=1
    variable_text.set(f"I changed to {selected_option.get()}")



root = tk.Tk()
root.title("interface test")
root.geometry("720x400")
############################
text_command = tk.Text(root, height=4, width=30)
# importing keyboard letters images
im = Image.open("images/keyboard_key_n.png")
im_r = im.resize((40,40))
image = ImageTk.PhotoImage(im_r)

text_command.insert(tk.END, "I am first")
text_command.image_create(tk.END, image=image)
text_command.insert(tk.END, "I am last")

text_command.place(x=100,y=100)
text_command.config(state=tk.DISABLED)
# text_command.tag_config("hidden", foreground="gray")
#################
variable_text = tk.StringVar(value="I did not change")

# title_label = tk.Label(root, text="MY Title")
title_label = tk.Label(root, textvariable=variable_text)
# title_label.pack()
title_label.grid(row=1,column=1)

name_entry = tk.Entry(root, width=20)
# name_entry.pack()
name_entry.grid(row=2,column=1)

# note_text = tk.Text(root, width= 50, height= 20)
# note_text.pack()
# note_text.grid(row=2, column=3)

submit_button = tk.Button(root, text="Submit", command = lambda: submit_data(5), height=2, width=10)
# submit_button.pack()
submit_button.place(x=720/2, y=400-100)

root.bind("s", lambda event: submit_data(5))

options = ["q","w","e"]
selected_option = tk.StringVar(value=options[0])
option_menu = tk.OptionMenu(root, selected_option, *options)
option_menu.grid()
root.mainloop()
