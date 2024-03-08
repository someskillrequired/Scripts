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
              "1130949242559706282":"TruckA",
              "1858993070642015232":"FortressBarLeft",
              "5955209075099213047":"FortressBarRight",
              "2617794739528169237":"TensionTowerMediumFlip",
              "4533866769353242870":"TensionTowerMedium",
              "2342596987766548617":"TensionTowerHighFlip",
              "3359149191582161849":"TensionTowerHigh"}


Ro5         = "R05.dxlevel"
map_path    = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Extracted"
save_path   = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Modded"
zipped_path = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Rezipped"

class map():
    def __init__(self,path,save_path,zipped_path,mapname):
        self.file = os.path.join(path,mapname)
        self.save_path = os.path.join(save_path,mapname)
        self.zipped_file_path =  os.path.join(zipped_path,mapname)
        self.file_name = mapname
        self.parse()
        self.get_indcies()
        self.pull_layer_strings()
        
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
    def __init__(self, map):
        pygame.init()
        self.map = map
        self.data_size = map.data_size
        self.ui_width = 150
        self.screen = pygame.display.set_mode((self.data_size*5 + self.ui_width, self.data_size*5), pygame.RESIZABLE)  # Added width for checkboxes
        self.init_toolbar_vars()
        self.define_toolbar()
        self.init_coniditions()
    
    def define_toolbar(self):
        self.layer_objects_options = ''
        
        if self.layer_select_option == 'terrain':
            self.layer_objects_options = [name for key, name in LayerObjects.items()]
            self.layer_option = 'None'
        elif self.layer_select_option == 'objects':
            self.layer_objects_options = [name for key, name in LayerTerrain.items()]
            self.layer_option = 'Earth'
        elif self.layer_select_option == "zombies":
            self.layer_objects_options = [name for key, name in LayerZombies.items()]
            self.layer_option = 'ZombieNone'
        
        self.manager                = pygame_gui.UIManager((self.screen.get_width() + 100, self.screen.get_height() * 5))
        self.terrain_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 20), (self.ui_width, 30)),text='Terrain',manager=self.manager)
        self.objects_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 60), (self.ui_width, 30)),text='Objects',manager=self.manager)
        self.zombies_checkbox       = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 100), (self.ui_width, 30)),text='Zombies',manager=self.manager)
        self.grid_checkbox          = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 140), (self.ui_width, 30)),text='Grid',manager=self.manager)
        self.save_button            = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 340), (self.ui_width, 30)),text='Save',manager=self.manager)
        self.zoom_slider            = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 300), (self.ui_width, 30)),start_value=100,value_range=(50, 200),manager=self.manager)
        self.layer_select_dropdown  = pygame_gui.elements.UIDropDownMenu(options_list=self.layer_select_options,starting_option=self.layer_select_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 180), (self.ui_width, 30)),manager=self.manager)
        self.layer_objects_dropdown = pygame_gui.elements.UIDropDownMenu(options_list=self.layer_objects_options,starting_option=self.layer_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 220), (self.ui_width, 30)),manager=self.manager)
        self.brushes_dropdown       = pygame_gui.elements.UIDropDownMenu(options_list=self.brush_options,starting_option=self.brush_option,relative_rect=pygame.Rect((self.screen.get_width()-self.ui_width, 260), (self.ui_width, 30)),manager=self.manager)
        
    def init_toolbar_vars(self):
        self.layer_visibility      = {'terrain': True, 'objects': True, 'grid' : True,'zombies':True}  # Example layer visibility dict
        
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

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.scroll_x -= 10  # Scroll left
            elif event.key == pygame.K_RIGHT:
                self.scroll_x += 10  # Scroll right
            elif event.key == pygame.K_UP:
                self.scroll_y -= 10  # Scroll up
            elif event.key == pygame.K_DOWN:
                self.scroll_y += 10  # Scroll down
            
            # Clamp the scroll values to prevent scrolling beyond the map
            self.scroll_x = max(0, min(self.scroll_x, self.max_scroll_x))
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll_y))
        
        self.manager.process_events(event)
        return True

    def build_image(self):
        clock = pygame.time.Clock()
        running = True
        self.data64_LayerTerrain = self.map.layers[0]
        self.data64_LayerObjects = self.map.layers[1]
        self.data64_LayerZombies = self.map.layers[3]
        
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
            
            self.manager.update(self.time_delta)
            self.manager.draw_ui(self.screen)
            pygame.display.update()
    
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
                    pygame.draw.rect(self.screen, the_color, pygame.Rect(x * cell_size - self.scroll_x, y * cell_size - self.scroll_y, cell_size, cell_size))

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
    
    def save_file(self):
        self.map.layers[0] = self.data64_LayerTerrain
        self.map.layers[1] = self.data64_LayerObjects
        self.map.layers[3] = self.data64_LayerZombies
        self.map.push_layer_strings()
        self.map.write_to_file()
        self.map.zip_files_with_7zip()
    
r05 = map(map_path,save_path,zipped_path,Ro5)
windowclass = YourGameClass(r05)
windowclass.build_image()