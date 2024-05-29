
import os
import zipfile
import shutil
import subprocess
import pygame
from PIL import Image, ImageDraw
import copy
import base64

strings = """ZXCampaign.dat	1688788812-163327433-2005584771
             ZXCampaignStrings.dat	-831217260-1747352550571668361
             ZXRules.dat	1435525863-7828404698500055911435525863-782840469850005591334454FADSFASDF45345
             ZXStrings.dat	1435525863-7828404698500055911435525863-782840469850005591334454FADSFASDF45345"""

#folder location
folder_path_clean   = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Clean"
folder_path_extract = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Extracted"
folder_path_modded  = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Modded"
folder_path_zipped  = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Rezipped"
folder_path_base    = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/"
R01_path            = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Levels/Modded/R06.dxlevel"
rules_path          = "D:/SteamLibrary/steamapps/common/They Are Billions/ZXRules/ZXRules.dat"

# Edit Map List
FileNames = ["R06.dxlevel"]

class file_helper(): 
    def __init__(self,FileNames,folder_path_clean,folder_path_extract,folder_path_modded,folder_path_zipped):
        #defining locations
        self.folder_path_clean   = folder_path_clean
        self.folder_path_extract = folder_path_extract
        self.folder_path_modded  = folder_path_modded
        self.folder_path_zipped  = folder_path_zipped
        self.FileNames           = FileNames
        self.maplist             = []
        #Clean all locations upon class definition
        self.clean(self.folder_path_extract)
        self.clean(self.folder_path_modded)
        self.clean(self.folder_path_zipped)
        
        #Extract all data to new location after clean
        self.extract_dxlevel_files()
        
        #Copy data
        self.copy_files()
        
        self.get_map_list()
  
    def clean(self,folder_path):
        try:
            # List all files in the folder
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

            # Delete each file
            for file in files:
                file_path = os.path.join(folder_path, file)
                os.remove(file_path)

            print(f"All files in '{folder_path}' deleted.")
        except Exception as e:
            print(f"Error deleting files: {e}")
            
    def extract_dxlevel_files(self):
        os.makedirs(self.folder_path_extract, exist_ok=True)
        for root, dirs, files in os.walk(self.folder_path_clean):
            for file in files:
                #if file in self.FileNames:
                    #if file.endswith("R05.dxlevel"):
                        try:
                            file_path = os.path.join(root, file)
                            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                zip_ref.extractall(self.folder_path_extract)
                        except Exception as e:
                            print(f"Error extracting file '{file}': {e}")
                            
    def copy_files(self):
        #copy clean files over
        try:
            os.makedirs(self.folder_path_modded, exist_ok=True)
            for item in os.listdir(self.folder_path_extract):
                source_item = os.path.join(self.folder_path_extract, item)
                destination_item = os.path.join(self.folder_path_modded, item)
                if os.path.isfile(source_item):
                    shutil.copy2(source_item, destination_item)
        except Exception as e:
            print(f"Error copying files: {e}")
    
    def get_map_list(self):
         for root, dirs, files in os.walk(self.folder_path_modded):
            for file in files:
                if file.endswith(".dxlevel"):
                    self.maplist.append(root+"/"+file)
                    
    def return_maplist(self):
        return self.maplist
        
    def zip_files_with_7zip(self):
        os.makedirs(self.folder_path_zipped, exist_ok=True)
        # Set the path to the 7zip executable
        sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'# Adjust the path based on your installation

        for root, dirs, files in os.walk(self.folder_path_modded):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file_path = os.path.join(self.folder_path_zipped, f"{os.path.splitext(file)[0]}.dxlevel")
                command = [
                    sevenzip_executable,
                    'a',  
                    '-tzip',
                    '-mx9',
                    zip_file_path, 
                    file_path  ]
                try:
                    subprocess.run(command, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error compressing file '{file}': {e}")

class map():
    def __init__(self,file_path):
        self.file_path                 = file_path
        self.file_name                 = os.path.basename(file_path)
        
        self.LayerTerrain              = ""
        self.LayerObjects              = ""
        self.LayerRoads                = ""
        self.LayerZombies              = ""
        self.LayerFortress             = ""
        self.LayerPipes                = ""
        self.LayerBelt                 = ""
        
        self.LayerTerrainLine          = ""
        self.LayerObjectsLine          = ""
        self.LayerRoadsLine            = ""
        self.LayerZombiesLine          = ""
        self.LayerFortressLine         = ""
        self.LayerPipesLine            = ""
        self.LayerBeltsLine            = ""
        
        self.LayerTerraindict          = {'AgAA':'g', 
                                          'AAEA':'E', 
                                          'AAAC':'C', 
                                          'AAIA':'I', 
                                          'AAAF':'F', 
                                          'AAUA':'U', 
                                          'AAAB':'B', 
                                          'BQAA':'V', 
                                          'AAAA':'A', 
                                          'AQAA':'Q'}
        
        self.LayerTerraindictcolor     = {'g':(0, 0, 0), 
                                          'E':(0, 0, 255), 
                                          'C':(0, 0, 0), 
                                          'I':(0, 255, 0), 
                                          'F':(0, 0, 0), 
                                          'U':(0, 0, 0), 
                                          'B':(0, 0, 0), 
                                          'V':(0, 0, 0), 
                                          'A':(255, 255, 255), 
                                          'Q':(0, 0, 0)}
        
        self.begining_splits           = ['128|128|','256|256']
        self.end_split                 = '==" />'
        self.file_data                 = []
        self.map_size                  = ""
        
        self.Bthemesplit               = '"ThemeType" value="'
        self.Ethemesplit               = '" />'
        self.MapTheme                  = ""
        self.themes                    =["FA","BR","TM","AL","DS","VO"]
        
        self.imagesettings = [(512, 512),4,8018]
        self.transposeX = 1
        self.transposeY = 1
        self.xoffset = 0
        self.yoffset = 1
        
        self.runner()
    
    def set_map_theme(self,theme):
        if theme in self.themes:
          self.MapTheme = theme
          if self.Bthemesplit in self.MapTheme:
              layer = layer.split(self.Bthemesplit,1)[1]
              layer = layer.split(self.Ethemesplit)[0]
          
      
    def runner(self):
        self.pull_in_map_data()
        self.parse_map_data()
        self.generate_image()
        
    def pull_in_map_data(self):
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    self.file_data.append(line)
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            
    def parse_map_data(self):
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
        
        self.MapTheme      = self.file_data[self.MapThemeLine]
        self.LayerTerrain  = self.file_data[self.LayerTerrainLine]
        self.LayerObjects  = self.file_data[self.LayerObjectsLine]
        self.LayerRoads    = self.file_data[self.LayerRoadsLine]
        self.LayerZombies  = self.file_data[self.LayerZombiesLine]
        self.LayerFortress = self.file_data[self.LayerFortressLine]
        self.LayerPipes    = self.file_data[self.LayerPipesLine]
        self.LayerBelt     = self.file_data[self.LayerBeltsLine]
        
        self.LayerTerrain = self.split_data_from_line(self.LayerTerrain)
        self.LayerObjects = self.split_data_from_line(self.LayerObjects)
        self.LayerRoads   = self.split_data_from_line(self.LayerRoads)
        self.LayerZombies = self.split_data_from_line(self.LayerZombies)
        self.LayerFortress= self.split_data_from_line(self.LayerFortress)
        self.LayerPipes   = self.split_data_from_line(self.LayerPipes)
        self.LayerBelt    = self.split_data_from_line(self.LayerBelt)
        
        #self.LayerTerrain = self.clear_layer(self.LayerTerrain)
        self.LayerObjects = self.clear_layer(self.LayerObjects)
        self.LayerRoads   = self.clear_layer(self.LayerRoads)
        self.LayerZombies = self.clear_layer(self.LayerZombies)
        self.LayerFortress= self.clear_layer(self.LayerFortress)
        self.LayerPipes   = self.clear_layer(self.LayerPipes)
        self.LayerBelt    = self.clear_layer(self.LayerBelt)
        
        #self.LayerTerrain = self.draw_on_layer( 7060, 7100, self.LayerTerrain)
        #self.LayerTerrain = self.draw_on_layer( 64536+8060, 65536+8060, self.LayerTerrain)
        #Placeholder for editing data
        #Placeholder for editing data
        #Placeholder for editing data
        #Placeholder for editing data
        #Placeholder for editing data
        #Placeholder for editing data
        
        #self.rewrite_layer_back(self.LayerTerrain,self.LayerTerrainLine)
        self.rewrite_layer_back(self.LayerObjects,self.LayerObjectsLine)
        self.rewrite_layer_back(self.LayerRoads,self.LayerRoadsLine)
        self.rewrite_layer_back(self.LayerZombies,self.LayerZombiesLine)
        self.rewrite_layer_back(self.LayerFortress,self.LayerFortressLine)
        self.rewrite_layer_back(self.LayerPipes,self.LayerPipesLine)
        self.rewrite_layer_back(self.LayerBelt,self.LayerBeltsLine)

        self.LayerTerrain = self.LayerTerrain[7103:]
        self.LayerTerrain = self.LayerTerrain[:65536]
        self.byte_array_LayerTerrain = base64.b64decode(self.LayerTerrain)
        #wordcount = len(self.byte_array_LayerTerrain) / 4
        #print(wordcount)
        
        
    def clear_layer(self,layer):
      layer = 'A' * len(layer)
      return layer
        
    def draw_on_layer(self,start,stop,layer):
        
        layer = list(layer)
        for i in range(stop-start):
            layer[i+start] = "I"
        layer = ''.join(layer)
        print(layer)
        return layer
        
        
    def rewrite_layer_back(self,layer,layerline):
      for begining_split in self.begining_splits:
        if begining_split in self.file_data[layerline]:
          temp_begin = self.file_data[layerline].split(begining_split,1)[0]
          self.file_data[layerline] = temp_begin + begining_split + layer + self.end_split + "\n"
          break
    
    def split_data_from_line(self,layer):
      for begining_split in self.begining_splits:
          if begining_split in layer:
              layer = layer.split(begining_split,1)[1]
              layer = layer.split(self.end_split)[0]
              return layer
                
    def return_file_data(self):
      return self.file_data
                
    def generate_image(self):
        self.transposedata = []

        
        #self.transposedata = [self.LayerTerrain[i:i+chunk_size] for i in range(0, len(input_string), chunk_size)]
        self.transposedata = [self.LayerTerrain[i:i+4] for i in range(0, len(self.LayerTerrain), 4)]
        print(set(self.transposedata))
        
        transposedatacolor = []
        #print(set(self.transposedata))
        j = 0
        for i in range(len(self.transposedata)):
          if 'E' in self.transposedata[i]:
            transposedatacolor.append((0,0,255))
            j += 1
          else:
            transposedatacolor.append((0,0,0))
        
        print(j)
        
        grid = [[(0,0,0) for _ in range(129)] for _ in range(129)]

        # Variable to track the current index in data_list
        index = 1

        for row in range(128):
          if index < len(transposedatacolor):
              for col in range(128):
                  if row % 2 == 1:
                    grid[row][col + 1] = transposedatacolor[index]
                  else:
                    grid[row][col] = transposedatacolor[index] 
                  
                  index += 2
          #index += 128  # Skip 128 characters after filling a row

          if index >= len(transposedatacolor):
            break  # Break if data_list is exhausted
        
        self.transposedatacolor = grid
        print((self.transposedatacolor[0][1]))
 
    def save_image(self):
      #self.image.save("image.png")
      pass
        
    def write_terrain_data_to_text_file(self):
      try:
          with open("TerrainData.txt", 'w') as file:
            file.writelines(self.byte_array_LayerTerrain)
                  
      except Exception as e:
          print(f"Error writing to file: {e}")
          
    def display_and_edit_with_pygame(self):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        window_size = self.imagesettings[0]
        screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption('Interactive Terrain Map')
        counter = 0
        # Main loop
        running = True
        while running:
            
            if counter == 0:
              self.draw_terrain(screen)
              counter =1
              
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == (pygame.K_UP):
                        self.yoffset = max(0, self.yoffset - 1)
                    elif event.key == (pygame.K_DOWN):
                        self.yoffset += 1
                    elif event.key == (pygame.K_LEFT):
                        self.xoffset = max(0, self.xoffset - 1)
                    elif event.key == (pygame.K_RIGHT):
                        self.xoffset += 1
                    elif event.key == (pygame.K_w):
                        self.transposeY = max(1, self.transposeY - 1)
                        print(self.transposeY)
                    elif event.key == (pygame.K_s):
                        self.transposeY += 1
                        print(self.transposeY)
                    elif event.key == (pygame.K_a):
                        self.transposeX = max(1, self.transposeX - 1)
                    elif event.key == (pygame.K_d):
                        self.transposeX += 1
                    self.draw_terrain(screen)  # Call draw_terrain after the value changes

            # Update the display
            pygame.display.flip()

        # Quit Pygame
        pygame.quit()

    def draw_terrain(self, screen):
      screen.fill((0, 0, 0))
      cell_size = 4
      angle = 45  # Rotation angle

      # Create a surface to draw a single rectangle
      rect_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
      rotated_rect_surface = pygame.Surface((cell_size*2 , cell_size *2), pygame.SRCALPHA)  # Larger surface for rotated rectangle
      x = 0
      for i in range(self.xoffset, len(self.transposedatacolor), self.transposeX):
          for j in range(self.yoffset, len(self.transposedatacolor[i]), self.transposeY):
              color = self.transposedatacolor[i][j]
              # Draw the rectangle on the temporary surface
              
              rect_surface.fill(color)
              
              if color == (0,0,255):
                x+=1
              # Clear the rotated surface
              rotated_rect_surface.fill((0, 0, 0, 0))
              # Rotate the rectangle surface
              rotated_surface = pygame.transform.rotate(rect_surface, angle)
              # Get the new rect to center the rotated surface
              new_rect = rotated_surface.get_rect(center=(cell_size, cell_size))
              rotated_rect_surface.blit(rotated_surface, new_rect.topleft)

              # Calculate position for the rotated rectangle
              x_pos = (i / self.transposeX) * cell_size
              y_pos = (j / self.transposeY) * cell_size
              # Blit the rotated rectangle surface onto the main screen
              screen.blit(rotated_rect_surface, (x_pos, y_pos), new_rect)

    def draw_terrain_2(self, screen):
      screen.fill((0, 0, 0))
      cell_size = 8
      counter = 0
      for i in range(len(self.transposedatacolor)):
          for j in range(len(self.transposedatacolor[i])):
              counter += 1
              pygame.draw.rect(screen, self.transposedatacolor[i][j], (i * cell_size, j * cell_size, cell_size, cell_size))
      
    def write_modification(self):
       try:
          with open(self.file_path, 'w') as file:
              for i in range(len(self.file_data)):
                  file.writelines(self.file_data[i])
                  
       except Exception as e:
          print(f"Error writing to file: {e}")

class rules():
  def __init__(self,path):
    self.path = path
  
  def extract_dxlevel_files(self):
      os.makedirs(self.folder_path_extract, exist_ok=True)
      for root, dirs, files in os.walk(self.folder_path_clean):
          for file in files:
              #if file in self.FileNames:
                  if file.endswith(".dxlevel"):
                      try:
                          file_path = os.path.join(root, file)
                          with zipfile.ZipFile(file_path, 'r') as zip_ref:
                              zip_ref.extractall(self.folder_path_extract)
                      except Exception as e:
                          print(f"Error extracting file '{file}': {e}")
    
      
mapdata = file_helper(FileNames,folder_path_clean,folder_path_extract,folder_path_modded,folder_path_zipped)
maplist = mapdata.return_maplist()
map1 = map(maplist[0])
map1.set_map_theme("DS")
map1.write_modification()
map1.display_and_edit_with_pygame()
mapdata.zip_files_with_7zip()