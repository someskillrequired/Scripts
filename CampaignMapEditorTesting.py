import os
import zipfile
import shutil
import subprocess
import pygame
from PIL import Image, ImageDraw
import copy
import base64
import re
import pygame_gui
import json


BYTES_PER_WORD = 4

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
    "ZombieWeak1": (144, 238, 144),  # Light green
    "ZombieWeak2": (0, 255, 0),      # Lime
    "ZombieWeak3": (0, 128, 0),      # Green
    "ZombieMedium1": (255, 255, 153),  # Light Yellow
    "ZombieMedium2": (255, 255, 0),    # Yellow
    "ZombieMedium3": (204, 204, 0),    # Yellow
    "ZombieStrong1": (255, 165, 0),  # Orange
    "ZombieStrong2": (255, 127, 80), # Coral
    "ZombieStrong3": (255, 69, 0),   # Orange Red
    "ZombiePowerful1": (255, 0, 0),    # Red
    "ZombiePowerful2": (220, 20, 60),  # Crimson
    "ZombieUltra1": (139, 0, 0),  # Dark Red
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

# Formatting the dictionary for better alignment
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
    "The Goddess of Destiny":     "REND.dxlevel"
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

# Let's format it into a string with aligned text
formatted_map_dict = "\n".join([f'"{key}":{value.rjust(30 - len(key))},' for key, value in map_dict.items()])

Ro5         = "R01.dxlevel"
map_path    = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Extracted"
save_path   = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Modded"
zipped_path = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Rezipped"

class map_entities():
    def __init__(self,data,value):
        self.data      = data
        self.unique_id = value
        
class map():
    def __init__(self,path,save_path,zipped_path,mapname):
        self.file = os.path.join(path,mapname)
        self.save_path = os.path.join(save_path,mapname)
        self.zipped_file_path =  os.path.join(zipped_path,mapname)
        self.file_name = mapname
        self.parse()
        self.get_indcies()
        self.pull_layer_strings()
        self.pull_entity_data()
        
    def parse(self):
        self.file_data = []
        try:
            print(self.file)
            with open(self.file, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    self.file_data.append(line)
        except FileNotFoundError:
            print(f"File not found: {self.file}")
        
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
                  
        with open('C:/Users/Josh/Desktop/MODS/Scripts/Entities.json', 'w') as f:
            json.dump(self.entities, f, indent=4)
        
    def write_to_file(self):
       try:
          with open(self.save_path, 'w') as file:
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

    def zip_files_with_7zip(self):
        # Set the path to the 7zip executable
        sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'# Adjust the path based on your installation
        command = [
            sevenzip_executable,
            'a',  
            '-tzip',
            '-mx9',
            self.zipped_file_path, 
            self.save_path  ]
        try:
            subprocess.run(command, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Error compressing file '{self.modded_file_path}': {e}")
            
        print(f'{self.file_name} Successfully Rezipped')

class YourGameClass:
    def __init__(self, current_map):
        pygame.init()
        self.current_map = current_map
        self.data_size  = current_map.data_size
        self.ui_width = 150
        self.screen = pygame.display.set_mode((self.data_size*5 + self.ui_width, self.data_size*5), pygame.RESIZABLE)  # Added width for checkboxes
        self.init_toolbar_vars()
        self.define_toolbar()
        self.init_coniditions()
    
    def set_map(self):
        curent_map_name = self.map_select_dropdown.selected_option
        current_map_readablename     = map_dict[curent_map_name]
        
        current_map= map(map_path,save_path,zipped_path,current_map_readablename)
        
        self.current_map         = current_map
        self.data_size           = current_map.data_size
        self.data64_LayerTerrain = self.current_map.layers[0]
        self.data64_LayerObjects = self.current_map.layers[1]
        self.data64_LayerZombies = self.current_map.layers[3]
        self.all_entities        = self.current_map.entities
    
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
        
        self.manager                = pygame_gui.UIManager((self.screen.get_width() + 100, self.screen.get_height() * 5))
        self.map_select_dropdown    = pygame_gui.elements.UIDropDownMenu(options_list=self.map_selection_options,starting_option=self.map_selection_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 0), (self.ui_width, 30)),manager=self.manager)
        self.terrain_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 40), (self.ui_width, 30)),text='Terrain',manager=self.manager)
        self.objects_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 80), (self.ui_width, 30)),text='Objects',manager=self.manager)
        self.zombies_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 120), (self.ui_width, 30)),text='Zombies',manager=self.manager)
        self.grid_checkbox          = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 160), (self.ui_width, 30)),text='Grid',manager=self.manager)
        self.save_button            = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 360), (self.ui_width, 30)),text='Save',manager=self.manager)
        self.zoom_slider            = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 320), (self.ui_width, 30)),start_value=100,value_range=(50, 200),manager=self.manager)
        self.layer_select_dropdown  = pygame_gui.elements.UIDropDownMenu(options_list=self.layer_select_options,starting_option=self.layer_select_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 200), (self.ui_width, 30)),manager=self.manager)
        self.layer_objects_dropdown = pygame_gui.elements.UIDropDownMenu(options_list=self.layer_objects_options,starting_option=self.layer_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 240), (self.ui_width, 30)),manager=self.manager)
        self.brushes_dropdown       = pygame_gui.elements.UIDropDownMenu(options_list=self.brush_options,starting_option=self.brush_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 280), (self.ui_width, 30)),manager=self.manager)
        
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
        self.layer_option          = 'None'
        self.brush_option          = 'Single'

    
    def init_coniditions(self):
        self.mouse_button_held_down = False
        self.current_selected_option = None
        self.scroll_x = 0  # Horizontal scroll offset
        self.scroll_y = 0  # Vertical scroll offset
        self.max_scroll_x = self.data_size * 5 - self.screen.get_width()  # Maximum horizontal scroll
        self.max_scroll_y = self.data_size * 5 - self.screen.get_height()  # Maximum vertical scroll

        # Make sure maximum scroll values are not negative
        self.max_scroll_x = max(self.max_scroll_x, 0)
        self.max_scroll_y = max(self.max_scroll_y, 0)
        self.drag_start = None   
        
    def handle_mouse_click(self, position):
        position = (position[0] + self.scroll_x, position[1] + self.scroll_y)
        cell_size = int(5 * (self.zoom_level / 100.0))  # Assuming zoom_level affects cell size
        grid_x, grid_y = position[0] // cell_size, position[1] // cell_size

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
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.terrain_checkbox:
                self.layer_visibility['terrain'] = not self.layer_visibility['terrain']
            elif event.ui_element == self.objects_checkbox:
                self.layer_visibility['objects'] = not self.layer_visibility['objects']
            elif event.ui_element == self.zombies_checkbox:
                self.layer_visibility['zombies'] = not self.layer_visibility['zombies']
            elif event.ui_element == self.grid_checkbox:
                self.layer_visibility['grid'] = not self.layer_visibility['grid']
            elif event.ui_element == self.save_button:
                self.save_file()
                    
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.layer_select_dropdown:
                self.on_option_selection_change()
            if event.ui_element == self.map_select_dropdown:
                self.on_map_selection_change()
                
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.zoom_slider:
                self.zoom_level = event.value
                
        elif event.type == pygame.VIDEORESIZE:
            self.on_window_resize()
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_button_held_down = True
            self.current_selected_option = self.layer_objects_dropdown.selected_option
            
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_button_held_down = False
            
        self.manager.process_events(event)
        return True

    def build_image(self):
        clock = pygame.time.Clock()
        running = True
        
        self.data64_LayerTerrain = self.current_map.layers[0]
        self.data64_LayerObjects = self.current_map.layers[1]
        self.data64_LayerZombies = self.current_map.layers[3]
        self.all_entities        = self.current_map.entities
        
        while running:
            self.time_delta = clock.tick(60)/1000.0
            for event in pygame.event.get():
                if not self.handle_events(event):
                    running = False
            if self.mouse_button_held_down:
                # Get current mouse position and update
                mouse_pos = pygame.mouse.get_pos()
                self.handle_mouse_click(mouse_pos)
                    
            self.screen.fill((255, 255, 255))  # Fill the background with white
            if self.layer_visibility['terrain']:
                self.map_array_to_image(self.data64_LayerTerrain, LayerTerrain)
            if self.layer_visibility['objects']:
                self.map_array_to_image(self.data64_LayerObjects, LayerObjects)
            if self.layer_visibility['zombies']:
                self.map_array_to_image(self.data64_LayerZombies, LayerZombies)
            if self.layer_visibility['grid']:  # Check if the grid should be drawn
                self.draw_grid()
            if self.layer_visibility['railroad']:
                self.draw_railroad()
            if self.layer_visibility['commandcenter']:
                self.draw_command_center()
            
            self.manager.update(self.time_delta)
            self.manager.draw_ui(self.screen)
            pygame.display.update()
    
    def draw_command_center(self):
        scale_factor = self.zoom_level / 100.0
        cell_size = int(5 * scale_factor)
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
                            pygame.draw.rect(self.screen, (255,192,203), pygame.Rect(new_x * cell_size, new_y * cell_size, cell_size, cell_size))

    def draw_railroad(self):
        scale_factor = self.zoom_level / 100.0
        cell_size = int(5 * scale_factor)
        for key, item in self.all_entities.items():
            if "isRailway" in self.all_entities[key]:
                x = self.all_entities[key]["valuex"] -1
                y = self.all_entities[key]["valuey"] -1
                if self.all_entities[key]["Size"] != "1;1":
                    temp = self.all_entities[key]["Size"]
                    tempfront, tempback = temp.split(";", maxsplit=1)
                    tempfront = int(tempfront)  # Convert to int to use in range
                    tempback = int(tempback)    # Convert to int to use in range
                    
                    for i in range(tempfront):  # Iterate over tempfront
                        for j in range(tempback):  # Iterate over tempback
                            # Calculate new x and y for each square
                            new_x = (x + i) - tempfront/2 + 1
                            new_y = (y + j) - tempback/2 + 1
                            # Draw the square at the new position
                            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(new_x * cell_size, new_y * cell_size, cell_size, cell_size))
                else:
                    pygame.draw.rect(self.screen, (255,255,255), pygame.Rect((x+.5) * cell_size, (y+.5) * cell_size, cell_size, cell_size))
        
    def map_array_to_image(self, data_array, color_dict, color_default=(0, 0, 0)):
        scale_factor = self.zoom_level / 100.0  # Calculate scale factor based on zoom level
        cell_size = int(5 * scale_factor)  # Apply scale factor to cell size

        for y in range(self.data_size):
            for x in range(self.data_size):
                map_pos = self.data_size * y + x
                the_number = data_array[map_pos]
                the_var = color_dict.get(the_number, "None")
                if the_var != "None" and the_var != "ZombieNone":
                    the_color = colors.get(the_var, color_default)
                    # Adjust draw position by scroll offsets
                    pygame.draw.rect(self.screen, the_color, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
                    
    def draw_grid(self):
        scale_factor = self.zoom_level / 100.0
        cell_size = int(5 * scale_factor)  # Adjust cell size based on zoom level

        # Draw vertical lines
        for x in range(0, self.data_size * cell_size, cell_size):
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, self.data_size * cell_size))

        # Draw horizontal lines
        for y in range(0, self.data_size * cell_size, cell_size):
            pygame.draw.line(self.screen, (200, 200, 200), (0, y), (self.data_size * cell_size, y))
        
    def on_window_resize(self):
        self.layer_option = self.layer_objects_dropdown.selected_option
        self.brush_option = self.brushes_dropdown.selected_option
        self.define_toolbar()
    
    def on_option_selection_change(self):
        self.layer_select_option = self.layer_select_dropdown.selected_option
        self.define_toolbar()
    
    def on_map_selection_change(self):
        self.map_selection_option = self.map_select_dropdown.selected_option
        self.set_map()
    
    def save_file(self):
        self.current_map.layers[0] = self.data64_LayerTerrain
        self.current_map.layers[1] = self.data64_LayerObjects
        self.current_map.layers[3] = self.data64_LayerZombies
        self.current_map.push_layer_strings()
        self.current_map.write_to_file()
        self.current_map.zip_files_with_7zip()
    
r05 = map(map_path,save_path,zipped_path,Ro5)
windowclass = YourGameClass(r05)
windowclass.build_image()