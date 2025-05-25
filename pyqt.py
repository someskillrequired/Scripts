import sys
import os
import shutil
import concurrent.futures
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel, QGridLayout, QTextEdit, QMenuBar, QAction, QFrame, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import subprocess
import change_rules
import pyqtcme
import traceback

current_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
default_game_directory = 'C:/Program Files (x86)/Steam/steamapps/common/They Are Billions'
default_sevenzip_executable = 'C:/Program Files/7-Zip/7z.exe'

rulesfilename = 'ZXRules.dat'
rulespassword = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
campaignfilename = 'ZXCampaign.dat'
campaignpassword = '1688788812-163327433-2005584771'

map_dict = {
    "Hidden Valley":              "R01.dxlevel",
    "The Crossroads":             "R02.dxlevel",
    "The Hunters Meadow":         "R03.dxlevel",
    "The Mines of the Raven":     "R04.dxlevel",
    "The Coast of Bones":         "R05.dxlevel",
    "The Narrow Pass":            "R06.dxlevel",
    "The Lowlands":               "R07.dxlevel",
    "Cape Storm":                 "R08.dxlevel",
    "The Lands of the Giant":     "R09.dxlevel",
    "The Frozen Lake":            "R10.dxlevel",
    "The Lonely Forest":          "R11.dxlevel",
    "The Nest of the Harpy":      "R12.dxlevel",
    "The Valley of Death":        "R13.dxlevel",
    "The Noxious Swamp":          "R14.dxlevel",
    "The Oasis":                  "R15.dxlevel",
    "The Villa of Terror":        "R16.dxlevel",
    "The Resistance":             "R17.dxlevel",
    "The Broken Land":            "R18.dxlevel",
    "El Dorado":                  "R19.dxlevel",
    "The Forbidden Forest":       "R20.dxlevel",
    "The Wasteland of the Giants":"R21.dxlevel",
    "The Highlands":              "R22.dxlevel",
    "The Goddess of Destiny":     "REND.dxlevel"}

class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.moveCursor(QTextCursor.End)
        self.widget.insertPlainText(string)
        self.widget.ensureCursorVisible()

class TAB_GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.game_directory = ''
        self.sevenzip_executable = ''
        self.entry_widgets = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("TAB Mod Tool")
        self.setGeometry(100, 100, 700, 500)
        self.createMenuBar()
        self.createTabs()
        self.load_entries()
        self.createConsole()

    def createMenuBar(self):
        self.menu_bar = QMenuBar(self)
        self.file_menu = self.menu_bar.addMenu("File")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        self.file_menu.addAction(about_action)
        
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_entries)
        self.file_menu.addAction(clear_action)
        
        self.file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)
        
        self.menu_bar.setNativeMenuBar(False)
        self.menu_bar.show()

    def createTabs(self):
        self.layout = QVBoxLayout(self)
        self.layout.setMenuBar(self.menu_bar)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        
        self.tabs.addTab(self.tab1, "Setup")
        self.tabs.addTab(self.tab2, "Campaign Editor")
        self.tabs.addTab(self.tab3, "Campaign World Map Editor")
        
        self.setupTab1()
        self.setupTab2()
        self.setupTab3()
        self.setLayout(self.layout)

    def setupTab1(self):
        layout = QVBoxLayout()
        self.tab1.setLayout(layout)

        file_selector_titles = ['Game Directory', 'Work Directory', 'Data Spread Sheet', '7zip']
        for title in file_selector_titles:
            title_label = QLabel(title, self.tab1)
            layout.addWidget(title_label)

            row_frame = QFrame(self.tab1)
            row_layout = QHBoxLayout(row_frame)

            entry = QLineEdit(self.tab1)
            self.entry_widgets.append(entry)
            row_layout.addWidget(entry)

            if title == "Game Directory" or title == "Work Directory":
                button = QPushButton("Browse", self.tab1)
                button.clicked.connect(self.create_select_directory_handler(entry))
            else:
                button = QPushButton("Browse", self.tab1)
                button.clicked.connect(self.create_select_path_handler(entry))

            row_layout.addWidget(button)
            layout.addWidget(row_frame)

        action_buttons_frame = QFrame(self.tab1)
        action_buttons_layout = QHBoxLayout(action_buttons_frame)
        layout.addWidget(action_buttons_frame)

        button_load_default = QPushButton("Load Default Data", self.tab1)
        button_load_default.clicked.connect(lambda: self.quick_load(False))
        action_buttons_layout.addWidget(button_load_default)

        button_load_modified = QPushButton("Load Modified Data", self.tab1)
        button_load_modified.clicked.connect(lambda: self.quick_load(True))
        action_buttons_layout.addWidget(button_load_modified)

    def create_select_directory_handler(self, entry):
        def handler():
            directory_path = QFileDialog.getExistingDirectory(self, "Select Directory")
            if directory_path:
                entry.setText(directory_path)
        return handler

    def create_select_path_handler(self, entry):
        def handler():
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
            if file_path:
                entry.setText(file_path)
        return handler

    def setupTab2(self):
        layout = QVBoxLayout()
        self.tab2.setLayout(layout)

        self.map_dropdown = QComboBox(self.tab2)
        self.map_dropdown.addItems(map_dict.keys())
        layout.addWidget(self.map_dropdown)

        button = QPushButton("Launch Campaign Map Editor", self.tab2)
        button.clicked.connect(self.launch_cme)
        layout.addWidget(button)
    
    def setupTab3(self):
        layout = QVBoxLayout()
        self.tab3.setLayout(layout)

        button = QPushButton("Launch Campaign Map World Editor", self.tab3)
        button.clicked.connect(self.launch_cmwe)
        layout.addWidget(button)

    def createConsole(self):
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.layout.addWidget(self.console)
        sys.stdout = TextRedirector(self.console)

    def show_about(self):
        QMessageBox.about(self, "About", "TAB Mod Tool\nVersion 1.4\nAuthor: SomeSkillRequired")

    def load_entries(self):
        try:
            with open('entry_values.txt', 'r') as file:
                for entry, line in zip(self.entry_widgets, file):
                    entry.setText(line.strip())
        except FileNotFoundError:
            print("No previous values found.")

        if not self.entry_widgets[0].text():
            self.entry_widgets[0].setText(default_game_directory)

        if not self.entry_widgets[1].text():
            self.entry_widgets[1].setText(current_dir.replace(r"\\", r"/"))

        if not self.entry_widgets[3].text():
            self.entry_widgets[3].setText(default_sevenzip_executable)
        
    def clear_entries(self):
        for entry in self.entry_widgets:
            entry.clear()

    def save_entries(self):
        with open('entry_values.txt', 'w') as file:
            for entry in self.entry_widgets:
                file.write(entry.text() + '\n')

    def closeEvent(self, event):
        self.save_entries()
        event.accept()

    def quick_load(self, mod=False):
        try:
            self.save_entries()
            self.load_data(mod)
            self.save_data()
            self.save_back_to_file()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(exc_type)
            print(exc_value)
            print(exc_traceback)
            print(traceback.print_tb(exc_traceback))

    def load_data(self, mod=False):
        self.game_directory = self.entry_widgets[0].text()
        self.current_directory = self.entry_widgets[1].text()
        self.xls_file_path = self.entry_widgets[2].text()
        self.sevenzip_executable = self.entry_widgets[3].text()

         # ZXRULES DATA
        self.File_Data_ZXRules = change_rules.Data(rulesfilename, rulespassword,self.game_directory,self.current_directory,self.sevenzip_executable)
        self.File_Data_ZXRules.unzip_file_with_7zip()
        self.File_Data_ZXRules.read_file()
        
        self.Entity_Data = change_rules.modify_entities(self.File_Data_ZXRules,self.xls_file_path,mod)
        if self.Entity_Data.valid_sheet:
            self.Entity_Data.read_sheet_to_xml()
            self.Entity_Data.format_xml()
        
        self.globals_Data = change_rules.modify_globals(self.File_Data_ZXRules,self.xls_file_path,mod)
        if self.globals_Data.valid_sheet:
            self.globals_Data.read_sheet_to_xml()
            self.globals_Data.format_xml()
        
        self.Command_Data = change_rules.modify_commands(self.File_Data_ZXRules,self.xls_file_path,mod)
        if self.Command_Data.valid_sheet:
            self.Command_Data.read_sheet_to_xml()
            self.Command_Data.format_xml()
        
        self.MapTheme_Data = change_rules.modify_mapthemes(self.File_Data_ZXRules,self.xls_file_path,mod)
        if self.MapTheme_Data.valid_sheet:
            self.MapTheme_Data.read_sheet_to_xml()
            self.MapTheme_Data.format_xml()
        
        self.map_conditions_Data = change_rules.modify_mapconditions(self.File_Data_ZXRules,self.xls_file_path,mod)
        if self.map_conditions_Data.valid_sheet:
            self.map_conditions_Data.read_sheet_to_xml()
            self.map_conditions_Data.format_xml()

        self.mayor_Data = change_rules.modify_mayor(self.File_Data_ZXRules,self.xls_file_path,mod)
        if self.mayor_Data.valid_sheet:
            self.mayor_Data.read_sheet_to_xml()
            self.mayor_Data.format_xml()
        
        #ZXCAMPAIGN DATA
        self.File_Data_ZXCampaign = change_rules.Data(campaignfilename, campaignpassword,self.game_directory,self.current_directory,self.sevenzip_executable)
        self.File_Data_ZXCampaign.unzip_file_with_7zip()
        self.File_Data_ZXCampaign.read_file()
        
 
        self.Wave_Data = change_rules.modify_waves(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        if self.Wave_Data.valid_sheet:
            self.Wave_Data.read_sheet_to_xml()
            self.Wave_Data.format_xml()    

        
        self.mission_Data = change_rules.modify_missions(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        if self.mission_Data.valid_sheet:
            self.mission_Data.read_sheet_to_xml()
            self.mission_Data.format_xml()
        
       
        self.hero_Data = change_rules.modify_heros(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        if self.hero_Data.valid_sheet:
            self.hero_Data.read_sheet_to_xml()
            self.hero_Data.format_xml()  

       
        self.research_Data = change_rules.modify_research(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        if self.research_Data.valid_sheet:
            self.research_Data.read_sheet_to_xml()
            self.research_Data.format_xml()

        self.researchtree_Data = change_rules.modify_researchtree(self.File_Data_ZXCampaign,self.xls_file_path,mod)
        if self.researchtree_Data.valid_sheet:
            self.researchtree_Data.read_sheet_to_xml()
            self.researchtree_Data.format_xml()    

    def save_data(self):
        if self.Entity_Data.valid_sheet:
            self.Entity_Data.find_start_location()
            self.Entity_Data.find_end_location()
            self.File_Data_ZXRules.original_file_data = self.Entity_Data.replace_and_insert()
        
        if self.Command_Data.valid_sheet:
            self.Command_Data.find_start_location()
            self.Command_Data.find_end_location()
            self.File_Data_ZXRules.original_file_data  = self.Command_Data.replace_and_insert()
        
        if self.globals_Data.valid_sheet:
            self.globals_Data.find_start_location()
            self.globals_Data.find_end_location()
            self.File_Data_ZXRules.original_file_data  = self.globals_Data.replace_and_insert()
        
        if self.MapTheme_Data.valid_sheet:
            self.MapTheme_Data.find_start_location()
            self.MapTheme_Data.find_end_location()
            self.File_Data_ZXRules.original_file_data  = self.MapTheme_Data.replace_and_insert()
        
        if self.map_conditions_Data.valid_sheet:
            self.map_conditions_Data.find_start_location()
            self.map_conditions_Data.find_end_location()
            self.File_Data_ZXRules.original_file_data  = self.map_conditions_Data.replace_and_insert()
        
        if self.mayor_Data.valid_sheet:
            self.mayor_Data.find_start_location()
            self.mayor_Data.find_end_location()
            self.File_Data_ZXRules.original_file_data  = self.mayor_Data.replace_and_insert()
        
        if self.Wave_Data.valid_sheet:
            self.Wave_Data.find_start_location()
            self.Wave_Data.find_end_location()
            self.File_Data_ZXCampaign.original_file_data = self.Wave_Data.replace_and_insert()
        
        if self.mission_Data.valid_sheet:
            self.mission_Data.find_start_location()
            self.mission_Data.find_end_location()
            self.File_Data_ZXCampaign.original_file_data = self.mission_Data.replace_and_insert()
        
        if self.hero_Data.valid_sheet:
            self.hero_Data.find_start_location()
            self.hero_Data.find_end_location()
            self.File_Data_ZXCampaign.original_file_data = self.hero_Data.replace_and_insert()
        
        if self.research_Data.valid_sheet:
            self.research_Data.find_start_location()
            self.research_Data.find_end_location()
            self.File_Data_ZXCampaign.original_file_data = self.research_Data.replace_and_insert()
        
        if self.researchtree_Data.valid_sheet:
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

    def launch_cme(self):
        try:
            self.game_directory = self.entry_widgets[0].text()
            self.current_directory = self.entry_widgets[1].text()
            self.xls_file_path = self.entry_widgets[2].text()
            self.sevenzip_executable = self.entry_widgets[3].text()
            
                
            selected_map_key = self.map_dropdown.currentText()
            r01 = os.path.join(self.game_directory, "ZXGame_Data", "Levels", map_dict[selected_map_key])
            
            launched_map = pyqtcme.Map(self.game_directory, r01, self.sevenzip_executable)
            
            windowclass = pyqtcme.MainWindow(launched_map, self.game_directory, self.sevenzip_executable, )
            windowclass.show()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(exc_type)
            print(exc_value)
            print(exc_traceback)
            print(traceback.print_tb(exc_traceback))

    def launch_cmwe(self):
        try:
            self.game_directory = self.entry_widgets[0].text()
            self.current_directory = self.entry_widgets[1].text()
            self.sevenzip_executable = self.entry_widgets[3].text()
            
            selected_map_key = self.map_dropdown.currentText()
            
            #windowclass = pyqtcme.MainWindow(launched_map, self.game_directory, self.sevenzip_executable, )
            #windowclass.show()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(exc_type)
            print(exc_value)
            print(exc_traceback)
            print(traceback.print_tb(exc_traceback))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = TAB_GUI()
    main_window.show()
    sys.exit(app.exec_())
