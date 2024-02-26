import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
import change_rules
import sys

global File_Data, Command_Data, MapTheme_Data, Entity_Data, units_dropdown, zombies_dropdown
global units,units_att,unit_entry,zombies,zombies_att,zombies_entry,units_entry_var,zombies_entry_var

# Get the directory where the script or executable is located
current_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
default_game_directory = 'C:/Program Files (x86)/Steam/steamapps/common/They Are Billions'
rulesfilename = 'ZXRules.dat'
rulespassword = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
filenameCampaign = 'ZXCampaign.dat' 
campaignpassword = '1688788812-163327433-2005584771'
sevenzip_executable = 'C:/Program Files/7-Zip/7z.exe'

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.configure(state='normal')
        self.widget.insert('end', str)
        self.widget.configure(state='disabled')
        self.widget.see('end')

    def flush(self):
        pass

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
    global Entity_Data,units,units_att,unit_entry,zombies,zombies_att,zombies_entry
    # Assuming the existence of the Data class and modify_entities function within change_rules
    File_Data = change_rules.Data(rulesfilename, rulespassword)
    File_Data.unzip_file_with_7zip()
    File_Data.read_zxrules()
    
    Entity_Data = change_rules.modify_entities(File_Data)
    Entity_Data.read_sheet_to_xml()
    Entity_Data.format_xml()

    # Update the dropdown menus with new values
    units['values'] = Entity_Data.units
    units_att['values'] = Entity_Data.entity_attributes
    attribute_dropdown['values'] = Entity_Data.entity_attributes
    
def save_data():
    pass
    
def save_back_to_file():
    pass

def is_valid_number(P):
    # Allow for empty input (to be able to clear the field)
    if P == "":
        return True
    try:
        # Attempt to convert the input to a float
        value = float(P)
        # Check if the input has more than two decimal places
        if P.count('.') == 1 and len(P.split('.')[1]) > 2:
            return False
        return True
    except ValueError:
        # If conversion to float fails, input is not a valid number
        return False

def set_unit_value(Entity_Data,local_attribute,local_unit,local_value):
    Entity_Data.set_attritbute(local_attribute,local_unit,local_value)

def set_zombie_value():
    print("setting zombie value")
    pass

def setup_console():
    message_frame = ttk.Frame(root)  # Create a frame for the message window
    message_frame.pack(side='bottom', fill='x')  # Position frame at the bottom

    message_window = tk.Text(message_frame, height=10, state='disabled', wrap='word')  # Create the text widget
    message_window.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(message_frame, command=message_window.yview)  # Add scrollbar
    scrollbar.pack(side='right', fill='y')
    message_window['yscrollcommand'] = scrollbar.set

    sys.stdout = TextRedirector(message_window)
    
# Create the main window
root = tk.Tk()
root.title("TAB Mod Tool")
root.geometry("700x500")  # Width x Height

setup_console()

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
notebook.add(tab2, text='Unit/Zombie Attributes')
notebook.add(tab3, text='Campaign Waves')
notebook.add(tab4, text='') 
notebook.add(tab5, text='')

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

def tab_1_setup():
    global Entity_Data,units,units_att,unit_entry,zombies,zombies_att,zombies_entry
    
    # Create a container frame for the new action buttons
    action_buttons_frame = ttk.Frame(tab1)
    action_buttons_frame.pack(fill='x', padx=5, pady=10)

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

def tab_2_setup():
    global Entity_Data,units,units_att,unit_entry,zombies,zombies_att,zombies_entry,units_entry_var,zombies_entry_var
    
    unitframeheader = ttk.Frame(tab2)
    unitframeheader.pack(fill='x', padx=5, pady=5)
    attribute_label = ttk.Label(unitframeheader, text="Units")
    attribute_label.pack(side=tk.LEFT)
    tab2unitframe = ttk.Frame(tab2)
    tab2unitframe.pack(fill='x', padx=5, pady=5)
    
    zombieframeheader = ttk.Frame(tab2)
    zombieframeheader.pack(fill='x', padx=5, pady=5)
    attribute_label = ttk.Label(zombieframeheader, text="Zombies")
    attribute_label.pack(side=tk.LEFT)
    tab2zombieframe = ttk.Frame(tab2)
    tab2zombieframe.pack(fill='x', padx=5, pady=5)
    
    units_var         = tk.StringVar()
    units_att_var     = tk.StringVar()
    units_entry_var   = tk.StringVar()
    zombies_var       = tk.StringVar()
    zombies_att_var   = tk.StringVar()
    zombies_entry_var = tk.StringVar()
    
    units= ttk.Combobox(tab2unitframe, textvariable=units_var, values=[])
    units.pack(side="left", padx=5)
    
    units_att = ttk.Combobox(tab2unitframe, textvariable=units_att_var, values=[])
    units_att.pack(side="left", padx=5)
    
    unit_entry = ttk.Entry(tab2unitframe, textvariable=units_entry_var, validate='key', validatecommand=(root.register(is_valid_number), '%P'))
    unit_entry.pack(side="left", padx=5)
    
    unit_button = ttk.Button(tab2unitframe, text="Set Value", command=lambda: set_unit_value(Entity_Data, units_att_var.get(), units_var.get(), units_entry_var.get()))
    unit_button.pack(side=tk.LEFT, padx=10, pady=5,)
    
    zombies = ttk.Combobox(tab2zombieframe, textvariable=zombies_var, values=[])
    zombies.pack(side="left", padx=5, pady=5)
    
    zombies_att = ttk.Combobox(tab2zombieframe, textvariable=zombies_att_var, values=[])
    zombies_att.pack(side="left", padx=5, pady=5)
    
    zombies_entry = ttk.Entry(tab2zombieframe, textvariable=zombies_entry_var, validate='key', validatecommand=(root.register(is_valid_number), '%P'))
    zombies_entry.pack(side="left", padx=5)
    
    zombie_button = ttk.Button(tab2zombieframe, text="Set Value", command=lambda: set_unit_value(Entity_Data, zombies_att_var.get(), zombies_var.get(), zombies_entry_var.get()))
    zombie_button.pack(side=tk.LEFT, padx=10, pady=5)
    
    tab2unitframe.pack(fill='x', padx=5, pady=5)
    tab2zombieframe.pack(fill='x', padx=5, pady=5)
    
    def update_unit_entry(*args):
        local_attribute = units_att_var.get()
        local_unit = units_var.get()
        if local_attribute and local_unit:
            Entity_Data.get_all_locations()
            units_entry_var.set(Entity_Data.get_attribute(str(local_attribute),str(local_unit))) 
        
    units_att_var.trace_add("write", update_unit_entry)
    units_var.trace_add("write", update_unit_entry)
        
    button_actions = [
        ("Load Data", load_data),
        ("Save Data", save_data),
        ("Save Back to File", save_back_to_file)
    ]
    
    # Create and pack the new action buttons
    action_buttons_frame = ttk.Frame(tab2)
    action_buttons_frame.pack(fill='x', padx=5, pady=10)
    for text, action in button_actions:
        button = ttk.Button(action_buttons_frame, text=text, command=action)
        button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)
    
def tab_3_setup():
    global Entity_Data,units_dropdown,units_dropdown_att,attribute_dropdown
    
    attribute_frame = ttk.Frame(tab3)
    attribute_frame.pack(fill='x', padx=5, pady=5)

    # Label for the "Attribute" dropdown
    attribute_label = ttk.Label(attribute_frame, text="Attribute")
    attribute_label.pack(side=tk.LEFT)

    # "Attribute" dropdown
    attribute_var = tk.StringVar()
    attribute_dropdown = ttk.Combobox(attribute_frame, textvariable=attribute_var, values=["Load Data First"])  # Placeholder values
    attribute_dropdown.pack(side=tk.LEFT, padx=5)

    # Frame for the "Scalar" entry
    scalar_frame = ttk.Frame(tab3)
    scalar_frame.pack(fill='x', padx=5, pady=5)

    # Label for the "Scalar" entry
    scalar_label = ttk.Label(scalar_frame, text="Scalar")
    scalar_label.pack(side=tk.LEFT)

    # "Scalar" entry box
    scalar_var = tk.StringVar()
    scalar_entry = ttk.Entry(scalar_frame, textvariable=scalar_var, validate='key', validatecommand=(root.register(is_valid_number), '%P'))
    scalar_entry.pack(side=tk.LEFT, padx=5)
    
# After defining your entry_widgets
tab_1_setup()
tab_2_setup()
tab_3_setup()
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
