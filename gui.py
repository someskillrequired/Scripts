import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from multiprocessing import Process
import CampaignMapEditorTesting as cme
import concurrent.futures
import os
import change_rules
import sys
import subprocess
from pathlib import Path
import shutil

# Get the directory where the script or executable is located
current_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
default_game_directory = 'C:/Program Files (x86)/Steam/steamapps/common/They Are Billions'

rulesfilename = 'ZXRules.dat'
rulespassword = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
campaignfilename = 'ZXCampaign.dat' 
campaignpassword = '1688788812-163327433-2005584771'
default_sevenzip_executable = 'C:/Program Files/7-Zip/7z.exe'

def run_cme_process(map_path, game_directory, sevenzip_executable):
    cme.launch_from_gui(map_path, game_directory, sevenzip_executable)

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.configure(state='normal')
        self.widget.insert('end', str)
        self.widget.configure(state='disabled')
        self.widget.see('end') 
        
class TAB_GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.game_directory = ''
        self.sevenzip_executable =  ''
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
        #self.notebook.add(self.tab2, text='Unit/Zombie Attributes')
        self.notebook.add(self.tab3, text='Campaign Editor')
        #self.notebook.add(self.tab4, text='') 
        #self.notebook.add(self.tab5, text='')
        
        self.setup_tab_1()
        #self.setup_tab_2()
        self.setup_tab_3()

    def launch_cme(self):
        Ro1          = "R01.dxlevel"
        dir_names = [
                     "clean",
                     "custom_maps_unzipped_with_changes",
                     "custom_maps_unzipped_no_changes",
                     "custom_maps"
                     ]
        
        game_directory = self.entry_widgets[0].get()
        
        first_setup = False
        map_path = game_directory + r"/ZXGame_Data/Levels/"
        for dir_name in dir_names:
            dir_path = Path(map_path,dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                if dir_name == "clean":
                    first_setup = True
        if first_setup:
            #extract standard maps to the clean folder
            
            for root,dirs, files in os.walk(map_path):
                for file in files:
                    # Check if the file ends with .dxlevel
                    if file.endswith(".dxlevel"):
                        file_path = Path(root, file)
                        shutil.copy2(file_path, Path(map_path,"clean"))
                        
            return "Operation completed."
        
        sevenzip_executable = self.entry_widgets[3].get()
        # game_thread = Process(target=run_cme_process, args=(os.path.join(map_path, Ro1), game_directory, sevenzip_executable))
        # game_thread.start()
        #cme.launch_from_gui(os.path.join(map_path + Ro1),game_directory,sevenzip_executable)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            future = executor.submit(run_cme_process, os.path.join(map_path, Ro1), game_directory, sevenzip_executable)
    
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
                button_command = lambda e=entry: self.select_directory(e)  # Use select_directory for directory selection
            else:  
                # For "Data Spread Sheet" or other file selections, use select_path with "file"
                button_command = lambda e=entry: self.select_path(e, select="file")

            button = ttk.Button(row_frame, text="Browse", command=button_command)
            button.pack(side=tk.RIGHT)
            
        # Create a container frame for the new action buttons
        action_buttons_frame = ttk.Frame(self.tab1)
        action_buttons_frame.pack(fill='x', padx=5, pady=10)

        #Define button texts and their corresponding functions in a list of tuples
        button_actions = [
            
            ("Load Default Data", self.quick_load),
            ("Load Modified Data", self.quick_load),
            #("Save Data", self.save_data),
            #("Save Back to File", self.save_back_to_file)
        ]
        
        # Create and pack the new action buttons
        action_buttons_frame = ttk.Frame(self.tab1)
        action_buttons_frame.pack(fill='x', padx=5, pady=10)
        for text, action in button_actions:
            print(text,action)
            if text == "Load Modified Data":
                button = ttk.Button(action_buttons_frame, text=text, command=lambda:self.quick_load(True))
            else:
                button = ttk.Button(action_buttons_frame, text=text, command=lambda:self.quick_load(False))
            button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)

    def setup_tab_2(self):
        def update_unit_entry(*args):
            local_attribute = units_att_var.get()
            local_unit = units_var.get()
            if local_attribute and local_unit:
                self.Entity_Data.get_all_locations()
                units_entry_var.set(self.Entity_Data.get_attribute(str(local_attribute),str(local_unit))) 
        
        def update_zombies_entry(*args):
            local_attribute = zombies_att_var.get()
            local_zombie = zombies_var.get()
            if local_attribute and local_zombie:
                self.Entity_Data.get_all_locations()
                zombies_entry_var.set(self.Entity_Data.get_attribute(str(local_attribute),str(local_zombie))) 
        
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
        
        # def set_unit_entry(*args):
        #     local_attribute = units_att_var.get()
        #     local_unit = units_var.get()
        #     if local_attribute and local_unit:
        #         self.Entity_Data.get_all_locations()
                
        # def set_zombies_entry(*args):
        #     local_attribute = zombies_att_var.get()
        #     local_zombies = zombies_var.get()
        #     if local_attribute and local_zombies:
        #         self.Entity_Data.get_all_locations()        
            
        units_att_var.trace_add("write", update_unit_entry)
        units_var.trace_add("write", update_unit_entry)
        
        zombies_att_var.trace_add("write", update_zombies_entry)
        zombies_var.trace_add("write", update_zombies_entry)
            
        button_actions = [
            
            ("Load Default Data", self.load_data),
            ("Load Modified Data", self.load_data),
            ("Save Data", self.save_data),
            ("Save Back to File", self.save_back_to_file)
        ]
        
        # Create and pack the new action buttons
        action_buttons_frame = ttk.Frame(self.tab2)
        action_buttons_frame.pack(fill='x', padx=5, pady=10)
        for text, action in button_actions:
            print(text,action)
            if text == "Load Modified Data":
                button = ttk.Button(action_buttons_frame, text=text, command=lambda:self.load_data(True))
            else:
                button = ttk.Button(action_buttons_frame, text=text, command=action)
            button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)
        
    def setup_tab_3(self):
        attribute_frame = ttk.Frame(self.tab3)
        attribute_frame.pack(fill='x', padx=5, pady=5)

        # # Label for the "Attribute" dropdown
        # attribute_label = ttk.Label(attribute_frame, text="Attribute")
        # attribute_label.pack(side=tk.LEFT)

        # # "Attribute" dropdown
        # attribute_var = tk.StringVar()
        # self.attribute_dropdown = ttk.Combobox(attribute_frame, textvariable=attribute_var, values=["Load Data First"])  # Placeholder values
        # self.attribute_dropdown.pack(side=tk.LEFT, padx=5)

        # # Frame for the "Scalar" entry
        # self.scalar_frame = ttk.Frame(self.tab3)
        # self.scalar_frame.pack(fill='x', padx=5, pady=5)

        # # Label for the "Scalar" entry
        # scalar_label = ttk.Label(self.scalar_frame, text="Scalar")
        # scalar_label.pack(side=tk.LEFT)

        # # "Scalar" entry box
        # scalar_var = tk.StringVar()
        # self.scalar_entry = ttk.Entry(self.scalar_frame, textvariable=scalar_var, validate='key', validatecommand=(self.root.register(self.is_valid_number), '%P'))
        # self.scalar_entry.pack(side=tk.LEFT, padx=5)
        
        # Create and pack the new action buttons
        action_buttons_frame = ttk.Frame(self.tab3)
        action_buttons_frame.pack(fill='x', padx=5, pady=10)
        button = ttk.Button(action_buttons_frame, text="Launch Campaign Map Editor", command= self.launch_cme)
        button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)
    
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
            self.entry_widgets[3].insert(3, default_sevenzip_executable)

    def clear_entries(self,entries):
        for entry in entries:
            entry.delete(0, tk.END)

    def on_closing(self):
        self.save_entries(self.entry_widgets)
        self.root.destroy()

    def quick_load(self, mod = False):
        self.load_data(mod)
        self.save_data()
        self.save_back_to_file()
   
    def load_data(self,mod = False):
        # Assuming the existence of the Data class and modify_entities function within change_rules
        self.game_directory = self.entry_widgets[0].get()
        self.current_directory = self.entry_widgets[1].get()
        self.xls_file_path = self.entry_widgets[2].get()
        self.sevenzip_executable = self.entry_widgets[3].get()
        
        # ZXRULES DATA
        self.File_Data_ZXRules = change_rules.Data(rulesfilename, rulespassword,self.game_directory,self.current_directory,self.sevenzip_executable)
        self.File_Data_ZXRules.unzip_file_with_7zip()
        self.File_Data_ZXRules.read_file()
        
        self.Entity_Data = change_rules.modify_entities(self.File_Data_ZXRules,self.xls_file_path,mod)
        self.Entity_Data.read_sheet_to_xml()
        self.Entity_Data.format_xml()
        
        self.globals_Data = change_rules.modify_globals(self.File_Data_ZXRules,self.xls_file_path,mod)
        self.globals_Data.read_sheet_to_xml()
        self.globals_Data.format_xml()
        
        self.Command_Data = change_rules.modify_commands(self.File_Data_ZXRules,self.xls_file_path,mod)
        self.Command_Data.read_sheet_to_xml()
        self.Command_Data.format_xml()
        
        self.MapTheme_Data = change_rules.modify_mapthemes(self.File_Data_ZXRules,self.xls_file_path,mod)
        self.MapTheme_Data.read_sheet_to_xml()
        self.MapTheme_Data.format_xml()
        
        self.mayor_Data = change_rules.modify_mayor(self.File_Data_ZXRules,self.xls_file_path,mod)
        self.mayor_Data.read_sheet_to_xml()
        self.mayor_Data.format_xml()
        
        #ZXCAMPAIGN DATA
        self.File_Data_ZXCampaign = change_rules.Data(campaignfilename, campaignpassword,self.game_directory,self.current_directory,self.sevenzip_executable)
        self.File_Data_ZXCampaign.unzip_file_with_7zip()
        self.File_Data_ZXCampaign.read_file()
        
        self.Wave_Data = change_rules.modify_waves(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        self.Wave_Data.read_sheet_to_xml()
        self.Wave_Data.format_xml()    

        self.mission_Data = change_rules.modify_missions(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        self.mission_Data.read_sheet_to_xml()
        self.mission_Data.format_xml()
        
        self.hero_Data = change_rules.modify_heros(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        self.hero_Data.read_sheet_to_xml()
        self.hero_Data.format_xml()  

        self.research_Data = change_rules.modify_research(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        self.research_Data.read_sheet_to_xml()
        self.research_Data.format_xml()

        self.researchtree_Data = change_rules.modify_researchtree(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        self.researchtree_Data.read_sheet_to_xml()
        self.researchtree_Data.format_xml()    
        
        # Update the dropdown menus with new values
        # self.units['values'] = self.Entity_Data.units
        # self.units_att['values'] = self.Entity_Data.entity_attributes
        # self.attribute_dropdown['values'] = self.Entity_Data.entity_attributes
        
        # self.zombies['values'] = self.Entity_Data.zombies
        # self.zombies_att['values'] = self.Entity_Data.entity_attributes
        # self.attribute_dropdown['values'] = self.Entity_Data.entity_attributes
        
    def save_data(self):
        self.Entity_Data.find_start_location()
        self.Entity_Data.find_end_location()
        self.File_Data_ZXRules.original_file_data = self.Entity_Data.replace_and_insert()
        
        self.Command_Data.find_start_location()
        self.Command_Data.find_end_location()
        self.File_Data_ZXRules.original_file_data  = self.Command_Data.replace_and_insert()
        
        self.globals_Data.find_start_location()
        self.globals_Data.find_end_location()
        self.File_Data_ZXRules.original_file_data  = self.globals_Data.replace_and_insert()
        
        self.MapTheme_Data.find_start_location()
        self.MapTheme_Data.find_end_location()
        self.File_Data_ZXRules.original_file_data  = self.MapTheme_Data.replace_and_insert()
        
        self.mayor_Data.find_start_location()
        self.mayor_Data.find_end_location()
        self.File_Data_ZXRules.original_file_data  = self.mayor_Data.replace_and_insert()
        
        self.Wave_Data.find_start_location()
        self.Wave_Data.find_end_location()
        self.File_Data_ZXCampaign.original_file_data = self.Wave_Data.replace_and_insert()
        
        self.mission_Data.find_start_location()
        self.mission_Data.find_end_location()
        self.File_Data_ZXCampaign.original_file_data = self.mission_Data.replace_and_insert()
        
        self.hero_Data.find_start_location()
        self.hero_Data.find_end_location()
        self.File_Data_ZXCampaign.original_file_data = self.hero_Data.replace_and_insert()
        
        self.research_Data.find_start_location()
        self.research_Data.find_end_location()
        self.File_Data_ZXCampaign.original_file_data = self.research_Data.replace_and_insert()
        
        self.researchtree_Data.find_start_location()
        self.researchtree_Data.find_end_location()
        self.File_Data_ZXCampaign.original_file_data = self.researchtree_Data.replace_and_insert()
        print("Data Saved")
        
    def save_back_to_file(self):
        self.File_Data_ZXRules.write_file()
        self.File_Data_ZXRules.zip_files_with_7zip()
        self.File_Data_ZXRules.move_file()
        
        self.File_Data_ZXCampaign.write_file()
        self.File_Data_ZXCampaign.zip_files_with_7zip()
        self.File_Data_ZXCampaign.move_file()
        
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




if __name__ == '__main__':    
    TAB_UI = TAB_GUI()