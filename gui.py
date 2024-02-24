import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
import change_rules

global File_Data, Command_Data, MapTheme_Data, Entity_Data, units_dropdown, zombies_dropdown

# Get the directory where the script or executable is located
current_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
default_game_directory = 'C:/Program Files (x86)/Steam/steamapps/common/They Are Billions'
rulesfilename = 'ZXRules.dat'
rulespassword = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
filenameCampaign = 'ZXCampaign.dat' 
campaignpassword = '1688788812-163327433-2005584771'
sevenzip_executable = 'C:/Program Files/7-Zip/7z.exe'

def show_about():
    messagebox.showinfo("About", "TAB MOD\nVersion 1.0\nAuthor SomeSkillRequired")

def select_directory(entry):
    directory_path = filedialog.askdirectory()
    if directory_path:
        entry.delete(0, tk.END)
        entry.insert(0, directory_path)

def set_work_directory(entry):
    current_path = os.path.dirname(os.path.realpath(__file__))
    entry.delete(0, tk.END)
    entry.insert(0, current_path)

def select_path(entry, select="file"):
    if select == "file":
        path = filedialog.askopenfilename()
    else:  # select == "directory"
        path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)  # Remove the current text
        entry.insert(0, path)  # Insert the selected path
        
def save_entries(entries):
    with open('entry_values.txt', 'w') as file:
        for entry in entries:
            file.write(entry.get() + '\n')

def load_entries(entries):
    try:
        with open('entry_values.txt', 'r') as file:
            for entry, line in zip(entries, file):
                entry.delete(0, tk.END)  # Clear current entry text
                entry.insert(0, line.strip())  # Insert loaded value
    except FileNotFoundError:
        print("No previous values found.")

def clear_entries(entries):
    for entry in entries:
        entry.delete(0, tk.END)

def on_closing():
    save_entries(entry_widgets)
    root.destroy()

def load_data():
    global Entity_Data
    # Assuming the existence of the Data class and modify_entities function within change_rules
    File_Data = change_rules.Data(rulesfilename, rulespassword)
    File_Data.unzip_file_with_7zip()
    File_Data.read_zxrules()
    
    Entity_Data = change_rules.modify_entities(File_Data)
    Entity_Data.read_sheet_to_xml()
    Entity_Data.format_xml()

    # Update the dropdown menus with new values
    units_dropdown['values'] = Entity_Data.units
    units_dropdown_att['values'] = Entity_Data.entity_attributes
    zombies_dropdown['values'] = Entity_Data.zombies
    zombies_dropdown_att['values'] = Entity_Data.entity_attributes

def save_data():
    pass
    
def save_back_to_file():
    pass

# Create the main window
root = tk.Tk()
root.title("TAB Mod Tool")
root.geometry("500x300")  # Width x Height

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a File menu and add it to the menu bar
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add items to the File menu
file_menu.add_command(label="About", command=show_about)
file_menu.add_command(label="Clear", command=lambda: clear_entries(entry_widgets))  # Clear menu item
file_menu.add_separator()  # Adds a separator line between menu items
file_menu.add_command(label="Exit", command=root.quit)

# Create the Notebook widget
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')  # Make the notebook expand to fill the window

# Create frames for each tab
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)
tab5 = ttk.Frame(notebook)

# Add tabs to the notebook
notebook.add(tab1, text='Setup')
notebook.add(tab2, text='Survival')
notebook.add(tab3, text='Tab 3')
notebook.add(tab4, text='Tab 4')
notebook.add(tab5, text='Tab 5')

entry_widgets = []  # Initialize the list to track entry widgets

# Titles for each file selector
file_selector_titles = ['Game Directory', 'Work Directory','Data Spread Sheet','7zip']

entry_widgets.clear()

# Modification for creating buttons, ensuring "Work Directory" uses a directory dialog
for i in range(len(file_selector_titles)):
    title_label = ttk.Label(tab1, text=file_selector_titles[i])
    title_label.pack(fill='x', padx=5, pady=(5, 0))

    row_frame = ttk.Frame(tab1)
    row_frame.pack(fill='x', padx=5, pady=(0, 5))

    entry = ttk.Entry(row_frame)
    entry.pack(side=tk.LEFT, expand=True, fill='x', padx=(0, 5))
    entry_widgets.append(entry)

    # Adjust the button command based on the title
    if file_selector_titles[i] == "Game Directory" or file_selector_titles[i] == "Work Directory":
        button_command = lambda e=entry: select_directory(e)  # Use select_directory for directory selection
    else:  
        # For "Data Spread Sheet" or other file selections, use select_path with "file"
        button_command = lambda e=entry: select_path(e, select="file")

    button = ttk.Button(row_frame, text="Browse", command=button_command)
    button.pack(side=tk.RIGHT)

# Create a container frame for the new action buttons
action_buttons_frame = ttk.Frame(tab1)
action_buttons_frame.pack(fill='x', padx=5, pady=10)

dropdown_frame_units = ttk.Frame(tab2)
dropdown_frame_units.pack(fill='x', padx=5, pady=5)

units_var = tk.StringVar()
units_dropdown = ttk.Combobox(dropdown_frame_units, textvariable=units_var, values=[])
units_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
units_dropdown.set('Select a Unit')

units_att_var = tk.StringVar()
units_dropdown_att = ttk.Combobox(dropdown_frame_units, textvariable=units_att_var, values=[])
units_dropdown_att.pack(side=tk.LEFT, padx=5, pady=5)
units_dropdown_att.set('Select an Attribute')

dropdown_frame_zombies = ttk.Frame(tab2)
dropdown_frame_zombies.pack(fill='x', padx=5, pady=5)

zombies_var = tk.StringVar()
zombies_dropdown = ttk.Combobox(dropdown_frame_zombies, textvariable=zombies_var, values=[])
zombies_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
zombies_dropdown.set('Select a Zombie')

zombies_att_var = tk.StringVar()
zombies_dropdown_att = ttk.Combobox(dropdown_frame_zombies, textvariable=zombies_att_var, values=[])
zombies_dropdown_att.pack(side=tk.LEFT, padx=5, pady=5)
zombies_dropdown_att.set('Select an Attribute')

units_dropdown.pack(padx=5, pady=5)
units_dropdown_att.pack(padx=25, pady=5)
zombies_dropdown.pack(padx=5, pady=5)
zombies_dropdown_att.pack(padx=25, pady=5)

# Define button texts and their corresponding functions in a list of tuples
button_actions = [
    ("Load Data", load_data),
    ("Save Data", save_data),
    ("Save Back to File", save_back_to_file)
]

# Create and pack the new action buttons
for text, action in button_actions:
    button = ttk.Button(action_buttons_frame, text=text, command=action)
    button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)

# After defining your entry_widgets
load_entries(entry_widgets)


# Set "Game Directory" to default path if it's empty
if not entry_widgets[0].get():
    entry_widgets[0].insert(0, default_game_directory)
    
if not entry_widgets[1].get():
    entry_widgets[1].insert(0, current_dir.replace(r"\\",r"/"))

if not entry_widgets[3].get():
    entry_widgets[3].insert(3, sevenzip_executable)

root.protocol("WM_DELETE_WINDOW", on_closing)  # Ensure save function is called on closing
    
# Start the Tkinter event loop
root.mainloop()
