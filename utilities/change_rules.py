password = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import subprocess
import os
import shutil
import pandas as pd

rulesfilename = 'ZXRules.dat'
rulespassword = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
filenameCampaign = 'ZXCampaign.dat' 
campaignpassword = '1688788812-163327433-2005584771'

class Data():
    # Class sheet handles parsing and holding of original data as well as any modifications to it
    def __init__(self,filename,password,game_directory,working_directory,sevenzip_executable):
        self.password             = password
        self.filename             = filename
        self.working_directory    = working_directory
        self.original_folder      = f'{working_directory}/original/'
        self.original_file        = f'{working_directory}/original/{filename}'
        self.unzipped_folder      = f'{working_directory}/unzipped/'
        self.unzipped_file        = f'{working_directory}/unzipped/{filename}'
        self.modded_folder        = f'{working_directory}/modded/'
        self.modded_file          = f'{working_directory}/modded/{filename}'
        self.zipped_folder        = f'{working_directory}/rezipped/'
        self.zipped_file          = f'{working_directory}/rezipped/{filename}'
        self.game_directory       = f'{game_directory}/{filename}'
        self.sevenzip_executable  = sevenzip_executable
        self.original_file_data   = []
        self.create_paths()
        
    def create_paths(self):
        
        os.makedirs(f'{self.original_folder}', exist_ok=True)
        os.makedirs(f'{self.unzipped_folder}', exist_ok=True)
        os.makedirs(f'{self.modded_folder}', exist_ok=True)
        os.makedirs(f'{self.zipped_folder}', exist_ok=True)
        shutil.copy(self.game_directory,self.original_folder)
        if not os.path.exists(self.game_directory):
            print(f'Didnt Find {self.game_directory} in Game Directory')
            return 
        
    def unzip_file_with_7zip(self):
          # Adjust the path based on your installation
        try:
            command = [
                self.sevenzip_executable,
                'x',  # Extract files with full paths
                '-y',  # Assume Yes on all queries (overwrite files without prompting)
                f'-p{self.password}',  # Password for the archive
                f'-o{self.unzipped_folder}',  # Output directory
                self.original_file  # The path of the archive to extract
            ]
            subprocess.run(command, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'{self.filename} Successfully Unzipped')
        except subprocess.CalledProcessError as e:
            print(f"Error extracting file '{self.original_file}': {e}")
        
    def read_file(self):
        #Function is used to pull "original" ZXRules data to use as a base to edit
        with open(self.unzipped_file, 'rb') as file:  # Open the file in binary mode
            content = file.read()
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]
        content_decoded = content.decode('utf-8')
        lines = content_decoded.splitlines()
        lines = [line + '\n' for line in lines]
        self.original_file_data = lines
        print(f'{self.filename} Successfully Read')
        
    def write_file(self):
        with open(self.modded_file,'w', encoding='utf-8-sig') as f:
            for line in self.original_file_data:
                f.write(f'{line}')
        print(f'{self.filename} Successfully Wrote')
                
    def zip_files_with_7zip(self):
        # Set the path to the 7zip executable
        command = [
            self.sevenzip_executable,
            'a',  
            '-tzip',
            '-mx9',
            '-p' + self.password,
            self.zipped_file, 
            self.modded_file  ]
        try:
            subprocess.run(command, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Error compressing file '{self.modded_file}': {e}")
            
        print(f'{self.filename} Successfully Rezipped')
            
    def move_file(self):
        shutil.copy(self.zipped_file,self.game_directory)
        print(f'{self.filename} Successfully Moved to {self.game_directory}')

class modify_sheet():
    def __init__(self,original_data,xls_file_path):
        self.original_data     = original_data.original_file_data
        self.sheet_data        = "None"
        self.xml_data          = "None"
        self.sheet_name        = "None"
        self.excel_path        = xls_file_path
        self.extracolin        = False
        self.removendcolin     = False
        self.extra_colin_space = True
        self.find_end_line     = "None"
        self.replaces          = "None"
        self.data_instance     = 0
        
        xls_file = pd.ExcelFile(xls_file_path)
        sheets = xls_file.sheet_names
        self.data_specific_init()
        
        if self.sheet_name in sheets:
            self.valid_sheet = True
        else:
            self.valid_sheet = False
    
    def find_start_location(self):
        #There are 7 locations where the data can start one for each sheet,
        #function is subclass specifc based on that data
        self.index     = []
        self.find_line = '<Dictionary name="Rows" keyType="System.String, mscorlib" valueType="System.String[], mscorlib">'
        for index, line in enumerate(self.original_data):
            if self.find_line in line:
                self.index.append(index)
                  
    def find_end_location(self):
        for index, line in enumerate(self.original_data):
            if self.find_end_line in line:
                self.endindex = index
    
    @staticmethod
    def format_cell_value(cell):
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

    def read_sheet_to_xml(self):
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
            first_cell_value = modify_sheet.format_cell_value(row.iloc[0])
            
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
                cell_value = modify_sheet.format_cell_value(cell)
                if cell_value is None:
                    SubElement(items_sub, 'Null')
                else:
                    if self.extracolin:
                        cell_value = f"{cell_value};"
                        SubElement(items_sub, 'Simple', attrib={'value': cell_value})
                    else:
                        
                        if ";" in cell_value and not cell_value.endswith(";") and self.extra_colin_space:
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
            if "&amp;amp;" in temp_string:
                temp_string = temp_string.replace("&amp;amp;","&amp;")
            if ';" />' in temp_string and self.removendcolin:
                temp_string = temp_string.replace(';" />','" />')   
            new_lines.append(temp_string)
            
        self.xml_data = new_lines[1:]
    
    def replace_and_insert(self):
        # Remove elements from list1 between indices p and q
        p = self.index[self.data_instance]
        q = self.endindex
        
        list1 = self.original_data
        list2 = self.xml_data
        
        del list1[p:q]
        
        # Insert all elements from list2 at index p
        for i, item in enumerate(list2):
            list1.insert(p + i, item)
        
        return list1
    
class modify_entities(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 2
        self.sheet_name    = "ZXRules_Entities"
        self.find_end_line = '<Simple name="Name" value="Entities" />'
        
class modify_globals(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 3
        self.sheet_name    = "ZXRules_Globals"
        self.find_end_line = '<Simple name="Name" value="Global" />'
        
class modify_mayor(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 6
        self.sheet_name = "ZXRules_Mayors"
        self.find_end_line = '<Simple name="Name" value="Mayors" />'
    
class modify_commands(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 1
        self.sheet_name    = "ZXRules_Commands"
        self.find_end_line = '<Simple name="Name" value="Commands" />'
    
class modify_mapconditions(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 4
        self.sheet_name    = "ZXRules_MapConditions"
        self.find_end_line = '<Simple name="Name" value="MapConditions" />'

class modify_campaign(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 1
        self.sheet_name    = "PlaceHolder"   

class modify_mapthemes(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 5
        self.sheet_name    = "ZXRules_MapThemes"
        self.find_end_line = '<Simple name="Name" value="MapThemes" />'

class modify_heros(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 1
        self.sheet_name    = "ZXCampaign_Heros"
        self.find_end_line = '<Simple name="Name" value="HeroPerks" />'

class modify_waves(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 2
        self.sheet_name    = "ZXCampaign_Waves"
        self.find_end_line = '<Simple name="Name" value="LevelEvents" />'
        
class modify_missions(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 3
        self.sheet_name    = "ZXCampaign_Missions"
        self.find_end_line = '<Simple name="Name" value="Missions" />'
            
class modify_research(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 4
        self.sheet_name    = "ZXCampaign_Research"
        self.find_end_line = '<Simple name="Name" value="Researchs" />'

class modify_researchtree(modify_sheet):
    def __init__(self, data, xls_file_path):
        super().__init__(data,xls_file_path)
        
    def data_specific_init(self):
        self.data_instance = 5
        self.sheet_name    = "ZXCampaign_ResearchTree"
        self.find_end_line = '<Simple name="Name" value="ResearchTree" />'
