password = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
import csv
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import subprocess
import os
import zipfile
import shutil
import copy
import base64
import pandas as pd

global working_directory, filename, game_directory, xls_file_path

working_directory = 'C:/Users/Josh/Desktop/MODS/Scripts/'
xls_file_path = 'C:/Users/Josh/Downloads/Rebalanced Mod.xlsx'
game_directory = 'D:/SteamLibrary/steamapps/common/They Are Billions'
filename = 'ZXRules.dat'

class Data():
    # Class sheet handles parsing and holding of original data as well as any modifications to it
    def __init__(self):
        self.password = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
        
        self.original_file      = f'{working_directory}data/original/{filename}'
        self.unzipped_file_path = f'{working_directory}data/unzipped/'
        self.unzipped_file      = f'{working_directory}data/unzipped/{filename}'
        self.modded_file_path   = f'{working_directory}data/modded/{filename}'
        self.zipped_file_path   = f'{working_directory}data/rezipped/{filename}'
        self.game_directory     = game_directory

        self.original_file_data      = []
        
    def unzip_file_with_7zip(self):
        sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'  # Adjust the path based on your installation
        try:
            command = [
                sevenzip_executable,
                'x',  # Extract files with full paths
                '-y',  # Assume Yes on all queries (overwrite files without prompting)
                f'-p{self.password}',  # Password for the archive
                f'-o{self.unzipped_file_path}',  # Output directory
                self.original_file  # The path of the archive to extract
            ]
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error extracting file '{self.original_file}': {e}")
        
    def read_zxrules(self):
        #Function is used to pull "original" ZXRules data to use as a base to edit
        with open(self.unzipped_file, 'rb') as file:  # Open the file in binary mode
            content = file.read()
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]
        content_decoded = content.decode('utf-8')
        lines = content_decoded.splitlines()
        lines = [line + '\n' for line in lines]
        self.original_file_data = lines
        
    def write_file(self):
        with open(self.modded_file_path,'w', encoding='utf-8-sig') as f:
            for line in self.original_file_data:
                f.write(f'{line}')
                
    def zip_files_with_7zip(self):
        # Set the path to the 7zip executable
        sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'# Adjust the path based on your installation
        command = [
            sevenzip_executable,
            'a',  
            '-tzip',
            '-mx9',
            '-p' + password,
            self.zipped_file_path, 
            self.modded_file_path  ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error compressing file '{self.modded_file_path}': {e}")

class modify_sheet():
    def __init__(self,original_data):
        self.original_data  = original_data.original_file_data
        self.sheet_data     = "None"
        self.xml_data       = "None"
        self.sheet_name     = "None"
        self.excel_path     = xls_file_path
        self.extracolin     = False
        self.find_end_line  = "None"
        self.replaces       = "None"
        self.data_instance  = 0
        self.__init_vars__()
        self.data_specific_init()
    
    def __init_vars__(self):
        #there are 7 instances of this line which point to each set of data to replace
        self.find_line= '<Dictionary name="Rows" keyType="System.String, mscorlib" valueType="System.String[], mscorlib">'
        self.replaces = [["AdvancedUnitCenter","EngineeringCenter",["PLACEHOLDER"]],
                        ["MillIron","AdvancedWindmill",["PLACEHOLDER"]],
                        ["MillWood","Windmill",["PLACEHOLDER"]],
                        ["MachineGun","Wasp",["PLACEHOLDER"]],
                        ["TrapStakes","WoodTraps",["PLACEHOLDER"]],
                        ["TrapBlades","IronTraps",["PLACEHOLDER"]],
                        ['"SoldierRegular','"Soldier',["Soldier_Shot","Soldier_Trained","Soldier_Die","Soldier_What","Soldier_Yes","Soldier_Attack"]],
                        ['"SoldiersCenter','"SoldierRegularsCenter',["PLACEHOLDER"]],
                        ['"SoldierRegularAttack"','"SoldierAttack"',["PLACEHOLDER"]],
                        ["ThanatosExtraAttack","ThanatosRocket",["PLACEHOLDER"]],
                        ['"ZombieGiantAttack"','"GiantAttack"',["PLACEHOLDER"]],
                        ['"ZombieGiant"','"Giant"',["PLACEHOLDER"]],
                        ["GiantDeath","ZombieGiantDeath",["PLACEHOLDER"]],
                        ["ZombieHarpy","Harpy",["PLACEHOLDER"]],
                        ['"BHZombieGiant"','"BHGiant"',["PLACEHOLDER"]],
                        ['"ZombieGiantDeath"','"GiantDeath"',["PLACEHOLDER"]],
                        ["ZombieVenom","Spitter",["PLACEHOLDER"]],
                        ['"ZombieVenomAttack"','"SpitterAttack"',["PLACEHOLDER"]],
                        ['"ZombieGiantRoar"','"GiantRoar"',["PLACEHOLDER"]],
                        ['DeffensesLife','DefencesLife',["PLACEHOLDER"]],
                        ['ResourceCollectionCellValue','ResourceGeneration',["PLACEHOLDER"]] ]
        
    def data_specific_init(self):
        pass
    
    def find_start_location(self):
        #There are 7 locations where the data can start one for each sheet,
        #function is subclass specifc based on that data
        self.index = []
        for index, line in enumerate(self.original_data):
            if self.find_line in line:
                self.index.append(index)
                
    def find_end_location(self):
        for index, line in enumerate(self.original_data):
            if self.find_end_line in line:
                print("self.find_end_line= ", self.find_end_line)
                print("index= ", index)
                self.endindex = index
        
    def read_sheet_to_xml(self):
        
        def format_cell_value(cell):
            """
            Format the cell value to handle numeric values correctly and replace new lines with semicolons:
            - Convert numeric values with no decimal part to integers.
            - Convert other values to string.
            """
            # Explicitly check for the string "None"
            if cell == "":
                return None
            elif pd.isnull(cell):
                return None  # Return None to indicate a null value explicitly
            elif isinstance(cell, float) and cell.is_integer():
                return str(int(cell))  # Convert to int to remove trailing .0
            else:
                # Convert other values to string, handling newline replacement if necessary
                return ";".join(str(cell).split('\n'))
        
        self.dictionary = Element('Dictionary', attrib={
        'name': "Rows",
        'keyType': "System.String, mscorlib",
        'valueType': "System.String[], mscorlib"
        })
        items = SubElement(self.dictionary, 'Items')

        # Read the Excel sheet into a pandas DataFrame
        df = pd.read_excel(self.excel_path, sheet_name=self.sheet_name,keep_default_na=False)

        for _, row in df.iterrows():
            item = SubElement(items, 'Item')
            first_cell_value = format_cell_value(row.iloc[0])
            # Ensure the first cell is processed correctly, including "None"
            if first_cell_value is None:
                SubElement(item, 'Simple', attrib={'value': "None"})
            else:
                SubElement(item, 'Simple', attrib={'value': first_cell_value})

            single_array = SubElement(item, 'SingleArray', attrib={'elementType': "System.String, mscorlib"})
            items_sub = SubElement(single_array, 'Items')
            
            # Ensure the first value is added again under the single array, including handling "None"
            if first_cell_value is None:
                SubElement(items_sub, 'Simple', attrib={'value': "None"})
            else:
                SubElement(items_sub, 'Simple', attrib={'value': first_cell_value})

            for cell in row[1:]:
                cell_value = format_cell_value(cell)
                if cell_value is None:
                    SubElement(items_sub, 'Null')
                else:
                    if self.extracolin:
                        cell_value = f"{cell_value};"
                        SubElement(items_sub, 'Simple', attrib={'value': cell_value})
                    else:
                        if ";" in cell_value and not cell_value.endswith(";"):
                            cell_value = cell_value.replace(";","; ")
                        SubElement(items_sub, 'Simple', attrib={'value': cell_value})
                        
    def format_xml(self):
        rough_string = tostring(self.dictionary, 'utf-8')
        reparsed = parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        lines = pretty_xml.splitlines()
        new_lines = []
        for line in lines:
            temp_string =str("              "+line+'\n').replace('/>', ' />')
            if ";" in temp_string and ';"' not in temp_string:
                last_quote_index = temp_string.rfind('"')
                if last_quote_index != -1:  # Ensure '"' was found
                    temp_string = temp_string[:last_quote_index] + ';"' + temp_string[last_quote_index + 1:]
            if len(self.replaces) > 0:    
                for replace in self.replaces:
                    found = False
                    for exclusion in replace[2]:
                        if exclusion in temp_string:
                            found = True
                    if not found:
                        temp_string = temp_string.replace(replace[1],replace[0])
            new_lines.append(temp_string)
            
        self.xml_data = new_lines[1:]
    
    def replace_and_insert(self):
        # Remove elements from list1 between indices p and q
        # Note: since slicing does not include the end index, we don't need to adjust q
        p = self.index[self.data_instance]
        q = self.endindex
        
        print(p,q)
        list1 = self.original_data
        list2 = self.xml_data
        
        del list1[p:q]
        
        # Insert all elements from list2 at index p
        for i, item in enumerate(list2):
            list1.insert(p + i, item)
        
        return list1
    
    def recreate_text(self):
        pass
    
    def write_to_file(self):
        pass
        
class modify_entities(modify_sheet):
    def __init__(self, data):
        super().__init__(data)
        
    def data_specific_init(self):
        self.data_instance = 2
        self.sheet_name    = "mod_ZXRules_Entities"
        self.find_end_line = '<Simple name="Name" value="Entities" />'
        self.extracolin = False
        
    def vars(self):
        self.zombies     = ["ZombieWeakA","ZombieWeakB", "ZombieWeakC","ZombieWorkerA",
                            "ZombieWorkerB", "ZombieMediumA","ZombieMediumB","ZombieDressedA",
                            "ZombieStrongA","Giant","Harpy","Spitter","ZombieMutant"]
        
        self.units = ["Ranger","Soldier","Sniper","Lucifer",
                      "Thanatos","Titan","Mutant","HA","HB"]
        
    def modify_enemy_health():
        pass
    
    def modify_enenmy_damage():
        pass

class modify_mayor(modify_sheet):
    def __init__(self, data):
        super().__init__(data)
        
    def data_specific_init(self):
        self.data_instance = 7
        self.sheet_name = "ZXRules_Mayors"
        self.replaces = [["AdvancedUnitCenter","EngineeringCenter",["PLACEHOLDER"]],
                ["MillIron","AdvancedWindmill",["PLACEHOLDER"]],
                ["MillWood","Windmill",["PLACEHOLDER"]],
                ["MachineGun","Wasp",["PLACEHOLDER"]],
                ["TrapStakes","WoodTraps",["PLACEHOLDER"]],
                ["TrapBlades","IronTraps",["PLACEHOLDER"]],
                ['"SoldierRegular','"Soldier',["Soldier_Shot","Soldier_Trained","Soldier_Die","Soldier_What","Soldier_Yes","Soldier_Attack"]],
                ['"SoldiersCenter','"SoldierRegularsCenter',["PLACEHOLDER"]],
                ['SoldierRegular Life','Soldier Life',["PLACEHOLDER"]],
                ['"SoldierRegularAttack"','"SoldierAttack"',["PLACEHOLDER"]],
                ["ThanatosExtraAttack","ThanatosRocket",["PLACEHOLDER"]],
                ['"ZombieGiantAttack"','"GiantAttack"',["PLACEHOLDER"]],
                ['"ZombieGiant"','"Giant"',["PLACEHOLDER"]],
                ["GiantDeath","ZombieGiantDeath",["PLACEHOLDER"]],
                ["ZombieHarpy","Harpy",["PLACEHOLDER"]],
                ['"BHZombieGiant"','"BHGiant"',["PLACEHOLDER"]],
                ['"ZombieGiantDeath"','"GiantDeath"',["PLACEHOLDER"]],
                ["ZombieVenom","Spitter",["PLACEHOLDER"]],
                ['"ZombieVenomAttack"','"SpitterAttack"',["PLACEHOLDER"]],
                ['"ZombieGiantRoar"','"GiantRoar"',["PLACEHOLDER"]],
                ['DeffensesLife','DefencesLife',["PLACEHOLDER"]],
                ['ResourceCollectionCellValue','ResourceGeneration',["PLACEHOLDER"]]
                ]
    
class modify_commands(modify_sheet):
    def __init__(self, data):
        super().__init__(data)
        
    def data_specific_init(self):
        self.data_instance = 1
        self.sheet_name    = "mod_ZXRules_Commands"
        self.find_end_line = '<Simple name="Name" value="Commands" />'
        self.extracolin = False
    
class modify_map(modify_sheet):
    def __init__(self, data):
        super().__init__(data)
        
    def data_specific_init(self):
        self.data_instance = 2
        self.sheet_name    = "mod_ZXRules_MapConditions"

class modify_campaign(modify_sheet):
    def __init__(self, data):
        super().__init__(data)
        
    def data_specific_init(self):
        self.data_instance = 1
        self.sheet_name    = "PlaceHolder"   

#Read In Original Data
File_Data = Data()
File_Data.unzip_file_with_7zip()
File_Data.read_zxrules()


#Read in New Data
Entity_Data = modify_entities(File_Data)
Entity_Data.read_sheet_to_xml()
Entity_Data.format_xml()

Command_Data = modify_commands(File_Data)
Command_Data.read_sheet_to_xml()
Command_Data.format_xml()


#Put Data back into original
Entity_Data.find_start_location()
Entity_Data.find_end_location()
File_Data.original_file_data  = Entity_Data.replace_and_insert()

Command_Data.find_start_location()
Command_Data.find_end_location()
File_Data.original_file_data  = Command_Data.replace_and_insert()


#Write and put back data
File_Data.write_file()
File_Data.zip_files_with_7zip()