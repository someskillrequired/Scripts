import os
import subprocess
import pygame
from PIL import Image
import base64
import re
import pygame_gui
import json
import math
from pathlib import Path
import io
import sys
import tkinter as tk
from tkinter import filedialog

DEBUG = False
sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'
sprite_base_path = r'D:\SteamLibrary\steamapps\common\They Are Billions\ZXGame_Data\Sprites'

BYTES_PER_WORD = 4
starting_zoom_level = 100
starting_cell_size = int(5 * (starting_zoom_level/ 100.0))

class TestSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class ImageHandler():
    #imports .dat file and converts them to useable sprites for placement
    def __init__(self,file,x1,y1,x2,y2,scale_x,scale_y = False,pixels_cell_size = 5,cell_size = 1):
        self.cell_size = cell_size
        self.pixels_cell_size = pixels_cell_size
        
        self.entire_image = self.pull_image_data(file)
        self.cut_image = self.get_cut_image(self.entire_image,x1,y1,x2,y2)
        self.final_image = self.scale_image(self.cut_image,scale_x,scale_y)  
        
    def pull_image_data(self,file):
        with open(file, 'rb') as f:
            encoded_data = f.read()
        image = Image.open(io.BytesIO(encoded_data))
        # Convert the PIL image to a Pygame surface
        mode = image.mode
        size = image.size
        data = image.tobytes()
        entire_image = pygame.image.frombuffer(data, size, mode)
        return entire_image

    def get_cut_image(self, entire_image, x1, y1, x2, y2):
        # Calculate the width and height based on the coordinates
        self.width = x2 - x1
        self.height = y2 - y1
        # Extract a single image from the sprite sheet
        cut_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        cut_image.blit(entire_image, (0, 0), (x1, y1, self.width, self.height))
        return cut_image

    def scale_image(self,image,scale_x,scale_y):
        if not scale_y:
            scale_y = scale_x
        
        image = pygame.transform.scale(image, (scale_x * self.cell_size*self.pixels_cell_size , scale_y * self.cell_size*self.pixels_cell_size))
        return image

sprite_dict_zombies = { "ZombieUltra1": {"x1"  : 2175,
                          "y1"  : 1720,
                          "x2"  : 2247,
                          "y2"  : 1795,
                          "path": sprite_base_path  + r"\InfectedGiant_LQ.dat",
                          "cell_size": 3},
               
                        "ZombieWeak1" :{"x1"  : 0,
                                "y1"  : 1245,
                                "x2"  : 35,
                                "y2"  : 1295,
                                "path": sprite_base_path + r"\InfectedA_LQ.dat"},
                        
                        "ZombieWeak2" :{"x1"  : 0,
                                "y1"  : 2775,
                                "x2"  : 35,
                                "y2"  : 2835,
                                "path": sprite_base_path + r"\InfectedA_LQ.dat"},
                        
                        "ZombieWeak3" :{"x1"  : 0,
                                        "y1"  : 1035,
                                        "x2"  : 30,
                                        "y2"  : 1085,
                                        "path": sprite_base_path + r"\InfectedA_LQ.dat"},
                        
                        "ZombieStrong1" :{"x1"  : 2500,
                                    "y1"  : 3740,
                                    "x2"  : 2535,
                                    "y2"  : 3800,
                                    "path": sprite_base_path + r"\InfectedA_LQ.dat"},
                        
                        "ZombieStrong2" :{"x1"  : 0,
                                "y1"  : 3455,
                                "x2"  : 30,
                                "y2"  : 3525,
                                "path": sprite_base_path + r"\InfectedC_LQ.dat"},
                        
                        "ZombieStrong3" :{"x1"  : 60,
                                "y1"  : 3525,
                                "x2"  : 95,
                                "y2"  : 3595,
                                "path": sprite_base_path + r"\InfectedC_LQ.dat"},
                        
                        "ZombiePowerful1" :{"x1"  : 0,
                                "y1"  : 0,
                                "x2"  : 110,
                                "y2"  : 95,
                                "path": sprite_base_path + r"\InfectedD_LQ.dat",
                                "cell_size": 3},
                        
                        "ZombiePowerful2" :{"x1"  : 0,
                                "y1"  : 515,
                                "x2"  : 45,
                                "y2"  : 565,
                                "path": sprite_base_path + r"\InfectedB_LQ.dat"},
                
                # "blank" :{"x1"  : 0,
                #           "y1"  : 0,
                #           "x2"  : 0,
                #           "y2"  : 0,
                #           "path": sprite_base_path + r""},
                
}                     
                               
colors = {
    "None": (255, 255, 255),
    "Water": (25, 25, 112),
    "Earth": (245, 222, 179),
    "Grass": (124, 252, 0),
    "Stone": (169, 169, 169),
    "Iron": (135, 206, 250),
    "Oil": (128, 0, 128),
    "Gold": (255, 215, 0),
    "Road": (255, 255, 255),
    "Wood": (0, 100, 0),
    "Mountain": (139, 69, 19),
    "Sky": (30, 144, 255),
    "Abyse": (255, 69, 0),
    "Default": (255, 0, 0),
    "ZombieNone": (255, 255, 255),
    "ZombieMedium1": (255, 255, 153),  # Light Yellow
    "ZombieMedium2": (255, 255, 0),    # Yellow
    "ZombieMedium3": (204, 204, 0),    # Yello
    }

LayerObjects = {0: "None",
                1: "Mountain",
                2: "Wood",
                3: "Gold",
                4: "Stone",
                5: "Iron"}

LayerTerrain =  {
                0: "Earth",
                1: "Water",
                2: "Grass",
                3: "Sky",  
                4: "Abyse"}

LayerZombies = {
    0: "ZombieNone",
    1: "ZombieWeak1",
    2: "ZombieWeak2",
    3: "ZombieWeak3",
    4: "ZombieMedium1",
    5: "ZombieMedium2",
    6: "ZombieMedium3",
    7: "ZombieStrong1",
    8: "ZombieStrong2",
    9: "ZombieStrong3",
    10: "ZombiePowerful1",
    11: "ZombiePowerful2",
    12: "ZombieUltra1"
}

MiscObjects ={"14597207313853823957":"OilSource",
              "1130949242559706282" :"TruckA",
              "1858993070642015232" :"FortressBarLeft",
              "5955209075099213047" :"FortressBarRight",
              "2617794739528169237" :"TensionTowerMediumFlip",
              "4533866769353242870" :"TensionTowerMedium",
              "2342596987766548617" :"TensionTowerHighFlip",
              "3359149191582161849" :"TensionTowerHigh"}

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
    "The Goddess of Destiny":     "REND.dxlevel",
    "Swarm 1" :                   "RS1.dxlevel",
    "Swarm 2" :                   "RS2.dxlevel",
    "Swarm 3" :                   "RS3.dxlevel",
    "Swarm 4" :                   "RS4.dxlevel",
    "Swarm 5" :                   "RS5.dxlevel",
    "Swarm 6" :                   "RS6.dxlevel",
    "Swarm 7" :                   "RS7.dxlevel",
    "Swarm 8" :                   "RS8.dxlevel",
    "Swarm 9" :                   "RS9.dxlevel",
    "Swarm a" :                   "RSA.dxlevel",
    "Swarm b" :                   "RSB.dxlevel",
    "Swarm c" :                   "RSC.dxlevel",
    "Swarm d" :                   "RSD.dxlevel",
    "Swarm e" :                   "RSE.dxlevel",
    "Swarm f" :                   "RSF.dxlevel",
    "Tactic 1" :                  "RF1.dxlevel",
    "Tactic 2" :                  "RF2.dxlevel",
    "Tactic 3" :                  "RF3.dxlevel",
    "Tactic 4" :                  "RF4.dxlevel",
    "Tactic 5" :                  "RF5.dxlevel",
    "Tactic 6" :                  "RF6.dxlevel",
    "Tactic 7" :                  "RF7.dxlevel",
    "Tactic 8" :                  "RF8.dxlevel",
    "Tactic A" :                  "RFA.dxlevel",
    "Tactic B" :                  "RFB.dxlevel",
}

knownBonusEntsNice = {
        '877281890077159856': 'AdvancedFarm',
        '6574833960938744452': 'AdvancedQuarry',
        '8857617519118038933': 'AdvancedUnitCenter',
        '1621013738552581284': 'Ballista',
        '5036892806562984913': 'Bank',
        '7736771959523609744': 'BunkerHouse',
        '3153977018683405164': 'CommandCenter',
        '1886362466923065378': 'CottageHouse',
        '3441286325348372349': 'DoomBuildingLarge',
        '293812117068830615': 'DoomBuildingMedium',
        '8702552346733362645': 'DoomBuildingSmall',
        '3581872206503330117': 'EnergyWoodTower',
        '782017986530656774': 'Executor',
        '7709119203238641805': 'Farm',
        '13910727858942983852': 'FishermanCottage',
        '14944401376001533849': 'Foundry',
        '18390252716895796075': 'GateStone',
        '8865737575894196495': 'GateWood',
        '1313209346733379187': 'Heater',
        '706050193872584208': 'HunterCottage',
        '2357834872970637499': 'InfectedNestBig',
        '9352245195514814739': 'LookoutTower',
        '5507471650351043258': 'Market',
        '12238914991741132226': 'MillIron',
        '869623577388046954': 'MillWood',
        '15110117066074335339': 'OilPlatform',
        '12703689153551509267': 'PowerPlant',
        '4012164333689948063': 'Quarry',
        '10083572309367106690': 'RadarTower',
        '6362162278734053601': 'Refinery',
        '6484699889268923215': 'Sawmill',
        '7671446590444700196': 'ShockingTower',
        '8537111584635793949': 'Shuttle',
        '17945382406851792953': 'SoldiersCenter',
        '17389931916361639317': 'StoneHouse',
        '11153810025740407576': 'StoneWorkshop',
        '17301104073651661026': 'TentHouse',
        '2562764233779101744': 'TrapBlades',
        '3791255408779778776': 'TrapMine',
        '17047104131874756555': 'TrapPetrol',
        '14605210100319949981': 'TrapStakes',
        '7684920400170855714': 'WallStone',
        '16980392503923994773': 'WallWood',
        '13640414733981798546': 'WareHouse',
        '16597317129181541225': 'WatchTowerStone',
        '11206202837167900273': 'WatchTowerWood',
        '2943963846200136989': 'WoodWorkshop',
        '16241120227094315491': 'Lucifer',
        '11462509610414451330': 'Ranger',
        '12735209386004068058': 'Raven',
        '6536008488763521408': 'Sniper',
        '8122295062332983407': 'SoldierRegular',
        '13687916016325214957': 'Thanatos',
        '15625692077980454078': 'Titan',
        '3208367948340991825': 'Worker_A',
        '13977466055377379252': 'Worker_B',
        '8049232565215955390': 'WorkerRunner_A',
        '7404423790615406394': 'WorkerRunner_B',
    }
       
class map:
    def __init__(self,directory,map_name,sevenzip_executable):
        self.directory = directory
        self.sevenzip_executable = sevenzip_executable
        
        self.loaded_folder_path           = os.path.join(directory)
        self.loaded_original_file_path    = os.path.join(directory,map_name)
        self.unzipped_folder_path         = os.path.join(directory,"custom_maps_unzipped_no_changes")
        self.unzipped_file_path           = os.path.join(directory,"custom_maps_unzipped_no_changes",map_name)
        self.unzipped_modded_folder_path  = os.path.join(directory,"custom_maps_unzipped")
        self.unzipped_modded_file_path    = os.path.join(directory,"custom_maps_unzipped",map_name)
        self.rezipped_folder_path         = os.path.join(directory,"custom_maps")
        self.rezipped_file_path           = os.path.join(directory,"custom_maps",map_name)
        
        self.file_name = map_name
        self.extract()
        self.parse()
        self.get_indcies()
        self.pull_layer_strings()
        self.pull_entity_data()
    
    def extract(self):
        try:
            # Extract files
            command = [
                self.sevenzip_executable,
                'x',  # Extract files with full paths
                '-y',  # Assume Yes on all queries (overwrite files without prompting)
                f'-o{Path(self.unzipped_folder_path)}',  # Output directory
                self.loaded_original_file_path  # The path of the archive to extract
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'{self.loaded_original_file_path} successfully unzipped')

            # Move extracted files to the root of the output directory
            #self.flatten_directory(Path(self.unzipped_file_path))
                
        except subprocess.CalledProcessError:
            print(f'{self.loaded_original_file_path} could not be unzipped')
    
    def parse(self):
        self.file_data = []
        try:
            with open(self.unzipped_file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    self.file_data.append(line)
        except FileNotFoundError:
            print(f"Failed to read {self.unzipped_file_path}")
       
    def get_indcies(self):
        substring_to_find = "LayerTerrain"
        index = None
        for i, item in enumerate(self.file_data):
            if substring_to_find in item:
                index = i
                break
        self.MapThemeLine      = index - 1
        self.LayerTerrainLine  = index + 2
        self.LayerObjectsLine  = index + 8
        self.LayerRoadsLine    = index + 14
        self.LayerZombiesLine  = index + 20
        self.LayerFortressLine = index + 26
        self.LayerPipesLine    = index + 32
        self.LayerBeltsLine    = index + 38
       
    def pull_layer_strings(self):
        pattern = r'<Simple name="Cells" value="(?P<size>256|128)\|(?P=size)\|(?P<data>.+?)" \/>'
       
        self.data_LayerTerrain  = re.search(pattern,self.file_data[self.LayerTerrainLine]).group('data')
        self.data_LayerObjects  = re.search(pattern,self.file_data[self.LayerObjectsLine]).group('data')
        self.data_LayerRoads    = re.search(pattern,self.file_data[self.LayerRoadsLine]).group('data')
        self.data_LayerZombies  = re.search(pattern,self.file_data[self.LayerZombiesLine]).group('data')
        self.data_LayerFortress = re.search(pattern,self.file_data[self.LayerFortressLine]).group('data')
        self.data_LayerPipes    = re.search(pattern,self.file_data[self.LayerPipesLine]).group('data')
        self.data_LayerBelts    = re.search(pattern,self.file_data[self.LayerBeltsLine]).group('data')
       
        self.data_size = int(re.search(pattern,self.file_data[self.LayerTerrainLine]).group('size'))
       
        self.data64_LayerTerrain  = self.base64_map_to_array(self.data_LayerTerrain)
        self.data64_LayerObjects  = self.base64_map_to_array(self.data_LayerObjects)        
        self.data64_LayerRoads    = self.base64_map_to_array(self.data_LayerRoads)        
        self.data64_LayerZombies  = self.base64_map_to_array(self.data_LayerZombies)      
        self.data64_LayerFortress = self.base64_map_to_array(self.data_LayerFortress)      
        self.data64_LayerPipes    = self.base64_map_to_array(self.data_LayerPipes)  
        self.data64_LayerBelts    = self.base64_map_to_array(self.data_LayerBelts)
       
        self.layers = [ self.data64_LayerTerrain,                          
                        self.data64_LayerObjects,        
                        self.data64_LayerRoads,        
                        self.data64_LayerZombies,      
                        self.data64_LayerFortress,        
                        self.data64_LayerPipes,    
                        self.data64_LayerBelts]
   
    def push_layer_strings(self):
        #Takes edited layers in gui and pushes it back to the file data inside this class
        start_pattern = '<Simple name="Cells" value="'
        end_pattern   = '" />'
       
        data64_LayerTerrain = self.array_to_base64_map(self.layers[0])
        data64_LayerObjects = self.array_to_base64_map(self.layers[1])
        data64_LayerZombies = self.array_to_base64_map(self.layers[3])
       
        self.data_LayerTerrain = f'{self.file_data[self.LayerTerrainLine].split(start_pattern,maxsplit = 1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerTerrain}{end_pattern}\n'
        self.data_LayerObjects = f'{self.file_data[self.LayerObjectsLine].split(start_pattern,maxsplit = 1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerObjects}{end_pattern}\n'
        self.data_LayerZombies = f'{self.file_data[self.LayerObjectsLine].split(start_pattern,maxsplit = 1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerZombies}{end_pattern}\n'

        self.file_data[self.LayerTerrainLine] = self.data_LayerTerrain
        self.file_data[self.LayerObjectsLine] = self.data_LayerObjects
        self.file_data[self.LayerZombiesLine] = self.data_LayerZombies
   
    def push_new_cc_pos(self,new_x,new_y):
        start = False
        cc_pos_index = 0
        for index, line in enumerate(self.file_data):
            if '<Complex type="ZX.Entities.CommandCenter' in line:
                start = True
            if start == True:
                if '"Position"' in line:
                    cc_pos_index = index
                    break
        if cc_pos_index != 0:
            temp_front = self.file_data[cc_pos_index].split("Position",maxsplit = 1)[0]
            new_string = f'{temp_front}Position" value ="{new_x};{new_y}" />\n'
            self.file_data[cc_pos_index] = new_string
       
        start = False
        cc_pos_index = 0
        for index, line in enumerate(self.file_data):
            if '<Complex type="ZX.Entities.CommandCenter' in line:
                start = True
            if start == True:
                if '"LastPosition"' in line:
                    cc_pos_index = index
                    break
               
        if cc_pos_index != 0:
            temp_front = self.file_data[cc_pos_index].split("LastPosition",maxsplit = 1)[0]
            new_string = f'{temp_front}LastPosition" value ="{new_x};{new_y}" />\n'
            self.file_data[cc_pos_index] = new_string

    def pull_entity_data(self):
        self.entities  = {}
        current_entity = ""
        start = False
        complex_count = 0
        for index,line in enumerate(self.file_data):
            #Start Stop Conditions
            if "<Items>"in line:
                start = True
            if '<Complex name="Extension" type="ZX.GameSystems.ZXLevelExtension, TheyAreBillions">' in line:
                break
            #Main loop
            if start == True:
                #keep track of where you are data wise
                if '<Complex'  in line:
                    if complex_count == 0:
                        self.entities[index] = {}
                        current_entity = index
                    complex_count += 1
                elif '</Complex>' in line:
                    complex_count -= 1
                   
                #type checking
                if current_entity and '<Complex type="ZX.Components.CRailWay'in line:
                    self.entities[current_entity]["isRailway"] = True
                elif '<Complex type="ZX.Entities.CommandCenter' in line:
                   self.entities[current_entity]["isCommandCenter"] = True    
               
                #data grabbing
                if current_entity and '<Simple name=' in line:
                    simplenameid = line.split('<Simple name=')[1]
                    simplenameid, value = simplenameid.split('value="',maxsplit = 1)
                    simplenameid = simplenameid.strip().replace('"','')
                    if " />" in value:
                        value = value.split(" />")[0]
                       
                    if "Position" in simplenameid:
                        valuex,valuey = value.split(";",maxsplit = 1)
                        self.entities[current_entity]["valuey"] = float(valuex.replace('"',''))
                        self.entities[current_entity]["valuex"] = float(valuey.replace('"',''))
                    self.entities[current_entity][simplenameid] = value.strip().replace('"','')
        if DEBUG:
            with open('C:/Users/Josh/Desktop/MODS/Scripts/Entities.json', 'w') as f:
                json.dump(self.entities, f, indent=4)
       
    def write_to_file(self,file_path):
       try:
          with open(file_path, 'x') as file:
              for i in range(len(self.file_data)):
                  file.writelines(self.file_data[i])
                 
       except Exception as e:
          print(f"Error writing to file: {e}")
       
    def base64_map_to_array(self,data):
        # Decode the Base64 encoded data
        decoded_data = base64.b64decode(data)
        # Prepare the output array
        output_array = []
        # Iterate through the decoded data, 4 bytes at a time (since we're dealing with 32-bit unsigned integers)
        for i in range(0, len(decoded_data), 4):
            # Unpack the 4 bytes into a 32-bit unsigned integer (little-endian)
            # and append it to the output array
            int_val = int.from_bytes(decoded_data[i:i+4], byteorder='little')
            output_array.append(int_val)
       
        return output_array
   
    def array_to_base64_map(self, data_array):
        # Prepare the bytes object
        bytes_data = bytes()
        # Iterate through the data array, converting each integer into 4 bytes (32-bit unsigned integer)
        for int_val in data_array:
            bytes_data += int_val.to_bytes(4, byteorder='little')
       
        # Encode the bytes object into a Base64 string
        encoded_data = base64.b64encode(bytes_data)
       
        # Convert bytes to string for easier use in Python (assuming UTF-8 encoding)
        encoded_str = encoded_data.decode('utf-8')
       
        return encoded_str

    def zip_files_with_7zip(self,file_path,path_to_save_to):
        # Set the path to the 7zip executable
        # Adjust the path based on your installation
        command = [
            sevenzip_executable,
            'a',  
            '-tzip',
            '-mx9',
            path_to_save_to,
            file_path  ]
        try:
            subprocess.run(command, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Error compressing file '{self.unzipped_modded_file_path}': {e}")
           
        print(f'{self.file_name} Successfully Rezipped')

class UI_Bar:
    def __init__(self,game):
        self.game = game
        
class MapDraw:
    def __init__(self,gameclass):
        self.game_handler = gameclass
        
    def map_array_to_image(self, data_array, color_dict, color_default=(0, 0, 0)):
        for y in range(self.game_handler.data_size):
            for x in range(self.game_handler.data_size):
                map_pos = self.game_handler.data_size * y + x
                the_number = data_array[map_pos]
                the_var = color_dict.get(the_number, "None")
                
                if self.game_handler.redraw_spirtes and the_var in self.game_handler.zombie_sprite_holder:
                    temp = TestSprite(self.game_handler.zombie_sprite_holder[the_var].final_image,x * self.game_handler.cell_size - self.game_handler.x_mapoffset,y * self.game_handler.cell_size - self.game_handler.y_mapoffset)
                    self.game_handler.sprite_zombies.add(temp)
                    
                elif the_var != "None" and the_var != "ZombieNone":
                    the_color = colors.get(the_var, color_default)
                    # Adjust draw position by scroll offsets
                    pygame.draw.rect(self.game_handler.screen, the_color, pygame.Rect(x * self.game_handler.cell_size - self.game_handler.x_mapoffset, y * self.game_handler.cell_size - self.game_handler.y_mapoffset, self.game_handler.cell_size, self.game_handler.cell_size))

class YourGameClass:
    def __init__(self, current_map, directory, sevenzip_executable):
        pygame.init()
        
        self.sevenzip_executable = sevenzip_executable
        self.dir = Path(directory) 
        self.file_path = directory
        
        self.custom_map_path = Path(directory, "custom_maps")
        self.write_path = Path(directory, "custom_maps_unzipped")
        
        self.map_path = "NA"
        self.current_map = current_map
        self.data_size  = current_map.data_size
        self.ui_width = 150
        self.init_scrollbar_vars()
        self.screen = pygame.display.set_mode((self.data_size*5 + self.scrollbar_width +self.ui_width, self.data_size*5 + self.scrollbar_width), pygame.RESIZABLE)  # Added width for checkboxes
        self.init_toolbar_vars()
        self.define_ui()
        self.init_coniditions()
        self.init_sprites()
        
    def init_sprites(self):
        self.zombie_sprite_holder = {}
        
        self.sprite_zombies = pygame.sprite.Group()
        for sprite in sprite_dict_zombies.keys():
            temp = ImageHandler(    sprite_dict_zombies[sprite]["path"],
                                    sprite_dict_zombies[sprite]["x1"],
                                    sprite_dict_zombies[sprite]["y1"],
                                    sprite_dict_zombies[sprite]["x2"],
                                    sprite_dict_zombies[sprite]["y2"],
                                    sprite_dict_zombies[sprite].get("scale_x",1),
                                    sprite_dict_zombies[sprite].get("scale_y",1),
                                    self.cell_size,                        # map cell size in pixels
                                    sprite_dict_zombies[sprite].get("cell_size",1),# number of squares object ocupies 3 would be 3x3
                                    )
            
            self.zombie_sprite_holder[sprite] = temp
            
    def init_scrollbar_vars(self):
        self.scrollbar_width = 30
        self.x_mapoffset = 0
        self.y_mapoffset = 0
   
    def set_map(self):
        def open_file_dialog():
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            file_path = filedialog.askopenfilename(initialdir=self.custom_map_path)
            if file_path:
                print("Selected file:", file_path)
            root.destroy()
            return file_path
        
        selected_file_path = open_file_dialog()
        if selected_file_path:
            self.file_name = os.path.basename(selected_file_path)
            self.file_path = os.path.dirname(selected_file_path)
            
            self.current_map = map(self.file_path,self.file_name,sevenzip_executable)
            self.data_size   = self.current_map.data_size
            self.data64_LayerTerrain = self.current_map.layers[0]
            self.data64_LayerObjects = self.current_map.layers[1]
            self.data64_LayerZombies = self.current_map.layers[3]
            self.all_entities        = self.current_map.entities
   
    def define_scroll_bars(self):
        
        cell_size = int(5 * (self.zoom_level / 100.0))
        total_size = cell_size * self.data_size
       
        self.tbmanager= pygame_gui.UIManager((self.screen.get_width() + 100, self.screen.get_height() * 5))
       
        x_current_size = self.screen.get_width()- self.ui_width - self.scrollbar_width
        y_current_size = self.screen.get_height()- self.scrollbar_width

        x_ratio = x_current_size / total_size
        y_ratio = y_current_size / total_size
       
        self.x_slider = pygame_gui.elements.UIHorizontalScrollBar(
            relative_rect=pygame.Rect(
                (0, self.screen.get_height() - self.scrollbar_width),  # X starts at 5, Y is screen height - height of scrollbar
                (self.screen.get_width()-self.ui_width-self.scrollbar_width, self.scrollbar_width)  # Width is self.ui_width, height is 30
            ),
            manager=self.tbmanager,
            visible_percentage=x_ratio  # This can be adjusted if not the entire content is visible at once
        )

        # Adjusting the vertical scrollbar
        self.y_slider = pygame_gui.elements.UIVerticalScrollBar(
            relative_rect=pygame.Rect(
                (self.screen.get_width() - self.scrollbar_width - self.ui_width, 0),  # X is screen width - width of scrollbar, Y starts at 0
                (self.scrollbar_width, self.screen.get_height()-self.scrollbar_width)  # Width is 30, Height is the entire height of the screen
            ),
            manager=self.tbmanager,
            visible_percentage=y_ratio  # This means 50% of the content is visible, adjust as needed
        )

    def scroll_bar_handler(self, event):
        if ((event.ui_element == self.x_slider.sliding_button) or
            (event.ui_element == self.x_slider.left_button) or
            (event.ui_element == self.x_slider.right_button)):
            self.sprite_zombies = pygame.sprite.Group()
            startx_pos = self.x_slider.visible_percentage * self.x_slider.right_limit
            self.x_mapoffset = int(self.x_slider.scroll_position) + startx_pos
            x_current_size = self.screen.get_width()- self.ui_width - self.scrollbar_width
            current_bar_pos = int(self.x_slider.visible_percentage * self.x_slider.scroll_position)
            bar_max_pos =  int((self.x_slider.right_limit - startx_pos)*self.x_slider.visible_percentage)
           
            if bar_max_pos != 0:
                self.data_size  
                self.bar_percentage         = (current_bar_pos / bar_max_pos)
                number_potential_cells_displayed = x_current_size / self.cell_size
                number_potential_cells_total = self.data_size
                number_cells_not_displayed = number_potential_cells_total - number_potential_cells_displayed
                self.x_mapoffset = round(((number_cells_not_displayed * self.bar_percentage) * self.cell_size)/self.cell_size) * self.cell_size
            else:
                self.x_mapoffset = 0
           
            return True
        elif ((event.ui_element == self.y_slider.sliding_button) or
            (event.ui_element == self.y_slider.top_button) or
            (event.ui_element == self.y_slider.bottom_button)):
            self.sprite_zombies = pygame.sprite.Group()
            starty_pos = self.y_slider.visible_percentage * self.y_slider.bottom_limit
            self.y_mapoffset = int(self.y_slider.scroll_position) + starty_pos
            y_current_size = self.screen.get_width() - self.scrollbar_width
            current_bar_pos = int(self.y_slider.visible_percentage * self.y_slider.scroll_position)
            bar_may_pos =  int((self.y_slider.bottom_limit - starty_pos)*self.y_slider.visible_percentage)
           
            if bar_may_pos != 0:
                self.data_size  
                self.bar_percentage         = (current_bar_pos / bar_may_pos)
                number_potential_cells_displayed = y_current_size / self.cell_size
                number_potential_cells_total = self.data_size
                number_cells_not_displayed = number_potential_cells_total - number_potential_cells_displayed
                self.y_mapoffset = round(((number_cells_not_displayed * self.bar_percentage) * self.cell_size)/self.cell_size) * self.cell_size
            else:
                self.y_mapoffset = 0
            
            return True
       
    def define_toolbar(self):
        self.layer_objects_options = ''
       
        if self.layer_select_option == 'terrain':
            self.layer_objects_options = [name for key, name in LayerTerrain.items()]
            self.layer_option = 'Earth'
        elif self.layer_select_option == 'objects':
            self.layer_objects_options = [name for key, name in LayerObjects.items()]
            self.layer_option = 'None'
        elif self.layer_select_option == "zombies":
            self.layer_objects_options = [name for key, name in LayerZombies.items()]
            self.layer_option = 'ZombieNone'
       
        self.uimanager              = pygame_gui.UIManager((self.screen.get_width() + 100, self.screen.get_height() * 5))
        self.map_select_dropdown    = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 0), (self.ui_width, 30)),text='Load Map',manager=self.uimanager)
        #self.map_select_dropdown    = pygame_gui.elements.UIDropDownMenu(options_list=self.map_selection_options,starting_option=self.map_selection_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 0), (self.ui_width, 30)),manager=self.uimanager)
        self.terrain_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 40), (self.ui_width, 30)),text='Terrain',manager=self.uimanager)
        self.objects_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 80), (self.ui_width, 30)),text='Objects',manager=self.uimanager)
        self.zombies_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 120), (self.ui_width, 30)),text='Zombies',manager=self.uimanager)
        self.grid_checkbox          = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 160), (self.ui_width, 30)),text='Grid',manager=self.uimanager)
        self.save_button            = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 360), (self.ui_width, 30)),text='Save',manager=self.uimanager)
        self.move_cc                = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 400), (self.ui_width, 30)),text='Move CC',manager=self.uimanager)
        self.select_tt              = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 440), (self.ui_width, 30)),text='TrainTrack',manager=self.uimanager)
        self.entities_checkbox      = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 480), (self.ui_width, 30)),text='Entities',manager=self.uimanager)
        self.zoom_slider            = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 320), (self.ui_width, 30)),start_value=100,value_range=(50, 200),manager=self.uimanager)
        self.layer_select_dropdown  = pygame_gui.elements.UIDropDownMenu(options_list=self.layer_select_options,starting_option=self.layer_select_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 200), (self.ui_width, 30)),manager=self.uimanager)
        self.layer_objects_dropdown = pygame_gui.elements.UIDropDownMenu(options_list=self.layer_objects_options,starting_option=self.layer_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 240), (self.ui_width, 30)),manager=self.uimanager)
        self.brushes_dropdown       = pygame_gui.elements.UIDropDownMenu(options_list=self.brush_options,starting_option=self.brush_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 280), (self.ui_width, 30)),manager=self.uimanager)
       
    def toolbar_button_handler(self,event):
        if event.ui_element == self.terrain_checkbox:
            self.layer_visibility['terrain'] = not self.layer_visibility['terrain']
            return True
        elif event.ui_element == self.objects_checkbox:
            self.layer_visibility['objects'] = not self.layer_visibility['objects']
            return True
        elif event.ui_element == self.zombies_checkbox:
            self.layer_visibility['zombies'] = not self.layer_visibility['zombies']
            return True
        elif event.ui_element == self.grid_checkbox:
            self.layer_visibility['grid'] = not self.layer_visibility['grid']
            return True
        elif event.ui_element == self.save_button:
            self.save_file()
            return True
        elif event.ui_element == self.move_cc:
            if self.move_cc_selected == True:
                self.move_cc_selected = False
            else:
                self.move_cc_selected = True
        elif event.ui_element == self.map_select_dropdown:
            self.on_map_selection_change()
            return True
        else:
            return False
       
    def init_toolbar_vars(self):
        self.layer_visibility      = {'terrain': True,
                                      'objects': True,
                                      'grid' : True,
                                      'zombies':True,
                                      'railroad':True,
                                      'commandcenter':True}
       
        self.map_selection_options =  []
       
        for keys,items in map_dict.items():
            self.map_selection_options.append(keys)
           
        self.map_selection_option  =  'Hidden Valley'
       
        self.layer_select_options  = ['terrain','objects','zombies']
        self.layer_select_option   = 'terrain'
       
        self.brush_options         = ["Single", "Crosshair" , "3x3", "5x5"]
        self.zoom_level            = 100  # Default zoom level
        scale_factor = self.zoom_level / 100.0
        self.cell_size = int(5 * scale_factor) * 2
        
        self.layer_option          = 'None'
        self.brush_option          = 'Single'
        self.move_cc_selected      = False
        self.move_tt_selected      = False
   
    def define_ui(self):
        self.define_toolbar()
        self.define_scroll_bars()
       
    def init_coniditions(self):
        self.mouse_button_held_down = False
        self.current_selected_option = None
       
    def handle_mouse_click(self, position):
        position = (position[0] + (self.x_mapoffset), position[1] + self.y_mapoffset )
        
          # Assuming zoom_level affects cell size
        
        grid_x, grid_y = position[0] //  self.cell_size, position[1] //  self.cell_size
        if not self.move_cc_selected and not self.move_tt_selected:
            self.handle_brush_selection(grid_x,grid_y)
        elif not self.move_tt_selected:
            self.move_command_ceneter(grid_x,grid_y)
        elif not self.move_cc_selected:
            self.select_train_track()
           
    def handle_brush_selection(self,grid_x,grid_y):
        # Determine the brush size
        brush_size = self.brushes_dropdown.selected_option
        brush_offsets = {
            "Single": [(0, 0)],
            "Crosshair": [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)],
            "3x3": [(x, y) for x in range(-1, 2) for y in range(-1, 2)],
            "5x5": [(x, y) for x in range(-2, 3) for y in range(-2, 3)]
        }

        # Check bounds and update the appropriate layer
        selected_option = self.layer_objects_dropdown.selected_option
        for offset in brush_offsets[brush_size]:
            # Calculate the new grid position based on the brush size
            new_grid_x = grid_x + offset[0]
            new_grid_y = grid_y + offset[1]
            # Check bounds for the new grid positions
            if new_grid_x >= self.data_size or new_grid_y >= self.data_size or new_grid_x < 0 or new_grid_y < 0:
                continue  # Skip this iteration if the new grid position is outside the bounds
            # Determine the index in the data array for the new grid position
            index = new_grid_y * self.data_size + new_grid_x
            # Update data based on the type (Terrain, Object, Zombie)
            if selected_option in LayerTerrain.values():
                # Update terrain
                for key, value in LayerTerrain.items():
                    if value == selected_option:
                        self.data64_LayerTerrain[index] = key
                        break
            elif selected_option in LayerObjects.values():
                # Update objects
                for key, value in LayerObjects.items():
                    if value == selected_option:
                        self.data64_LayerObjects[index] = key
                        break
            elif selected_option in LayerZombies.values():
                # Update zombies
                for key, value in LayerZombies.items():
                    if value == selected_option:
                        self.data64_LayerZombies[index] = key
                        break
       
    def handle_events(self, event):
        if event.type == pygame.QUIT:
            return False
       
        if event.type == pygame.VIDEORESIZE:
            self.on_window_resize()
       
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self.toolbar_button_handler(event):
                pass
            elif self.scroll_bar_handler(event):
                pass
           
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.layer_select_dropdown:
                self.on_option_selection_change()
            if event.ui_element == self.map_select_dropdown:
                self.on_map_selection_change()
               
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.zoom_slider:
                self.zoom_level = event.value * 2
                self.define_scroll_bars()
           
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_button_held_down = True
            self.current_selected_option = self.layer_objects_dropdown.selected_option
           
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_button_held_down = False
           
        self.uimanager.process_events(event)
        self.tbmanager.process_events(event)
       
        return True

    def build_image(self):
        clock = pygame.time.Clock()
        running = True
        
        self.Map_Draw = MapDraw(self)
       
        self.data64_LayerTerrain = self.current_map.layers[0]
        self.data64_LayerObjects = self.current_map.layers[1]
        self.data64_LayerZombies = self.current_map.layers[3]
        self.all_entities        = self.current_map.entities
        
        self.redraw_spirtes = True
        self.prev_cell_size = 0
        
        
        while running:
            
            self.cell_size = int(5 * (self.zoom_level / 100.0)) * 2
            self.time_delta = clock.tick(60)/1000.0
            
            
            
            for event in pygame.event.get():
                if not self.handle_events(event):
                    running = False
            if self.mouse_button_held_down:
                # Get current mouse position and update
                mouse_pos = pygame.mouse.get_pos()
                self.handle_mouse_click(mouse_pos)
            
            
            self.screen.fill((255, 255, 255))  # Fill the background with white
            
            #clearing sprites
            self.sprite_zombies = pygame.sprite.Group()
            
            if self.cell_size != self.prev_cell_size:
                self.init_sprites()
                self.prev_cell_size = self.cell_size
            
            if self.layer_visibility['terrain']:
                self.Map_Draw.map_array_to_image(self.data64_LayerTerrain, LayerTerrain)
            
            if self.layer_visibility['objects']:
                self.Map_Draw.map_array_to_image(self.data64_LayerObjects, LayerObjects)
                
            if self.layer_visibility['zombies']:
                self.Map_Draw.map_array_to_image(self.data64_LayerZombies, LayerZombies)
            
            if self.layer_visibility['grid']:  # Check if the grid should be drawn
                self.draw_grid()
                
            if self.layer_visibility['railroad']:
                self.draw_railroad()
                
            if self.layer_visibility['commandcenter']:
                self.draw_command_center()
           
            self.sprite_zombies.draw(self.screen)
            
            self.uimanager.update(self.time_delta)
            self.uimanager.draw_ui(self.screen)
           
            self.tbmanager.update(self.time_delta)
            self.tbmanager.draw_ui(self.screen)
            
            pygame.display.update()
           
    def draw_command_center(self):
        for key, item in self.all_entities.items():
            if "isCommandCenter" in self.all_entities[key]:
                x = self.all_entities[key]["valuex"]
                y = self.all_entities[key]["valuey"]
                if self.all_entities[key]["Size"]:
                    temp = self.all_entities[key]["Size"]
                    tempfront, tempback = temp.split(";", maxsplit=1)
                    tempfront = int(tempfront)  # Convert to int to use in range
                    tempback = int(tempback)    # Convert to int to use in range
                    # Draw a grid of squares based on tempfront and tempback
                    for i in range(tempfront):  # Iterate over tempfront
                        for j in range(tempback):  # Iterate over tempback
                            # Calculate new x and y for each square
                            new_x = x + i - tempfront/2
                            new_y = y + j - tempback/2
                            # Draw the square at the new position
                            pygame.draw.rect(self.screen, (255,192,203), pygame.Rect(new_x * self.cell_size- self.x_mapoffset, new_y * self.cell_size- self.y_mapoffset, self.cell_size, self.cell_size))
   
    def move_command_ceneter(self,x,y):
        self.move_cc_selected = False
        for key, item in self.all_entities.items():
            if "isCommandCenter" in self.all_entities[key]:
                self.all_entities[key]["valuex"] = float(x +.5)
                self.all_entities[key]["valuey"] = float(y +.5)

    def select_train_track(self):
        pass
   
    def draw_dynamic_arrow(self, cell_top_left, direction, color):
        x, y = cell_top_left
        cell_width = self.cell_size
        cell_height = self.cell_size

        # Calculate arrow head size and shaft length dynamically
        arrow_head_length = min(cell_width, cell_height) * 0.5
        shaft_length = min(cell_width, cell_height) * 0.5

        # Mid points of the cell
        mx, my = x + cell_width // 2, y + cell_height // 2

        # Calculate start and end points based on direction
        if direction == 'up':
            start_shaft = (mx, y + cell_height)
            end_shaft = (mx, y + cell_height - shaft_length)
            end_point = (mx, my - shaft_length)

        elif direction == 'down':
            start_shaft = (mx, y)
            end_shaft = (mx, y + shaft_length)
            end_point = (mx, my + shaft_length)

        elif direction == 'left':
            start_shaft = (x + cell_width, my)
            end_shaft = (x + cell_width - shaft_length, my)
            end_point = (mx - shaft_length, my)

        elif direction == 'right':
            start_shaft = (x, my)
            end_shaft = (x + shaft_length, my)
            end_point = (mx + shaft_length, my)

        else:
            return  # Invalid direction

        # Draw the main line of the arrow
        pygame.draw.line(self.screen, color, start_shaft, end_shaft, int(self.cell_size / 5))

        # Compute arrowhead points using trigonometry for directionality
        angle = math.pi / 6  # 30 degrees for arrow head angle
        ux, uy = math.cos(angle), math.sin(angle)

        # Calculate arrowhead points
        if direction == 'up':
            side1 = (end_point[0] + arrow_head_length * uy, end_point[1] + arrow_head_length * ux)
            side2 = (end_point[0] - arrow_head_length * uy, end_point[1] + arrow_head_length * ux)
        elif direction == 'down':
            side1 = (end_point[0] + arrow_head_length * uy, end_point[1] - arrow_head_length * ux)
            side2 = (end_point[0] - arrow_head_length * uy, end_point[1] - arrow_head_length * ux)
        elif direction == 'right':
            side1 = (end_point[0] + arrow_head_length * -ux , end_point[1] + arrow_head_length * uy)
            side2 = (end_point[0] + arrow_head_length * -ux , end_point[1] - arrow_head_length * uy)
        elif direction == 'left':
            side1 = (end_point[0] - arrow_head_length * -ux , end_point[1] - arrow_head_length * uy)
            side2 = (end_point[0] - arrow_head_length * -ux , end_point[1] + arrow_head_length * uy)
        # Draw the arrowhead
        pygame.draw.polygon(self.screen, color, [end_point, side1, side2])
    
    def draw_rail(self, cell_top_left, direction, color):
        x, y = cell_top_left
        cell_width = self.cell_size
        cell_height = self.cell_size

        # Calculate arrow head size and shaft length dynamically
        shaft_length = min(cell_width, cell_height) * 1

        # Mid points of the cell
        mx, my = x + cell_width // 2, y + cell_height // 2

        # Calculate start and end points based on direction
        if direction == 'up':
            start_shaft = (mx, y + cell_height)
            end_shaft = (mx, y + cell_height - shaft_length)

        elif direction == 'down':
            start_shaft = (mx, y)
            end_shaft = (mx, y + shaft_length)

        elif direction == 'left':
            start_shaft = (x + cell_width, my)
            end_shaft = (x + cell_width - shaft_length, my)

        elif direction == 'right':
            start_shaft = (x, my)
            end_shaft = (x + shaft_length, my)

        else:
            return  # Invalid direction

        # Draw the main line of the arrow
        pygame.draw.line(self.screen, color, start_shaft, end_shaft, int(self.cell_size / 5))
    
    def draw_railroad(self):
        railway_type_directions = {"7194251041032460376" : "down",
                                   "2589476676823118189" : 1,
                                   "5720808135500898894" : 2,
                                   "3093433183056323676" : "right"}
   
        for key, item in self.all_entities.items():
            if "isRailway" in self.all_entities[key]:
                if "IDTemplate type=System.UInt64, mscorlib" in self.all_entities[key]:
                    id = self.all_entities[key].get("IDTemplate type=System.UInt64, mscorlib")
                    direction = railway_type_directions.get(id, "up")
                    
                color = (255,255,255)
                x = self.all_entities[key]["valuex"] -1
                y = self.all_entities[key]["valuey"] -1
                if "IsOrigin" in self.all_entities[key]:
                    if self.all_entities[key]["IsOrigin"] == "True":
                        color = (0,0,0)
               
                if self.all_entities[key]["Size"] != "1;1":
                    temp = self.all_entities[key]["Size"]
                    tempfront, tempback = temp.split(";", maxsplit=1)
                    tempfront = int(tempfront)  # Convert to int to use in range
                    tempback = int(tempback)    # Convert to int to use in range
                    if direction == 1:
                        j = tempback
                        for i in range(tempfront):  # Iterate over tempfront
                            #for j in range(tempback):  # Iterate over tempback
                            # Calculate new x and y for each square
                            new_x = (x + i) - tempfront/2 + 1
                            new_y = (y + j) - tempback/2 + 1
                            adjusted_x = (new_x + .5) * self.cell_size - self.x_mapoffset
                            adjusted_y = (new_y - .5) * self.cell_size - self.y_mapoffset
                            # Draw the square at the new position
                            #pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(new_x * self.cell_size - self.x_mapoffset, new_y * self.cell_size - self.y_mapoffset, self.cell_size, self.cell_size))
                            self.draw_rail((adjusted_x,adjusted_y),"right",color)
                        i = 0
                        for j in range(tempback):  # Iterate over tempback
                            # Calculate new x and y for each square
                            new_x = (x + i) - tempfront/2 + 1
                            new_y = (y + j) - tempback/2 + 1
                            adjusted_x = (new_x) * self.cell_size - self.x_mapoffset
                            adjusted_y = (new_y) * self.cell_size - self.y_mapoffset
                            # Draw the square at the new position
                            #pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(new_x * self.cell_size - self.x_mapoffset, new_y * self.cell_size - self.y_mapoffset, self.cell_size, self.cell_size))
                            self.draw_rail((adjusted_x,adjusted_y),"down",color)
                                
                    elif direction == 2:
                        j = 0
                        for i in range(tempfront):  # Iterate over tempfront
                            #for j in range(tempback):  # Iterate over tempback
                            # Calculate new x and y for each square
                            new_x = (x + i) - tempfront/2 + 1
                            new_y = (y + j) - tempback/2 + 1
                            adjusted_x = (new_x + .5) * self.cell_size - self.x_mapoffset
                            adjusted_y = (new_y) * self.cell_size - self.y_mapoffset
                            # Draw the square at the new position
                            #pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(new_x * self.cell_size - self.x_mapoffset, new_y * self.cell_size - self.y_mapoffset, self.cell_size, self.cell_size))
                            self.draw_rail((adjusted_x,adjusted_y),"right",color)
                        i = tempback
                        for j in range(tempback):  # Iterate over tempback
                            # Calculate new x and y for each square
                            new_x = (x + i) - tempfront/2 + 1
                            new_y = (y + j) - tempback/2 + 1
                            adjusted_x = (new_x) * self.cell_size - self.x_mapoffset
                            adjusted_y = (new_y+.5) * self.cell_size - self.y_mapoffset
                            # Draw the square at the new position
                            #pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(new_x * self.cell_size - self.x_mapoffset, new_y * self.cell_size - self.y_mapoffset, self.cell_size, self.cell_size))
                            self.draw_rail((adjusted_x,adjusted_y),"down",color)
                    else:
                        for i in range(tempfront):  # Iterate over tempfront
                            for j in range(tempback):  # Iterate over tempback
                                # Calculate new x and y for each square
                                new_x = (x + i) - tempfront/2 + 1
                                new_y = (y + j) - tempback/2 + 1
                                # Draw the square at the new position
                                pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(new_x * self.cell_size - self.x_mapoffset, new_y * self.cell_size - self.y_mapoffset, self.cell_size, self.cell_size))
                else:
                    adjusted_x = (x+.5) * self.cell_size - self.x_mapoffset
                    adjusted_y = (y+.5) * self.cell_size - self.y_mapoffset
                    
                    self.draw_rail((adjusted_x,adjusted_y),direction,color)
                    #pygame.draw.rect(self.screen, color, pygame.Rect((x+.5) * self.cell_size - self.x_mapoffset, (y+.5) * self.cell_size - self.y_mapoffset, self.cell_size, self.cell_size))
       
    def draw_grid(self):
        # Draw vertical lines
        for x in range(0, (self.data_size * self.cell_size)-int(self.x_mapoffset/self.cell_size), self.cell_size):
            pygame.draw.line(self.screen, (200, 200, 200), (x,0), (x, self.data_size * self.cell_size))

        # Draw horizontal lines
        for y in range(0, (self.data_size * self.cell_size)-int(self.y_mapoffset/self.cell_size), self.cell_size):
            pygame.draw.line(self.screen, (200, 200, 200), (0,y), (self.data_size * self.cell_size, y))
       
    def on_window_resize(self):
        self.layer_option = self.layer_objects_dropdown.selected_option
        self.brush_option = self.brushes_dropdown.selected_option
        
        self.define_ui()
   
    def on_option_selection_change(self):
        self.layer_select_option = self.layer_select_dropdown.selected_option
        self.define_ui()
   
    def on_map_selection_change(self):
        self.set_map()
        self.define_ui()
   
    def save_file(self):
        def open_save_as_dialog(initial_dir):
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            save_file_path = filedialog.asksaveasfilename(initialdir=initial_dir, defaultextension=".dxlevel",
                                                    filetypes=[("Level", "*.dxlevel"), ("All files", "*.*")])
            root.destroy()
            return save_file_path
            
        save_file_path = open_save_as_dialog(self.custom_map_path)
        file_name  = os.path.basename(save_file_path)
        file_path  = os.path.dirname(save_file_path)
        write_path = Path(self.dir,file_name)
        zip_path   = save_file_path
        if save_file_path:
            self.current_map.layers[0] = self.data64_LayerTerrain
            self.current_map.layers[1] = self.data64_LayerObjects
            self.current_map.layers[3] = self.data64_LayerZombies

            for key, item in self.all_entities.items():
                if "isCommandCenter" in self.all_entities[key]:
                    self.current_map.push_new_cc_pos(self.all_entities[key]["valuex"], self.all_entities[key]["valuey"])

            self.current_map.push_layer_strings()
            self.current_map.write_to_file(write_path)
            
            self.current_map.zip_files_with_7zip(write_path,zip_path)

def launch():
    r01         = "R01.dxlevel"
    directory = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/"
    launched_map = map(directory,r01,sevenzip_executable)
    windowclass = YourGameClass(launched_map,directory,sevenzip_executable)
    windowclass.build_image()
    
def launch_from_gui(r01,directory,sevenzip_executable):
    launched_map = map(directory,r01,sevenzip_executable)
    windowclass = YourGameClass(launched_map,directory,sevenzip_executable)
    windowclass.build_image()

if __name__ == '__main__':
    launch()







































