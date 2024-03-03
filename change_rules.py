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
import re
import shutil

xls_file_path = 'C:/Users/Josh/Downloads/Rebalanced Mod.xlsx'

rulesfilename = 'ZXRules.dat'
rulespassword = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
filenameCampaign = 'ZXCampaign.dat' 
campaignpassword = '1688788812-163327433-2005584771'

class Data():
    # Class sheet handles parsing and holding of original data as well as any modifications to it
    def __init__(self,filename,password,game_directory,working_directory,sevenzip_executable):
        self.password = password
        self.filename = filename
        self.working_directory = working_directory
        self.original_file        = f'{working_directory}/original/{filename}'
        self.unzipped_file_path   = f'{working_directory}/unzipped/'
        self.unzipped_file        = f'{working_directory}/unzipped/{filename}'
        self.modded_file_path     = f'{working_directory}/modded/{filename}'
        self.zipped_file_path     = f'{working_directory}/rezipped/{filename}'
        self.game_directory       = f'{game_directory}/{filename}'
        self.original_file_data   = []
        self.sevenzip_executable  = sevenzip_executable
        self.validate_paths()
        
    def validate_paths(self):
        if os.path.exists(self.original_file):
            print(f'Found {self.filename}')
        else:
            print(f'Didnt Find {self.filename} in {self.original_file}')
            
        #os.makedirs(self.unzipped_file_path, exist_ok=True)    
        os.makedirs(f'{self.working_directory}/unzipped/', exist_ok=True)
        os.makedirs(f'{self.working_directory}/modded/', exist_ok=True)    
        os.makedirs(f'{self.working_directory}/rezipped/', exist_ok=True)    
        
    def unzip_file_with_7zip(self):
          # Adjust the path based on your installation
        try:
            command = [
                self.sevenzip_executable,
                'x',  # Extract files with full paths
                '-y',  # Assume Yes on all queries (overwrite files without prompting)
                f'-p{self.password}',  # Password for the archive
                f'-o{self.unzipped_file_path}',  # Output directory
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
        with open(self.modded_file_path,'w', encoding='utf-8-sig') as f:
            for line in self.original_file_data:
                f.write(f'{line}')
        print(f'{self.filename} Successfully Wrote')
                
    def zip_files_with_7zip(self):
        # Set the path to the 7zip executable
        sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'# Adjust the path based on your installation
        command = [
            sevenzip_executable,
            'a',  
            '-tzip',
            '-mx9',
            '-p' + self.password,
            self.zipped_file_path, 
            self.modded_file_path  ]
        try:
            subprocess.run(command, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Error compressing file '{self.modded_file_path}': {e}")
            
        print(f'{self.filename} Successfully Rezipped')
            
    def move_file(self):
        shutil.copy(self.zipped_file_path,self.game_directory)
        print(f'{self.filename} Successfully Moved to {self.game_directory}')

class modify_sheet():
    def __init__(self,original_data,xls_file_path,modded = False):
        self.original_data  = original_data.original_file_data
        self.sheet_data     = "None"
        self.xml_data       = "None"
        self.modded         = modded
        self.sheet_name     = "None"
        self.excel_path     = xls_file_path
        self.extracolin     = False
        self.removendcolin  = False
        self.extra_colin_space = True
        self.find_end_line  = "None"
        self.replaces       = "None"
        self.data_instance  = 0
        self.__init_vars__()
        self.data_specific_init()
        self.modded_sheet()
    
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
    
    def modded_sheet(self):
        if not self.modded:
            self.sheet_name = self.sheet_name.replace("mod_","")
    
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
                self.endindex = index
  
    def read_sheet_to_xml(self):
        
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
            if len(self.replaces) > 0:    
                for replace in self.replaces:
                    found = False
                    for exclusion in replace[2]:
                        if exclusion in temp_string:
                            found = True
                    if not found:
                        temp_string = temp_string.replace(replace[1],replace[0])
            if "&amp;amp;" in temp_string:
                temp_string = temp_string.replace("&amp;amp;","&amp;")
            if ';" />' in temp_string and self.removendcolin:
                temp_string = temp_string.replace(';" />','" />')
            if 'Rainy;"' in temp_string:
                temp_string = temp_string.replace('Rainy;"','Rainy"')
            if 'Snowy"' in temp_string:
                temp_string = temp_string.replace('Snowy"','Snowy;"')
            if 'SlowTerrain"' in temp_string:
                temp_string = temp_string.replace('SlowTerrain"','SlowTerrain;"')        
            new_lines.append(temp_string)
            
        self.xml_data = new_lines[1:]
    
    def replace_and_insert(self):
        # Remove elements from list1 between indices p and q
        # Note: since slicing does not include the end index, we don't need to adjust q
        p = self.index[self.data_instance]
        q = self.endindex
        
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
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 2
        self.sheet_name    = "mod_ZXRules_Entities"
        self.find_end_line = '<Simple name="Name" value="Entities" />'
        self.extracolin = False
        self.zombies = ["ZombieWeakA","ZombieWeakB", "ZombieWeakC","ZombieWorkerA",
                        "ZombieWorkerB", "ZombieMediumA","ZombieMediumB","ZombieDressedA",
                        "ZombieStrongA","ZombieGiant","ZombieHarpy","ZombieVenom","ZombieMutant"]
        self.units   = ["Ranger","SoldierRegular","Sniper","Lucifer",
                        "Thanatos","Titan","Mutant","HA","HB"]
        
        self.entity_attributes = ["ID","Order","Key","Name","Description","PanelPosition","Nature","Category","Level","Power","CommandRequisite","BuildingRequisite","UpgradeTo","ExperienceNeededToVeteran","Life","Armor","DeffensesLife","LifeRegenFactor","WatchRange","EntityWatchInterval","WatchThroughOpaque","WalkSpeed","RunSpeed","Mass","Height","ActivityAwarenessFactor","BuildingTimeFactor","FactorResourcesReturn","BuildingFrom","BuildingTarget","BuildingMargin","SameBuildingMargin","IgnoreBuildingsMargin","MaxBuildingsAdjacent","MinEmptyCellsAdjacent","CanBeDestroyed","CanBeRepaired","CanBeDisabled","MaxUnitsInside","RangeBonus","MaxInstances","MinColonistsRequisite","CanQueueCommands","CanBeBuiltOnWalls","ColonistType","ColonistUnitNumber","ScorePoints","EngineeringPoints","SciencePoints","EmpirePoints","DisableWithoutEnergy","EnergyTransferRadius","ResourcesStorage","FireDamageFactor","InflamableTime","BurningTime","VenomDamageFactor","Infectable","ExtraUnitsWhenInfected","ConvertibleInZombie","VibrateWhenDamaged","ExplosionOnDestroy","WorkersNeeded","FoodNeeded","EnergyNeeded","GoldCost","WoodCost","StoneCost","IronCost","OilCost","Colonists","WorkersSupply","FoodSupply","EnergySupply","WoodGen","StoneGen","IronGen","OilGen","GoldGen","GoldGenPerColonist","ConvertResourcesIntoGold","ResourcesGenerationTimeFactor","ResourceCollectionType","ResourceCollectionRadius","ResourceCollectionCellValue","Averageunitsperturnestimated","AffectedByEnhancerBuildings","FactorProductionNearBuildings","FactorGoldNearBuildings","FactorFoodNeedNearBuildings","MakeSoldiersVeteran","ShowFullMap","CanEnterInBuildings","CanTravel","CanStop","CanHold","CanPatrol","CanChase","CanJump","CanBeCarried","CanCarryObjects","CanCounterAttack","TimeAniNormal","TimeAniSpecial","TimeAniWalk","TimeAniRun","TimeAniDie","TimeAniWork","TimeAniPrepareWork","TimeAniFly","TimeAniPrepareFly","ReverseAniNormal","ReverseAniSpecial","TimeAniJump","TimeAniThrow","TimeAniInteract","AttackCommand","ExtraAttackCommand","BellWalkingFactor","BellRunningFactor","MinRoamingDistance","MaxRoamingDistance","CellsAwayCommandCenter","Behaviour","CanAvoidOverkill","CanBePulled","DisableDiagonalBuilding","EndGameIfInfected","EndGameIfDestroyed","InfectionNestSize","InfectionNestMaxUnits","TerrainSpeedPercentage","GoldPerKill","EmpirePointsCost","NDaysNewMercenariesInterval","FactorCostMercenaries","FactorPrestige","SoundOnDestroy","SoundOnCreation","SoundOnDie","SoundOnSelected","SoundOnCommandGeneric","SoundOnCommandAttack","SoundOnInfection","SoundOnDesertion","SoundOnPick"]
        
    def get_all_locations(self):
        self.zombies_dict = {}
        self.units_dict = {}
        strstart = '<Simple value="'
        strfin = '" />'
        strsec = '<SingleArray elementType="System.String, mscorlib">'
        
        for zombie in self.zombies:
            searchstr = f'{strstart}{zombie}{strfin}'
            for index, line in enumerate(self.xml_data):
                if searchstr in line:
                    if index + 1 < len(self.xml_data):
                        next_line = self.xml_data[index + 1]
                        if strsec in next_line:
                            self.zombies_dict[zombie] = index + 3
                            
        for units in self.units:
            searchstr = f'{strstart}{units}{strfin}'
            for index, line in enumerate(self.xml_data):
                if searchstr in line:
                    if index + 1 < len(self.xml_data):
                        next_line = self.xml_data[index + 1]
                        if strsec in next_line:
                            self.units_dict[units] = index + 3
    
    def set_attritbute(self, attribute, entity, value):
        att_index      = self.entity_attributes.index(attribute)
        
        if entity in self.units_dict:
            att_index_ent  = att_index + self.units_dict[entity]
        elif entity in self.zombies_dict:
            att_index_ent  = att_index + self.zombies_dict[entity]
        else:
            print(f'Could not find {entity}')
            return    
        
        fst_split_str = '<Simple value="'
        est_split_str = '" />'
        null_split    = "<Null"
        
        if null_split not in self.xml_data[att_index_ent]:
            initial_split = self.xml_data[att_index_ent].split(fst_split_str,maxsplit = 1)
            keep_split_front = f'{initial_split[0]}{fst_split_str}'
            data_split  = initial_split[1].split(est_split_str)[0]
            if ',' in data_split:
                result = f"{value:.2f}".replace('.', ',')
            else:
                # Input does not contain a comma, treat as integer
                number = int(data_split)
                # Multiply by scalar and convert back to string
                result = str(int(value))
                
            self.xml_data[att_index_ent] = f'{keep_split_front}{result}{est_split_str}\n'
        else:
            if ',' in data_split:
                result = f"{value:.2f}".replace('.', ',')
            temp_spaces = self.xml_data[att_index_ent].replace("<Null","")
            self.xml_data[att_index_ent] = f'{temp_spaces}{fst_split_str}{result}{est_split_str}\n'
            
        print(f'{entity} {attribute} set to {value}')
        
    def modify_attribute(self, attribute, entity, scalar):
        att_index      = self.entity_attributes.index(attribute)
        
        if entity in self.units_dict:
            att_index_ent  = att_index + self.units_dict[entity]
        elif entity in self.zombies_dict:
            att_index_ent  = att_index + self.zombies_dict[entity]
        else:
            print(f'Could not find {entity}')
            return    
        
        fst_split_str = '<Simple value="'
        est_split_str = '" />'
        
        if "<Null />" in self.xml_data[att_index_ent]:
            print("No initial value cannot modify")
            pass
        else:
            initial_split = self.xml_data[att_index_ent].split(fst_split_str,maxsplit = 1)
            keep_split_front = f'{initial_split[0]}{fst_split_str}'
            data_split  = initial_split[1].split(est_split_str)[0]
            if ',' in data_split:
                # Replace comma with period and convert to float
                number = float(data_split.replace(',', '.'))
                result = f"{number * scalar:.2f}".replace('.', ',')
            else:
                # Input does not contain a comma, treat as integer
                number = int(data_split)
                # Multiply by scalar and convert back to string
                result = str(int(number * scalar))
                
        self.xml_data[att_index_ent] = f'{keep_split_front}{result}{est_split_str}\n'

    def modify_all_zombies(self,attribute,scalar):
        for zombie in self.zombies:
            self.modify_attribute(attribute,zombie,scalar)
            
    def get_attribute(self,attribute,entity):
        att_index      = self.entity_attributes.index(attribute)
        
        if entity in self.units_dict:
            att_index_ent  = att_index + self.units_dict[entity]
        elif entity in self.zombies_dict:
            att_index_ent  = att_index + self.zombies_dict[entity]
        else:
            print(f'Could not find {entity}')
            return    
        
        fst_split_str = '<Simple value="'
        est_split_str = '" />'
        
        if "<Null />" in self.xml_data[att_index_ent]:
            print("No initial value cannot modify")
            return "Null"
            pass
        else:
            initial_split = self.xml_data[att_index_ent].split(fst_split_str,maxsplit = 1)
            keep_split_front = f'{initial_split[0]}{fst_split_str}'
            data_split  = initial_split[1].split(est_split_str)[0]
            if ',' in data_split:
                # Replace comma with period and convert to float
                number = float(data_split.replace(',', '.'))
                result = f"{number:.2f}".replace('.', ',')
            else:
                try:
                    # Input does not contain a comma, treat as integer
                    number = int(data_split)
                    # Multiply by scalar and convert back to string
                    result = str(int(number))
                except:
                    result = data_split
        return result

class modify_mayor(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 6
        self.sheet_name = "mod_ZXRules_Mayors"
        self.find_end_line =  '<Simple name="Name" value="Mayors" />'
        self.replaces = [["AdvancedUnitCenter","EngineeringCenter",["PLACEHOLDER"]],
                ["MillIron","AdvancedWindmill",["PLACEHOLDER"]],
                ["MillWood","Windmill",["PLACEHOLDER"]],
                ["MachineGun","Wasp",["PLACEHOLDER"]],
                ["TrapStakes","WoodTraps",["PLACEHOLDER"]],
                ["TrapBlades","IronTraps",["PLACEHOLDER"]],
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
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 1
        self.sheet_name    = "mod_ZXRules_Commands"
        self.find_end_line = '<Simple name="Name" value="Commands" />'
        self.extracolin = False
    
class modify_mapconditions(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 3
        self.sheet_name    = "mod_ZXRules_MapConditions"

class modify_campaign(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 1
        self.sheet_name    = "PlaceHolder"   

class modify_mapthemes(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 5
        self.sheet_name    = "mod_ZXRules_MapThemes"
        self.find_end_line = '<Simple name="Name" value="MapThemes" />'

class modify_heros(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 1
        self.sheet_name    = "mod_ZXCampaign_Heros"
        self.find_end_line = '<Simple name="Name" value="HeroPerks" />" />'

class modify_waves(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 2
        self.extracolin    = False
        self.removendcolin = True
        self.extra_colin_space = False
        removal = ["ZombieHarpy","Harpy",["PLACEHOLDER"]]
        self.replaces.remove(removal)
        self.sheet_name    = "mod_ZXCampaign_Waves"
        self.find_end_line = '<Simple name="Name" value="LevelEvents" />'
        
class modify_missions(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 3
        self.removendcolin = True
        self.extra_colin_space = False
        self.sheet_name    = "mod_ZXCampaign_Missions"
        self.find_end_line = '<Simple name="Name" value="Missions" />'
            
class modify_research(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 4
        removal = ['"SoldierRegular','"Soldier',["Soldier_Shot","Soldier_Trained","Soldier_Die","Soldier_What","Soldier_Yes","Soldier_Attack"]]
        self.replaces.remove(removal)
        self.sheet_name    = "mod_ZXCampaign_Research"
        self.find_end_line = '<Simple name="Name" value="Researchs" />'

class modify_researchtree(modify_sheet):
    def __init__(self, data, xls_file_path,modded = False):
        super().__init__(data,xls_file_path,modded)
        
    def data_specific_init(self):
        self.data_instance = 5
        removal = ['"SoldierRegular','"Soldier',["Soldier_Shot","Soldier_Trained","Soldier_Die","Soldier_What","Soldier_Yes","Soldier_Attack"]]
        self.replaces.remove(removal)
        self.sheet_name    = "mod_ZXCampaign_ResearchTree"
        self.find_end_line = '<Simple name="Name" value="ResearchTree" />'
        
# #Read In Original Data
# File_Data = Data(rulesfilename,rulespassword)
# File_Data.unzip_file_with_7zip()
# File_Data.read_file()

# cFile_Data = Data(filenameCampaign,campaignpassword)
# cFile_Data.unzip_file_with_7zip()
# cFile_Data.read_file()

# Wave_Data = modify_waves(cFile_Data)
# Wave_Data.read_sheet_to_xml()
# Wave_Data.format_xml()    
# Wave_Data.find_start_location()
# Wave_Data.find_end_location()
# cFile_Data.original_file_data = Wave_Data.replace_and_insert()

# mission_Data = modify_missions(cFile_Data)
# mission_Data.read_sheet_to_xml()
# mission_Data.format_xml()    
# mission_Data.find_start_location()
# mission_Data.find_end_location()
# cFile_Data.original_file_data = mission_Data.replace_and_insert()

# research_Data = modify_research(cFile_Data)
# research_Data.read_sheet_to_xml()
# research_Data.format_xml()    
# research_Data.find_start_location()
# research_Data.find_end_location()
# cFile_Data.original_file_data = research_Data.replace_and_insert()

# researchtree_Data = modify_researchtree(cFile_Data)
# researchtree_Data.read_sheet_to_xml()
# researchtree_Data.format_xml()    
# researchtree_Data.find_start_location()
# researchtree_Data.find_end_location()
# cFile_Data.original_file_data = researchtree_Data.replace_and_insert()

# cFile_Data.write_file()
# cFile_Data.zip_files_with_7zip()
# cFile_Data.move_file()


# #Read in New Data
# Entity_Data = modify_entities(File_Data)
# Entity_Data.read_sheet_to_xml()
# Entity_Data.format_xml()
# Entity_Data.get_all_locations()
# Entity_Data.modify_all_zombies("Life",2)
# Entity_Data.find_start_location()
# Entity_Data.find_end_location()
# File_Data.original_file_data  = Entity_Data.replace_and_insert()

# Command_Data = modify_commands(File_Data)
# Command_Data.read_sheet_to_xml()
# Command_Data.format_xml()
# Command_Data.find_start_location()
# Command_Data.find_end_location()
# File_Data.original_file_data  = Command_Data.replace_and_insert()

# MapTheme_Data = modify_mapthemes(File_Data)
# MapTheme_Data.read_sheet_to_xml()
# MapTheme_Data.format_xml()
# MapTheme_Data.find_start_location()
# MapTheme_Data.find_end_location()
# File_Data.original_file_data  = MapTheme_Data.replace_and_insert()

# #Write and put back data
# File_Data.write_file()
# File_Data.zip_files_with_7zip()
# File_Data.move_file()

