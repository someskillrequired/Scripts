import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
import change_rules
import sys

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
        print("wrting")
class TAB_GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TAB Mod Tool")
        self.root.geometry("700x500")  # Width x Height
        self.entry_widgets = []
        self.setup_menu_bar()
        self.setup_widgets()
        self.setup_tabs()
        self.load_entries(self.entry_widgets)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Ensure save function is called on closing
        self.setup_console()
        self.root.mainloop()
        
    def setup_menu_bar(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="About", command=self.show_about)
        self.file_menu.add_command(label="Clear", command=lambda: self.clear_entries(self.entry_widgets))  # Clear menu item
        self.file_menu.add_separator()  # Adds a separator line between menu items
        self.file_menu.add_command(label="Exit", command=self.root.quit)
    
    def setup_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')  # Make the notebook expand to fill the windo   
        
    def setup_tabs(self):
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)
        self.tab5 = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab1, text='Setup')
        self.notebook.add(self.tab2, text='Unit/Zombie Attributes')
        self.notebook.add(self.tab3, text='Campaign Waves')
        self.notebook.add(self.tab4, text='') 
        self.notebook.add(self.tab5, text='')
        
        self.setup_tab_1()
        self.setup_tab_2()
        self.setup_tab_3()

    def setup_tab_1(self):
        self.file_selector_titles = ['Game Directory', 'Work Directory','Data Spread Sheet','7zip']
        # Modification for creating buttons, ensuring "Work Directory" uses a directory dialog
        for i in range(len(self.file_selector_titles)):
            title_label = ttk.Label(self.tab1, text=self.file_selector_titles[i])
            title_label.pack(fill='x', padx=5, pady=(5, 0))

            row_frame = ttk.Frame(self.tab1)
            row_frame.pack(fill='x', padx=5, pady=(0, 5))

            entry = ttk.Entry(row_frame)
            entry.pack(side=tk.LEFT, expand=True, fill='x', padx=(0, 5))
            self.entry_widgets.append(entry)

            # Adjust the button command based on the title
            if self.file_selector_titles[i] == "Game Directory" or self.file_selector_titles[i] == "Work Directory":
                button_command = lambda e=entry: select_directory(e)  # Use select_directory for directory selection
            else:  
                # For "Data Spread Sheet" or other file selections, use select_path with "file"
                button_command = lambda e=entry: select_path(e, select="file")

            button = ttk.Button(row_frame, text="Browse", command=button_command)
            button.pack(side=tk.RIGHT)
            
        # Create a container frame for the new action buttons
        action_buttons_frame = ttk.Frame(self.tab1)
        action_buttons_frame.pack(fill='x', padx=5, pady=10)

        # Define button texts and their corresponding functions in a list of tuples
        button_actions = [
            ("Load Data", self.load_data),
            ("Save Data", self.save_data),
            ("Save Back to File", self.save_back_to_file)
        ]

        # Create and pack the new action buttons
        for text, action in button_actions:
            button = ttk.Button(action_buttons_frame, text=text, command=action)
            button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)

    def setup_tab_2(self):
        unitframeheader = ttk.Frame(self.tab2)
        unitframeheader.pack(fill='x', padx=5, pady=5)
        attribute_label = ttk.Label(unitframeheader, text="Units")
        attribute_label.pack(side=tk.LEFT)
        tab2unitframe = ttk.Frame(self.tab2)
        tab2unitframe.pack(fill='x', padx=5, pady=5)
        
        zombieframeheader = ttk.Frame(self.tab2)
        zombieframeheader.pack(fill='x', padx=5, pady=5)
        attribute_label = ttk.Label(zombieframeheader, text="Zombies")
        attribute_label.pack(side=tk.LEFT)
        tab2zombieframe = ttk.Frame(self.tab2)
        tab2zombieframe.pack(fill='x', padx=5, pady=5)
        
        units_var         = tk.StringVar()
        units_att_var     = tk.StringVar()
        units_entry_var   = tk.StringVar()
        zombies_var       = tk.StringVar()
        zombies_att_var   = tk.StringVar()
        zombies_entry_var = tk.StringVar()
        
        self.units= ttk.Combobox(tab2unitframe, textvariable=units_var, values=[])
        self.units.pack(side="left", padx=5)
        
        self.units_att = ttk.Combobox(tab2unitframe, textvariable=units_att_var, values=[])
        self.units_att.pack(side="left", padx=5)
        
        self.unit_entry = ttk.Entry(tab2unitframe, textvariable=units_entry_var, validate='key', validatecommand=(self.root.register(self.is_valid_number), '%P'))
        self.unit_entry.pack(side="left", padx=5)
        
        self.unit_button = ttk.Button(tab2unitframe, text="Set Value", command=lambda: self.set_unit_value(self.Entity_Data, units_att_var.get(), units_var.get(), units_entry_var.get()))
        self.unit_button.pack(side=tk.LEFT, padx=10, pady=5,)
        
        self.zombies = ttk.Combobox(tab2zombieframe, textvariable=zombies_var, values=[])
        self.zombies.pack(side="left", padx=5, pady=5)
        
        self.zombies_att = ttk.Combobox(tab2zombieframe, textvariable=zombies_att_var, values=[])
        self.zombies_att.pack(side="left", padx=5, pady=5)
        
        self.zombies_entry = ttk.Entry(tab2zombieframe, textvariable=zombies_entry_var, validate='key', validatecommand=(self.root.register(self.is_valid_number), '%P'))
        self.zombies_entry.pack(side="left", padx=5)
        
        self.zombie_button = ttk.Button(tab2zombieframe, text="Set Value", command=lambda: self.set_unit_value(self.Entity_Data, zombies_att_var.get(), zombies_var.get(), zombies_entry_var.get()))
        self.zombie_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        tab2unitframe.pack(fill='x', padx=5, pady=5)
        tab2zombieframe.pack(fill='x', padx=5, pady=5)
        
        def update_unit_entry(*args):
            local_attribute = units_att_var.get()
            local_unit = units_var.get()
            if local_attribute and local_unit:
                self.Entity_Data.get_all_locations()
                units_entry_var.set(self.Entity_Data.get_attribute(str(local_attribute),str(local_unit))) 
            
        units_att_var.trace_add("write", update_unit_entry)
        units_var.trace_add("write", update_unit_entry)
            
        button_actions = [
            ("Load Data", self.load_data),
            ("Save Data", self.save_data),
            ("Save Back to File", self.save_back_to_file)
        ]
        
        # Create and pack the new action buttons
        action_buttons_frame = ttk.Frame(self.tab2)
        action_buttons_frame.pack(fill='x', padx=5, pady=10)
        for text, action in button_actions:
            button = ttk.Button(action_buttons_frame, text=text, command=action)
            button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)
        
    def setup_tab_3(self):
        attribute_frame = ttk.Frame(self.tab3)
        attribute_frame.pack(fill='x', padx=5, pady=5)

        # Label for the "Attribute" dropdown
        attribute_label = ttk.Label(attribute_frame, text="Attribute")
        attribute_label.pack(side=tk.LEFT)

        # "Attribute" dropdown
        attribute_var = tk.StringVar()
        self.attribute_dropdown = ttk.Combobox(attribute_frame, textvariable=attribute_var, values=["Load Data First"])  # Placeholder values
        self.attribute_dropdown.pack(side=tk.LEFT, padx=5)

        # Frame for the "Scalar" entry
        self.scalar_frame = ttk.Frame(self.tab3)
        self.scalar_frame.pack(fill='x', padx=5, pady=5)

        # Label for the "Scalar" entry
        scalar_label = ttk.Label(self.scalar_frame, text="Scalar")
        scalar_label.pack(side=tk.LEFT)

        # "Scalar" entry box
        scalar_var = tk.StringVar()
        self.scalar_entry = ttk.Entry(self.scalar_frame, textvariable=scalar_var, validate='key', validatecommand=(self.root.register(self.is_valid_number), '%P'))
        self.scalar_entry.pack(side=tk.LEFT, padx=5)
    
    def show_about(self):
        messagebox.showinfo("About", "TAB MOD\nVersion 1.0\nAuthor SomeSkillRequired")

    def select_directory(self,entry):
        directory_path = filedialog.askdirectory()
        if directory_path:
            entry.delete(0, tk.END)
            entry.insert(0, directory_path)

    def set_work_directory(self,entry):
        current_path = os.path.dirname(os.path.realpath(__file__))
        entry.delete(0, tk.END)
        entry.insert(0, current_path)

    def select_path(self,entry, select="file"):
        if select == "file":
            path = filedialog.askopenfilename()
        else:  # select == "directory"
            path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)  # Remove the current text
            entry.insert(0, path)  # Insert the selected path
            
    def save_entries(self,entries):
        with open('entry_values.txt', 'w') as file:
            for entry in entries:
                file.write(entry.get() + '\n')

    def load_entries(self,entries):
        try:
            with open('entry_values.txt', 'r') as file:
                for entry, line in zip(entries, file):
                    entry.delete(0, tk.END)  # Clear current entry text
                    entry.insert(0, line.strip())  # Insert loaded value
        except FileNotFoundError:
            print("No previous values found.")
            
        if not self.entry_widgets[0].get():
            self.entry_widgets[0].insert(0, default_game_directory)
            
        if not self.entry_widgets[1].get():
            self.entry_widgets[1].insert(0, current_dir.replace(r"\\",r"/"))

        if not self.entry_widgets[3].get():
            self.entry_widgets[3].insert(3, sevenzip_executable)

    def clear_entries(self,entries):
        for entry in entries:
            entry.delete(0, tk.END)

    def on_closing(self):
        self.save_entries(self.entry_widgets)
        self.root.destroy()

    def load_data(self):
        # Assuming the existence of the Data class and modify_entities function within change_rules
        File_Data = change_rules.Data(rulesfilename, rulespassword)
        File_Data.unzip_file_with_7zip()
        File_Data.read_zxrules()
        
        self.Entity_Data = change_rules.modify_entities(File_Data)
        self.Entity_Data.read_sheet_to_xml()
        self.Entity_Data.format_xml()

        # Update the dropdown menus with new values
        self.units['values'] = self.Entity_Data.units
        self.units_att['values'] = self.Entity_Data.entity_attributes
        self.attribute_dropdown['values'] = self.Entity_Data.entity_attributes
    
    def save_data(self):
        pass
        
    def save_back_to_file(self):
        pass

    def is_valid_number(self,P):
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

    def set_unit_value(self,Entity_Data,local_attribute,local_unit,local_value):
        Entity_Data.set_attritbute(local_attribute,local_unit,local_value)

    def set_zombie_value(self):
        print("setting zombie value")
        pass

    def setup_console(self):
        message_frame = ttk.Frame(self.root)  # Create a frame for the message window
        message_frame.pack(side='bottom', fill='x')  # Position frame at the bottom

        message_window = tk.Text(message_frame, height=10, state='disabled', wrap='word')  # Create the text widget
        message_window.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(message_frame, command=message_window.yview)  # Add scrollbar
        scrollbar.pack(side='right', fill='y')
        message_window['yscrollcommand'] = scrollbar.set

        sys.stdout = TextRedirector(message_window)
    
TAB_UI = TAB_GUI()