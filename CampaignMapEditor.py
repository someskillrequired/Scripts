import os
import subprocess
import base64
import re
import json
from datetime import datetime
from pathlib import Path
import sys
import numpy as np
import utilities.entitynames as entitynames
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QGroupBox, QCheckBox, QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox,
    QPushButton, QVBoxLayout, QWidget, QSlider, QComboBox, QLabel, QGraphicsPixmapItem,
    QTabWidget, QSpacerItem, QHBoxLayout, QLineEdit, QLabel, QSizePolicy, QTextEdit, QSplitter, QMenu,QMenuBar,QAction,QGraphicsEllipseItem
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QKeySequence
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtOpenGL import QGLWidget
from utilities.sprite_definitions import dict_zombies, dict_entities
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QShortcut
from PIL import Image, ImageEnhance
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap

DEBUG = True

BYTES_PER_WORD = 4
starting_zoom_level = 100
starting_cell_size = int(5 * (starting_zoom_level / 100.0))

help_str = """
Entity Selection:
Switch To Entity Tab
Use the Cursor to Select Entity
Entity will have red box outlining it
Once an Entity has been selected it can then be
Deleted: Deletes Entity
Updated: Using the entry box can completely customize anything availible as this data will be inserted into the game data. Can be used for fine adjusting of position as well as changing entity size
Moved: Use the keyboard arrow keys to move the entity or use keys in combonination with cntrl and or alt to move it more for fine adjustment below one cell size use update method

For Adding New Entities select the entity you want to add from the drop down menu
Once correct entity has been selected click on add entity
This will allow you to click anywhere on the map to add an entity
Deselect Add Entity when done

Railways:
All Railways are entities
Have to use the corner piece to change the train direction which are 6x6 cells called RailWayArc90
Need to use terminator for both start location as well as end location
Need to adjust terminator for start location to also have its entity data updated so it is <Simple name="IsOrigin" value="True" />
Use RailWayCellH and RailWayCellV for going horizontal and veritically

Zombies:
Zombie layer does not contain giants and mutants those need to be added in the entities
Although giants that are not visible on minimap can be added to that layer

Extra Tab is in beta currently used for 'Upscaling Map Size' currently this requires manual intervention to allow the campaign to load it
You will also need to manually unzip ZXGame.dxprj and edit the NCELLS to match the new size as well as rezip and put it back where it needs to go.

Map Saves are Located at game directory ZXGame_Data\Levels

Hidden Valley                R01.dxlevel
The Crossroads               R02.dxlevel
The Hunters Meadow           R03.dxlevel
The Mines of the Raven       R04.dxlevel
The Coast of Bones           R05.dxlevel
The Narrow Pass              R06.dxlevel
The Lowlands                 R07.dxlevel
Cape Storm                   R08.dxlevel
The Lands of the Giant       R09.dxlevel
The Frozen Lake              R10.dxlevel
The Lonely Forest            R11.dxlevel
The Nest of the Harpy        R12.dxlevel
The Valley of Death          R13.dxlevel
The Noxious Swamp            R14.dxlevel
The Oasis                    R15.dxlevel
The Villa of Terror          R16.dxlevel
The Resistance               R17.dxlevel
The Broken Land              R18.dxlevel
El Dorado                    R19.dxlevel
The Forbidden Forest         R20.dxlevel
The Wasteland of the Giants  R21.dxlevel
The Highlands                R22.dxlevel
The Goddess of Destiny       REND.dxlevel

"""

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
    "Nothing?":(0,0,0),
    "unknown2":(0,0,0),
    "tall_barrier":(0,0,0),
    "tall_barrier_spiked":(0,0,0),
    "short_barrier_spiked":(0,0,0),
    "pylon":(0,0,0),
    "pylon_light1":(0,0,0),
    "door":(255,0,0),
    "pylon_light2":(0,0,0),
    "rubble":(0,0,0),
    "unknown10":(0,0,0),
    "tube":(0,0,0),
    "tubew/vent":(0,0,0),
    "right_elbow":(0,0,0),
    "y_top":(0,0,0),
    "vent":(0,0,0),
    "blower":(0,0,0),
    "belt":(0,0,0),
    "beltendpoint":(0,0,0),
    "unknown19":(0,0,0),
    "unknown20":(0,0,0),
}

LayerTerrain = {
    0: "None",
    1: "Water",
    2: "Grass",
    3: "Sky",
    4: "Abyse"
}

LayerRoads = {
    0: "None",
    1: "Nothing?",
    2: "Unknown2",
}

LayerObjects = {
    0: "None",
    1: "Mountain",
    2: "Wood",
    3: "Gold",
    4: "Stone",
    5: "Iron"
}

LayerZombies = {
    0: "ZombieNone",
    1: "walker1",
    2: "walker2",
    3: "walker3",
    4: "runner1",
    5: "runner2",
    6: "runner3",
    7: "medium1",
    8: "medium2",
    9: "medium3",
    10: "Strong1",
    11: "Strong2",
    12: "Strong3",
    13: "Powerful1",
    14: "Powerful2",
    15: "Ultra", #Giant
    16: "Harpies1",
    17: "Harpies2", 
    18: "Harpies3",
    19: "Venoms1",
    20: "Venoms2",
    21: "Venoms3",
    22: "Chubbies1",
    23: "Chubbies2",
    24: "Chubbies3"
}

LayerFortress = {
    0: "None",
    1: "tall_barrier",
    2: "tall_barrier_spiked",
    3: "short_barrier_spiked",
    4: "pylon",
    5: "pylon_light1",
    6: "door",
    7: "pylon_light2",
    8: "rubble",
}

LayerPipes = {
    0: "None",
    1: "tube",
    2: "tubew/vent",
    3: "right_elbow",
    4: "y_top",
    5: "vent",
    6: "blower1",
    7: "blower2",
}

LayerBelts = {
    0: "None",
    1: "belt",
    2: "beltendpoint",
}

def invert_layer_dict(layer):
    inverted = {value: key for key, value in layer.items()}
    return inverted

def weighted_random_choice(weighted_dict):
    keys = list(weighted_dict.keys())  # Extract keys (names)
    weights = list(weighted_dict.values())  # Extract corresponding weights
    
    return random.choices(keys, weights=weights, k=1)[0]

inverted_LayerTerrain = invert_layer_dict(LayerTerrain)
inverted_LayerRoads = invert_layer_dict(LayerRoads)
inverted_LayerObjects = invert_layer_dict(LayerObjects)
inverted_LayerZombies = invert_layer_dict(LayerZombies)
inverted_LayerFortress = invert_layer_dict(LayerFortress)
inverted_LayerPipes = invert_layer_dict(LayerPipes)
inverted_LayerBelts = invert_layer_dict(LayerBelts)

class MultiSelectComboBox(QComboBox):
    def __init__(self,items):
        super().__init__()

        # Allow text editing to display selected items
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.lineEdit().setReadOnly(True)  # Prevent manual text editing

        # Create a model for checkable items
        self.model = QStandardItemModel(self)
        self.setModel(self.model)

        # Add checkable items
        items = []
        for item in items:
            list_item = QStandardItem(item)
            list_item.setCheckable(True)
            list_item.setCheckState(Qt.Unchecked)  # Ensure checkboxes are shown
            self.model.appendRow(list_item)

        # Detect when an item is clicked and manually toggle the checkbox
        self.view().pressed.connect(self.toggle_item)

        # Initialize the displayed text
        self.update_display_text()

    def addItems(self,items):
        for item in items:
            list_item = QStandardItem(item)
            list_item.setCheckable(True)
            list_item.setCheckState(Qt.Unchecked)  # Ensure checkboxes are shown
            self.model.appendRow(list_item)
    
    def toggle_item(self, index):
        """Toggle the check state of the selected item."""
        item = self.model.itemFromIndex(index)
        item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)
        self.update_display_text()

    def update_display_text(self):
        """Update the displayed text with selected items."""
        selected_items = [
            self.model.item(i).text() for i in range(self.model.rowCount()) if self.model.item(i).checkState() == Qt.Checked
        ]
        self.setEditText(", ".join(selected_items) if selected_items else "Select options")
    
    def get_checked_items(self):
        """Retrieve a list of all checked items."""
        return [
            self.model.item(i).text()
            for i in range(self.model.rowCount())
            if self.model.item(i).checkState() == Qt.Checked
        ]

class ImageHandler:
    def __init__(self, file, x1, y1, x2, y2, scale_x, scale_y=False, pixels_cell_size=5, cell_size=1, rotate=0):
        self.file = file
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.pixels_cell_size = pixels_cell_size
        self.cell_size = cell_size
        self.scale_x = scale_x
        self.scale_y = scale_y if scale_y else scale_x
        self.rotate = rotate

        self.entire_image = self.pull_image_data(file)
        self.cut_image = self.get_cut_image(self.entire_image, x1, y1, x2, y2)
        self.final_image = self.cut_image

    def pull_image_data(self, file):
        image = Image.open(file)
        image = image.convert("RGBA")

        # Apply brightness filter
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.25)

        # Rotate the image if required
        if self.rotate !=0:
            image = image.rotate(self.rotate, expand=True)

        data = np.array(image)
        height, width, channel = data.shape
        qimage = QImage(data.data, width, height, width * channel, QImage.Format_RGBA8888)
        if qimage.isNull():
            raise ValueError("Failed to load image data. Unsupported format or corrupted file.")
        return QPixmap.fromImage(qimage)
    
    def get_cut_image(self, entire_image, x1, y1, x2, y2):
        return entire_image.copy(x1, y1, x2 - x1, y2 - y1)

class SpriteAnimation(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Create a scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Load sprite frames
        self.frames = [
            QPixmap("frame1.png"),
            QPixmap("frame2.png"),
            QPixmap("frame3.png"),
            QPixmap("frame4.png")
        ]
        
        # Create sprite item
        self.sprite = QGraphicsPixmapItem(self.frames[0])
        self.scene.addItem(self.sprite)

        # Sprite position
        self.sprite.setPos(100, 100)

        # Timer to animate sprite
        self.frame_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(100)  # Change frame every 100ms

    def load_frames(self):
        pass
        
    
    def next_frame(self):
        """Update the sprite to the next frame."""
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.sprite.setPixmap(self.frames[self.frame_index])

class MapView(QGraphicsView):
    def __init__(self, brushes_dropdown, layer_select_dropdown, layer_objects_dropdown, all_entities, tabs, zoom_slider, random_checkbox, parent=None, main_window = None):
        super().__init__(parent)
        self.setViewport(QGLWidget())  # Enable OpenGL
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.circles = [200]
        self.layer_draw_dict ={}
        self.layer_draw_dict_priority = {'terrain': 1, 
                                         'objects': 2, 
                                         'zombies': 11, 
                                         'entities': 4, 
                                         'railways' :5,
                                         'pipes':6,
                                         'roads':7,
                                         'fortress':8,
                                         'belts':9,
                                         'playable area':10,
                                         'circles':11,
                                         'debug_circles':12}
        
        self.cell_size = starting_cell_size
        self.x_mapoffset = 0
        self.y_mapoffset = 0
        self.layers_visibility = {'terrain': True, 'objects': True, 'zombies': True, 'entities': True, 'railways' :True,'pipes':True,'roads':True,'fortress':True,'belts':True,'playable area': True}
        self.layer_data = {'terrain': None, 'objects': None, 'zombies': None,'pipes':None,'roads':None,'fortress':None,'belts':None}
        self.layer_chunks = {
            'terrain': {}, 'objects': {}, 'zombies': {}, 'pipes': {},
            'roads': {}, 'fortress': {}, 'belts': {}
        }
        self.zombie_sprite_holder = {}  # Add a dictionary to hold zombie sprites
        self.entity_sprite_holder = {}
        self.brushes_dropdown = brushes_dropdown
        self.layer_select_dropdown = layer_select_dropdown
        self.layer_objects_dropdown = layer_objects_dropdown
        self.random_checkbox = random_checkbox
        self.all_entities = all_entities  # Store all_entities
        self.mouse_held = False
        self.grid_visible = False
        self.selected_entity = None
        self.tabs = tabs  # Store the reference to tabs
        self.zoom_slider = zoom_slider  # Store the reference to zoom slider
        self.main_window = main_window
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y() / 120  # 120 is the typical value for one notch
            new_value = self.zoom_slider.value() + delta * self.zoom_slider.singleStep()
            self.zoom_slider.setValue(int(new_value))
        else:
            super().wheelEvent(event)
            
    def draw_playable_area(self):
        layer_name = 'playable area'
        data_array = self.layer_data['zombies']
        size = data_array.shape[0]  # Assuming a square map
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)

        pixmap = QPixmap(size * self.cell_size, size * self.cell_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(pen)

        # Draw the four lines of the diamond shape
        painter.drawLine(self.cell_size, (size // 2) * self.cell_size, (size // 2) * self.cell_size, self.cell_size)  # Top-left to center
        painter.drawLine((size // 2) * self.cell_size, self.cell_size, (size - 1) * self.cell_size, (size // 2) * self.cell_size)  # Center to top-right
        painter.drawLine(self.cell_size, (size // 2) * self.cell_size, (size // 2) * self.cell_size, (size - 1) * self.cell_size)  # Bottom-left to center
        painter.drawLine((size // 2) * self.cell_size, (size - 1) * self.cell_size, (size - 1) * self.cell_size, (size // 2) * self.cell_size)  # Center to bottom-right

        painter.end()

        if layer_name in self.layer_draw_dict and self.layer_draw_dict[layer_name] in self.scene.items():
            self.scene.removeItem(self.layer_draw_dict[layer_name])

        zlevel = self.layer_draw_dict_priority[layer_name]
        self.layer_draw_dict[layer_name] = QGraphicsPixmapItem(pixmap)
        self.layer_draw_dict[layer_name].setZValue(zlevel)
        self.scene.addItem(self.layer_draw_dict[layer_name])
            
    def draw_map(self):
        
        self.scene.clear()
        if self.layers_visibility['terrain']:
            self.draw_layer('terrain',self.layer_data['terrain'], LayerTerrain)
        
        if self.layers_visibility['objects']:
            self.draw_layer('objects',self.layer_data['objects'], LayerObjects)
        
        if self.layers_visibility['pipes']:
            self.draw_layer('pipes',self.layer_data['pipes'], LayerPipes)
        
        if self.layers_visibility['roads']:
            self.draw_layer('roads',self.layer_data['roads'], LayerRoads)
        
        if self.layers_visibility['belts']:
            self.draw_layer('belts',self.layer_data['belts'], LayerBelts)
        
        if self.layers_visibility['fortress']:
            self.draw_layer('fortress',self.layer_data['fortress'], LayerFortress)
            
        if self.layers_visibility['zombies']:
            self.draw_zombie_layer()
        
        if self.layers_visibility['entities']:
            self.entity_boxes = {}
            self.draw_entities()
        
        self.draw_playable_area()
        
        if self.tabs.currentIndex() == 3:
            self.draw_circle()
        
    def update_map(self,layer):
        #on a single entity change or layer changes this function is called to only update the layer you are touching
        #speeds up process
        if self.layers_visibility['terrain'] and layer == 'terrain':
            self.draw_layer('terrain',self.layer_data['terrain'], LayerTerrain)
        
        if self.layers_visibility['objects'] and layer == 'objects':
            self.draw_layer('objects',self.layer_data['objects'], LayerObjects)
        
        if self.layers_visibility['pipes'] and layer == 'pipes':
            self.draw_layer('pipes',self.layer_data['pipes'], LayerPipes)
        
        if self.layers_visibility['roads'] and layer == 'roads':
            self.draw_layer('roads',self.layer_data['roads'], LayerRoads)
        
        if self.layers_visibility['belts'] and layer == 'belts':
            self.draw_layer('belts',self.layer_data['belts'], LayerBelts)
        
        if self.layers_visibility['fortress'] and layer == 'fortress':
            self.draw_layer('fortress',self.layer_data['fortress'], LayerFortress)
            
        if self.layers_visibility['zombies'] and layer == 'zombies':
            self.draw_zombie_layer()
        
        if self.layers_visibility['entities'] and layer == 'entities':
           self.entity_boxes = {}
           self.draw_entities()
        
        if self.tabs.currentIndex() == 3:
            self.draw_circle()
        
    def draw_layer(self, layer_name, data_array, color_dict, overwrite=True):
        if data_array is None:
            return

        chunk_size = 64
        height, width = data_array.shape  # Note the order: height, width

        for chunk_y in range(0, height, chunk_size):
            for chunk_x in range(0, width, chunk_size):
                chunk_key = (chunk_x, chunk_y)
                if chunk_key in self.layer_chunks[layer_name] and not overwrite:
                    continue
                
                pixmap = QPixmap(chunk_size * self.cell_size, chunk_size * self.cell_size)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                for y in range(chunk_y, min(chunk_y + chunk_size, height)):
                    for x in range(chunk_x, min(chunk_x + chunk_size, width)):
                        the_number = data_array[x, y]
                        the_var = color_dict.get(the_number, "None")
                        if the_var != "None":
                            color = QColor(*colors.get(the_var, (0, 0, 0)))
                            painter.fillRect((x - chunk_x) * self.cell_size, (y - chunk_y) * self.cell_size, self.cell_size, self.cell_size, color)
                        if self.grid_visible:  # Draw grid lines
                            pen = QPen(QColor(200, 200, 200))
                            painter.setPen(pen)
                            painter.drawRect((x - chunk_x) * self.cell_size, (y - chunk_y) * self.cell_size, self.cell_size, self.cell_size)
                painter.end()
                
                if chunk_key in self.layer_chunks[layer_name]:
                    item = self.layer_chunks[layer_name][chunk_key]
                    if item in self.scene.items():
                        self.scene.removeItem(item)
                
                zlevel = self.layer_draw_dict_priority[layer_name]
                chunk_item = QGraphicsPixmapItem(pixmap)
                chunk_item.setPos(chunk_x * self.cell_size, chunk_y * self.cell_size)  # Corrected the positions
                chunk_item.setZValue(zlevel)
                self.layer_chunks[layer_name][chunk_key] = chunk_item
                self.scene.addItem(chunk_item)

    def draw_zombie_layer(self):
        layer_name = 'zombies'
        data_array = self.layer_data['zombies']
        if data_array is None:
            return
        
        # Create a pixmap for the zombie layer
        pixmap = QPixmap(data_array.shape[0] * self.cell_size, data_array.shape[1] * self.cell_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        
        for y in range(data_array.shape[0]):
            for x in range(data_array.shape[1]):
                the_number = data_array[y, x]
                the_var = LayerZombies.get(the_number, "ZombieNone")
                if the_var != "ZombieNone" and the_var in self.zombie_sprite_holder:
                    sprite_pixmap = self.zombie_sprite_holder[the_var].final_image
                    painter.drawPixmap(y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size, sprite_pixmap)
                if self.grid_visible:  # Draw grid lines
                    pen = QPen(QColor(200, 200, 200))
                    painter.setPen(pen)
                    painter.drawRect(y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size)
        
        painter.end()

        # Remove the existing layer item if it exists
        if layer_name in self.layer_draw_dict and self.layer_draw_dict[layer_name] in self.scene.items():
            self.scene.removeItem(self.layer_draw_dict[layer_name])
        
        # Create a new QGraphicsPixmapItem for the combined pixmap
        pixmap_item = QGraphicsPixmapItem(pixmap)
        zlevel = self.layer_draw_dict_priority[layer_name]
        pixmap_item.setZValue(zlevel)

        # Add the new pixmap item to the scene
        self.layer_draw_dict[layer_name] = pixmap_item
        self.scene.addItem(pixmap_item)

    def compute_annular_cells(self,r_small_outer, r_large_inner, cell_size):
        pixels = set()  # Use a set to avoid duplicate grid cells

        # Define bounding box (relative to origin)
        r_max = r_large_inner
        x_min, x_max = -r_max, r_max
        y_min, y_max = -r_max, r_max

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                # Compute squared distance from origin (0,0)
                dist_sq = x**2 + y**2
                
                # Check if pixel falls within annular region
                if r_small_outer**2 <= dist_sq <= r_large_inner**2:
                    grid_x, grid_y = x / cell_size /2, y / cell_size /2  # Convert pixel to grid cell
                    
                    pixels.add((int(grid_x + (self.cc_pos[0]- .5)//self.cell_size), int(grid_y + (self.cc_pos[1]- .5)//self.cell_size)))  # Store unique cell coordinates

        return list(pixels)  # Convert set to list for return
    
    def circle_compute(self,weights):
        cells = self.compute_annular_cells(self.circles[0] * self.cell_size,self.circles[1] * self.cell_size,self.cell_size)
        
        data_array = self.layer_data['zombies']
        size = data_array.shape[0]
        for cell in cells:
            if cell[0] < size and cell[1] < size:
                if self.layer_data['objects'][cell[1], cell[0]] not in [1,2] and self.layer_data['terrain'][cell[1], cell[0]] not in [1,3,4]:
                    zombie_random_choice = weighted_random_choice(weights)
                    self.layer_data['zombies'][cell[1], cell[0]] = inverted_LayerZombies[zombie_random_choice]
                    
        self.update_map("zombies")
        
    def draw_circle(self):
        layer_name = "circles"
        for key, values in self.all_entities.items():
            for item in self.all_entities[key]:
                if 'TelescopeEnabled' in item:
                    x = float(self.all_entities[key].get("Position","1;1").split(";")[1]) * self.cell_size
                    y = float(self.all_entities[key].get("Position","1;1").split(";")[0]) * self.cell_size
                
        data_array = self.layer_data['zombies']
        size = data_array.shape[0]
        
        pixmap = QPixmap(size * self.cell_size, size * self.cell_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        pen = QPen(Qt.red)  # Set the outline color
        pen.setWidth(3)  # Set outline thickness
        painter.setPen(pen)
        for circle in self.circles:
            painter.drawEllipse(int(y- circle/2*self.cell_size) , int(x - circle/2*self.cell_size) , circle *self.cell_size, circle*self.cell_size)
        
        self.cc_pos = [x,y]
        
        
        painter.end()
        
        if layer_name in self.layer_draw_dict and self.layer_draw_dict[layer_name] in self.scene.items():
            self.scene.removeItem(self.layer_draw_dict[layer_name])
        zlevel = self.layer_draw_dict_priority[layer_name]
        self.layer_draw_dict[layer_name] = QGraphicsPixmapItem(pixmap)
        self.layer_draw_dict[layer_name].setZValue(zlevel)
        self.scene.addItem(self.layer_draw_dict[layer_name])
    
    def draw_entities(self):
        entity_layer_name = 'entities'
        
        # Using zombies to grab size as entities not stored the same
        data_array = self.layer_data.get('zombies')
        if data_array is None:
            return

        # Create a pixmap for the entities and railways layer
        pixmap = QPixmap(data_array.shape[0] * self.cell_size, data_array.shape[1] * self.cell_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        rail_types = {
            "5720808135500898894": "down_right",
            "3393198510858167203": "right and down",
            "2589476676823118189": "right_down",
            "1005025118540253051": "opps"
        }

        for entity in self.all_entities.keys():
            xsize = float(self.all_entities[entity].get("Size", "1;1").split(";")[0])
            ysize = float(self.all_entities[entity].get("Size", "1;1").split(";")[1])
            x = float(self.all_entities[entity].get("Position", "1;1").split(";")[0])
            y = float(self.all_entities[entity].get("Position", "1;1").split(";")[1])
            starting_x = x * self.cell_size - (xsize / 2 * self.cell_size)
            starting_y = y * self.cell_size - (ysize / 2 * self.cell_size)
            x_len = self.cell_size * xsize
            y_len = self.cell_size * ysize
            
            
            temp_x = x_len
            temp_y = y_len
            x_len_min = 5
            y_len_min = 5
            if temp_x < x_len_min:
                temp_x = x_len_min
            if temp_y < y_len_min:
                temp_y = y_len_min
            
            if self.all_entities[entity]['IDTemplate type=System.UInt64, mscorlib'] in rail_types:
                self.entity_boxes[entity] = {
                    "x": starting_x / self.cell_size - (.5 / self.cell_size),
                    "y": starting_y / self.cell_size - (.5 / self.cell_size),
                    "x_len": x_len / self.cell_size,
                    "y_len": y_len / self.cell_size 
                }
            else:
                self.entity_boxes[entity] = {
                    "x": int(starting_x) / self.cell_size,
                    "y": int(starting_y) / self.cell_size,
                    "x_len": temp_x / self.cell_size,
                    "y_len": temp_y / self.cell_size
                }

            rect = QRectF(starting_x, starting_y, x_len, y_len)
            
            color = QColor(255, 190, 0)
            found = False
            id = self.all_entities[entity]['IDTemplate type=System.UInt64, mscorlib']
            if id in self.main_window.entity_template_dict:
                name = self.main_window.entity_template_dict[id]['Name']
                if name in self.entity_sprite_holder:
                    found = True
                    sprite_pixmap = self.entity_sprite_holder[name].final_image
                    painter.drawPixmap(int(x * self.cell_size - y_len/2), int(y * self.cell_size - x_len/2), int(y_len), int(x_len), sprite_pixmap)
                        
            if self.all_entities[entity]['IDTemplate type=System.UInt64, mscorlib'] in rail_types and not found:
            
                color = QColor(9, 178, 164)
                size = int(self.all_entities[entity].get("Size", "1;1").split(";")[0])
                color = QColor(0, 0, 0)
                if rail_types.get(self.all_entities[entity]["IDTemplate type=System.UInt64, mscorlib"]):
                    rail_type = rail_types[self.all_entities[entity]["IDTemplate type=System.UInt64, mscorlib"]]
                    if rail_type == "right_down":
                        for y_value in range(size):
                            rect = QRectF(
                                x * self.cell_size - size / 2 * self.cell_size + y_value * self.cell_size,
                                y * self.cell_size - size / 2 * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            painter.fillRect(rect, color)
                            if self.grid_visible:
                                pen = QPen(QColor(200, 200, 200))
                                painter.setPen(pen)
                                painter.drawRect(rect)
                        
                        for x_value in range(size):
                            rect = QRectF(
                                x * self.cell_size - size / 2 * self.cell_size + (size - 1) * self.cell_size,
                                (y - size / 2 + x_value) * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            painter.fillRect(rect, color)
                            if self.grid_visible:
                                pen = QPen(QColor(200, 200, 200))
                                painter.setPen(pen)
                                painter.drawRect(rect)
                    
                    if rail_type == "down_right":
                        for y_value in range(size):
                            rect = QRectF(
                                x * self.cell_size - size / 2 * self.cell_size,
                                (y - size / 2 + y_value) * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            painter.fillRect(rect, color)
                            if self.grid_visible:
                                pen = QPen(QColor(200, 200, 200))
                                painter.setPen(pen)
                                painter.drawRect(rect)
                        
                        for x_value in range(size):
                            rect = QRectF(
                                x * self.cell_size - size / 2 * self.cell_size + x_value * self.cell_size,
                                (y - size / 2 + (size - 1)) * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            painter.fillRect(rect, color)
                            if self.grid_visible:
                                pen = QPen(QColor(200, 200, 200))
                                painter.setPen(pen)
                                painter.drawRect(rect)
                        
                    if rail_type == "right and down":
                        for y_value in range(size):
                            rect = QRectF(
                                x * self.cell_size - size / 2 * self.cell_size + y_value * self.cell_size,
                                y * self.cell_size - size / 2 * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            painter.fillRect(rect, color)
                            if self.grid_visible:
                                pen = QPen(QColor(200, 200, 200))
                                painter.setPen(pen)
                                painter.drawRect(rect)
                        
                        for y_value in range(size):
                            rect = QRectF(
                                x * self.cell_size - size / 2 * self.cell_size,
                                (y - size / 2 + y_value) * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            painter.fillRect(rect, color)
                            if self.grid_visible:
                                pen = QPen(QColor(200, 200, 200))
                                painter.setPen(pen)
                                painter.drawRect(rect)
                    
                    if rail_type == "opps":
                        for y_value in range(size):
                            rect = QRectF(
                                x * self.cell_size - size / 2 * self.cell_size + (size - 1) * self.cell_size,
                                (y - size / 2 + y_value) * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            painter.fillRect(rect, color)
                            if self.grid_visible:
                                pen = QPen(QColor(200, 200, 200))
                                painter.setPen(pen)
                                painter.drawRect(rect)
                        
                        for x_value in range(size):
                            rect = QRectF(
                                x * self.cell_size - size / 2 * self.cell_size + x_value * self.cell_size,
                                (y - size / 2 + (size - 1)) * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            painter.fillRect(rect, color)
                            if self.grid_visible:
                                pen = QPen(QColor(200, 200, 200))
                                painter.setPen(pen)
                                painter.drawRect(rect)
            elif not found:
                painter.fillRect(rect, color)
                pen = QPen(QColor(0, 0, 0))
                painter.setPen(pen)
                painter.drawRect(rect)

            if self.all_entities.get(self.selected_entity) and self.all_entities[entity] == self.all_entities[self.selected_entity]:
                # Check if the selected entity is one of the special railways and draw a 6x6 box if true
                if self.all_entities[entity]['IDTemplate type=System.UInt64, mscorlib'] in rail_types:
                    pen = QPen(QColor(255, 0, 0))
                    pen.setWidth(2)
                    pen.setStyle(Qt.DashLine)
                    painter.setPen(pen)
                    special_railway_size = 6 * self.cell_size
                    special_railway_rect = QRectF(
                        starting_y - (special_railway_size - y_len) / 2,
                        starting_x - (special_railway_size - x_len) / 2,
                        special_railway_size,
                        special_railway_size
                    )
                    painter.drawRect(special_railway_rect)
                else:
                    # Draw a red hollow box around the selected entity
                    pen = QPen(QColor(255, 0, 0))
                    pen.setWidth(2)
                    pen.setStyle(Qt.DashLine)
                    painter.setPen(pen)
                    painter.drawRect(rect)

        painter.end()

        # Remove the existing layer item if it exists for entities
        if entity_layer_name in self.layer_draw_dict and self.layer_draw_dict[entity_layer_name] in self.scene.items():
            self.scene.removeItem(self.layer_draw_dict[entity_layer_name])

        # Create a new QGraphicsPixmapItem for the combined pixmap for entities
        entity_pixmap_item = QGraphicsPixmapItem(pixmap)
        entity_zlevel = self.layer_draw_dict_priority[entity_layer_name]
        entity_pixmap_item.setZValue(entity_zlevel)

        # Add the new pixmap item to the scene for entities
        self.layer_draw_dict[entity_layer_name] = entity_pixmap_item
        self.scene.addItem(entity_pixmap_item)
                    
    def set_layer_data(self, layer_name, data_array):
        self.layer_data[layer_name] = data_array

    def toggle_grid(self):
        self.grid_visible = not self.grid_visible
        self.draw_map()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.tabs.currentIndex() == 0:
                self.mouse_held = True
            pos = self.mapToScene(event.pos())
            grid_x = int(pos.y() // self.cell_size)
            grid_y = int(pos.x() // self.cell_size)
            self.handle_mouse_click(grid_x, grid_y)  

    def mouseMoveEvent(self, event):
        if self.mouse_held:
            pos = self.mapToScene(event.pos())
            if self.tabs.currentIndex() == 0:
                grid_x = int(pos.y() // self.cell_size)
                grid_y = int(pos.x() // self.cell_size)
                self.handle_mouse_click(grid_x, grid_y)  

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_held = False

    def handle_mouse_click(self, grid_x, grid_y):
        layer_updated = ""
        if self.tabs.currentIndex() == 0:
        
            brush_size = self.brushes_dropdown.currentText()
            select_layer = self.layer_select_dropdown.currentText()
            selected_option = self.layer_objects_dropdown.currentText()
            
            potential_items = self.layer_objects_dropdown.get_checked_items()
            print(potential_items)
            
            brush_offsets = {
                "Single": [(0, 0)],
                "Crosshair": [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)],
                "3x3": [(x, y) for x in range(-1, 2) for y in range(-1, 2)],
                "5x5": [(x, y) for x in range(-2, 3) for y in range(-2, 3)],
                "CLEAR":[(x, y) for x in range(-256, 256) for y in range(-256, 256)],
            }
            
            for offset in brush_offsets[brush_size]:
                if self.random_checkbox.isChecked():
                    selected_option = random.choice(potential_items)

                new_grid_x = grid_x + offset[0]
                new_grid_y = grid_y + offset[1]
                if new_grid_x >= self.layer_data['terrain'].shape[1] or new_grid_y >= self.layer_data['terrain'].shape[0] or new_grid_x < 0 or new_grid_y < 0:
                    continue
                
                if select_layer == "terrain":
                    for key, value in LayerTerrain.items():
                        if value == selected_option:
                            self.layer_data['terrain'][new_grid_y, new_grid_x] = key
                            layer_updated = 'terrain'
                            break
                elif select_layer == "objects":
                    for key, value in LayerObjects.items():
                        if value == selected_option:
                            self.layer_data['objects'][new_grid_y, new_grid_x] = key
                            layer_updated = 'objects'
                            break
                elif select_layer == "zombies":
                    for key, value in LayerZombies.items():
                        if value == selected_option:
                            if self.layer_data['objects'][new_grid_y, new_grid_x] not in [1,2] and self.layer_data['terrain'][new_grid_y, new_grid_x] not in [1,3,4]:
                                self.layer_data['zombies'][new_grid_y, new_grid_x] = key
                                layer_updated = 'zombies'
                            else:
                                temp = self.layer_data['objects'][new_grid_y, new_grid_x]
                            break
                elif select_layer == "pipes":
                    for key, value in LayerPipes.items():
                        if value == selected_option:
                            self.layer_data['pipes'][new_grid_y, new_grid_x] = key
                            layer_updated = 'pipes'
                            break
                elif select_layer == "roads":
                    for key, value in LayerRoads.items():
                        if value == selected_option:
                            self.layer_data['roads'][new_grid_y, new_grid_x] = key
                            layer_updated = 'roads'
                            break
                elif select_layer == "fortress":
                    for key, value in LayerFortress.items():
                        if value == selected_option:
                            self.layer_data['fortress'][new_grid_y, new_grid_x] = key
                            layer_updated = 'fortress'
                            break
                elif select_layer == "belts":
                    for key, value in LayerBelts.items():
                        if value == selected_option:
                            self.layer_data['belts'][new_grid_y, new_grid_x] = key
                            layer_updated = 'belts'
                            break
                elif selected_option == "CommandCenter":
                    for entity in self.parent().all_entities.values():
                        if "isCommandCenter" in entity:
                            entity["valuex"] = new_grid_x + 0.5
                            entity["valuey"] = new_grid_y + 0.5
                            break
                        
        if self.tabs.currentIndex() == 1:
            if self.main_window.add_new_entity_button.isChecked():
                self.main_window.add_new_entity(grid_x,grid_y)
            else:
                self.find_and_print_entity(grid_x, grid_y)
                layer_updated = 'entities'
        
        if self.tabs.currentIndex() == 3:
            layer_updated = 'circles'
        
        if layer_updated:
            self.update_map(layer_updated)
        
    def find_and_print_entity(self, grid_x, grid_y):
        print(grid_x,grid_y)
        
        def point_in_boxes_dict(px, py, boxes_dict):
            potential_items = []
            for key, box in boxes_dict.items():
                min_x = box["x"]
                max_x = box["x"] + box["x_len"]
                min_y = box["y"]
                max_y = box["y"] + box["y_len"]
                if min_x <= px <= max_x and min_y <= py <= max_y:
                    potential_items.append(key)
                    print(key,box)
            return potential_items

        potential_items = point_in_boxes_dict(grid_y,grid_x,self.entity_boxes)
        if potential_items:
            self.selected_entity = random.choice(potential_items)
        else:
            self.selected_entity = None
        
        self.update_entity_data_text_edit()

    def update_entity_data_text_edit(self):
        if self.selected_entity is not None:
            if self.selected_entity in self.all_entities:
                
                entity_data = self.all_entities[self.selected_entity]['template']
                temp_str = "".join(entity_data)
                self.tabs.widget(1).findChild(QTextEdit).setPlainText(temp_str)
                
                common_name = self.tabs.widget(1).findChild(QLabel)
                if self.all_entities[self.selected_entity] and common_name:
                    if self.all_entities[self.selected_entity].get("IDTemplate type=System.UInt64, mscorlib"):
                        if entitynames.name_dict.get(self.all_entities[self.selected_entity]["IDTemplate type=System.UInt64, mscorlib"]):
                            name = entitynames.name_dict.get(self.all_entities[self.selected_entity]["IDTemplate type=System.UInt64, mscorlib"])
                            common_name.setText(name['Name'])
            else:
                self.tabs.widget(1).findChild(QTextEdit).setPlainText("")
                common_name = self.tabs.widget(1).findChild(QLabel)
                common_name.setText('Common Name')

    def load_zombie_sprites(self, sprite_directory):
        self.zombie_sprite_holder = {}
        sprite_dict_zombies = dict_zombies(sprite_directory)
        for sprite, data in sprite_dict_zombies.items():
            temp = ImageHandler(
                data["path"],
                data["x1"],
                data["y1"],
                data["x2"],
                data["y2"],
                data.get("scale_x", 1),
                data.get("scale_y", 1),
                self.cell_size,
                data.get("cell_size", 1),
                data.get("rotate",0)
            )
            self.zombie_sprite_holder[sprite] = temp

    def load_entity_sprites(self,sprite_directory):
        self.entity_sprite_holder = {}
        sprite_dict_entity = dict_entities(sprite_directory)
        for sprite, data in sprite_dict_entity.items():
            temp = ImageHandler(
                data["path"],
                data["x1"],
                data["y1"],
                data["x2"],
                data["y2"],
                data.get("scale_x", 1),
                data.get("scale_y", 1),
                self.cell_size,
                data.get("cell_size", 1),
                data.get("rotate",0)
            )
            self.entity_sprite_holder[sprite] = temp

class MyPopup(QWidget):
    def __init__(self):
        print('here')
        QWidget.__init__(self)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Enter text:")
        layout.addWidget(self.label)

        self.text_input = QLineEdit(self)
        layout.addWidget(self.text_input)

        self.button = QPushButton("Print Text", self)
        self.button.clicked.connect(self.print_text)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setWindowTitle("PyQt5 Text Input Example")
        self.setGeometry(100, 100, 300, 150)

    def print_text(self):
        text = self.text_input.text()
        print(f"Entered Text: {text}")

class CheckboxWidget(QWidget):
    def __init__(self, mainwindow, items, parent_layer,parent=None):
        super().__init__(parent)
        self.parent_layer = parent_layer
        self.mainwindow = mainwindow
        # Main layout
        main_layout = QVBoxLayout(self)

        # Create a group box to enclose everything
        self.group_box = QGroupBox(f'Circle')
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setSpacing(5)  # Reduce spacing between rows

        self.data = {}  # Store references to checkboxes and textboxes
        
        for item in items:
            row_layout = QHBoxLayout()

            checkbox = QCheckBox(item)
            textbox = QLineEdit()
            textbox.setFixedWidth(50)  # Small text box
            textbox.setValidator(QIntValidator(1, 100))  # Limit between 1 and 100
            textbox.setPlaceholderText("1-100")

            # Store references
            self.data[item] = {"checkbox": checkbox, "textbox": textbox}

            row_layout.addWidget(checkbox)
            row_layout.addWidget(textbox)
            row_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins inside row
            group_layout.addLayout(row_layout)

        remove_button = QPushButton("Generate")
        remove_button.clicked.connect(self.generate)
        group_layout.addWidget(remove_button)
        # Set group box layout
        self.group_box.setLayout(group_layout)

        # Add the group box to the main layout
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def retrieve_values(self):
        values = {
            key: int(widget["textbox"].text()) if widget["textbox"].text().isdigit() else 1
            for key, widget in self.data.items()
            if widget["checkbox"].isChecked()  # Only include checked items
        }
        return values
        

    def generate(self):
        """Removes this widget from the parent layout."""
        self.mainwindow.map_view.circle_compute(self.retrieve_values())
        pass

   
class MainWindow(QMainWindow):
    def __init__(self, current_map, directory, sevenzip_executable):
        super().__init__()
        self.setWindowTitle("Map Editor")
        self.current_map = current_map
        self.directory = directory
        self.sevenzip_executable = sevenzip_executable
        self.brushes_dropdown = None
        self.layer_objects_dropdown = None
        self.all_entities = None
        self.create_arrow_shortcuts()
        self.create_delete_shortcut()
        
        if self.current_map.valid_map:
            self.data_size = self.current_map.data_size
            self.import_entity_template()
            self.create_menu_bar()  # Add this line to create the menu bar
            self.initUI()
            self.load_map_data()

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        
        # Create the Settings menu
        settings_menu = QMenu('File', self)

        # Add dropdown options to the Settings menu
        action1 = QAction('Save', self)
        action2 = QAction('Load', self)
        action3 = QAction('Help', self)
        action4 = QAction('About', self)
        action5 = QAction('Options', self)
        
        action1.triggered.connect(lambda: self.on_setting_selected('Save'))
        action2.triggered.connect(lambda: self.on_setting_selected('Load'))
        action3.triggered.connect(lambda: self.on_setting_selected('Help'))
        action4.triggered.connect(lambda: self.on_setting_selected('About'))
        action5.triggered.connect(lambda: self.on_setting_selected('Options'))

        settings_menu.addAction(action1)
        settings_menu.addAction(action2)
        settings_menu.addAction(action3)
        settings_menu.addAction(action4)
        settings_menu.addAction(action5)

        # Add the Settings menu to the menu bar
        menu_bar.addMenu(settings_menu)
        self.setMenuBar(menu_bar)

    def options_menu(self):
        print('here1')
        self.w = MyPopup()
        self.w.show()
    
    def on_setting_selected(self, option):

        if option == "Save":
            self.save_map()
        elif option == "Load":
            self.load_map()
        elif option == "Help":            
            QMessageBox.about(self, "Help", help_str)
        elif option == "About":
            QMessageBox.about(self, "About", "TAB Campaign Mod Tool\nVersion 1.4\nAuthor: SomeSkillRequired")
        elif option == "Options":
            self.options_menu()
        print(f'Selected setting: {option}')

    def initUI(self):
        self.tab_width = 300
        self.tab_width_button = 280
        layout = QVBoxLayout()
    
        self.tabs = QTabWidget()
        self.tabs.setMinimumWidth(300)  # Set minimum width for the tabs

        self.tabs.addTab(self.create_terrain_tab(), "Terrain")
        self.tabs.addTab(self.create_entities_tab(), "Entities")
        self.tabs.addTab(self.create_extras_tab(), "Extra")
        
        self.zoom_slider = QSlider(Qt.Horizontal, self)
        self.zoom_slider.setRange(5, 33)
        self.zoom_slider.setValue(10)
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(self.tabs)
        tab_layout.addWidget(self.zoom_slider)

        tab_widget = QWidget()
        tab_widget.setLayout(tab_layout)

        self.map_view = MapView(self.brushes_dropdown, self.layer_select_dropdown ,self.layer_objects_dropdown, self.all_entities, self.tabs, self.zoom_slider, self.random_checkbox, main_window=self)
        self.tabs.addTab(self.create_zombie_gen_tab(), "Zombies Generator")
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(tab_widget)
        splitter.addWidget(self.map_view)
        splitter.setStretchFactor(0, 1)  # Give the tabs widget less initial space
        splitter.setStretchFactor(1, 4)  # Give the map view more initial space
        layout.addWidget(splitter)
        splitter.splitterMoved.connect(self.on_splitter_moved)
        self.splitter = splitter
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_terrain_tab(self):
        terrain_tab = QWidget()
        layout = QVBoxLayout()

        self.terrain_checkbox = QPushButton('Terrain', self)
        self.terrain_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.terrain_checkbox.setCheckable(True)
        self.terrain_checkbox.setChecked(True)
        self.terrain_checkbox.clicked.connect(lambda: self.toggle_layer('terrain'))
        layout.addWidget(self.terrain_checkbox)

        self.objects_checkbox = QPushButton('Objects', self)
        self.objects_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.objects_checkbox.setCheckable(True)
        self.objects_checkbox.setChecked(True)
        self.objects_checkbox.clicked.connect(lambda: self.toggle_layer('objects'))
        layout.addWidget(self.objects_checkbox)

        self.zombies_checkbox = QPushButton('Zombies', self)
        self.zombies_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.zombies_checkbox.setCheckable(True)
        self.zombies_checkbox.setChecked(True)
        self.zombies_checkbox.clicked.connect(lambda: self.toggle_layer('zombies'))
        layout.addWidget(self.zombies_checkbox)
        
        self.pipes_checkbox = QPushButton('Pipes', self)
        self.pipes_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.pipes_checkbox.setCheckable(True)
        self.pipes_checkbox.setChecked(True)
        self.pipes_checkbox.clicked.connect(lambda: self.toggle_layer('pipes'))
        layout.addWidget(self.pipes_checkbox)
        
        self.roads_checkbox = QPushButton('Roads', self)
        self.roads_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.roads_checkbox.setCheckable(True)
        self.roads_checkbox.setChecked(True)
        self.roads_checkbox.clicked.connect(lambda: self.toggle_layer('roads'))
        layout.addWidget(self.roads_checkbox)
        
        self.fortress_checkbox = QPushButton('Fortress', self)
        self.fortress_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.fortress_checkbox.setCheckable(True)
        self.fortress_checkbox.setChecked(True)
        self.fortress_checkbox.clicked.connect(lambda: self.toggle_layer('fortress'))
        layout.addWidget(self.fortress_checkbox)
        
        self.belts_checkbox = QPushButton('Belts', self)
        self.belts_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.belts_checkbox.setCheckable(True)
        self.belts_checkbox.setChecked(True)
        self.belts_checkbox.clicked.connect(lambda: self.toggle_layer('belts'))
        layout.addWidget(self.belts_checkbox)

        self.random_checkbox = QPushButton('Random', self)
        self.random_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.random_checkbox.setCheckable(True)
        self.random_checkbox.setChecked(False)
        self.random_checkbox.clicked.connect(self.toggle_random)  # Connect to the toggle_grid method
        layout.addWidget(self.random_checkbox)
        
        self.grid_checkbox = QPushButton('Grid', self)
        self.grid_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.grid_checkbox.setCheckable(True)
        self.grid_checkbox.setChecked(False)
        self.grid_checkbox.clicked.connect(self.toggle_grid)  # Connect to the toggle_grid method
        layout.addWidget(self.grid_checkbox)

        self.layer_select_dropdown = QComboBox(self)
        self.layer_select_dropdown.setFixedWidth(self.tab_width_button)  # Set fixed width for the dropdown
        self.layer_select_dropdown.addItems(['terrain', 'objects', 'zombies','pipes','roads','fortress','belts'])
        self.layer_select_dropdown.currentIndexChanged.connect(self.change_layer)
        
        layout.addWidget(QLabel("Layer Select"))
        layout.addWidget(self.layer_select_dropdown)

        self.layer_objects_dropdown = MultiSelectComboBox(self)
        self.layer_objects_dropdown.setFixedWidth(self.tab_width_button)  # Set fixed width for the dropdown
        self.layer_objects_dropdown.addItems(LayerTerrain.values())  # Start with LayerTerrain items
        layout.addWidget(QLabel("Layer Objects"))
        layout.addWidget(self.layer_objects_dropdown)

        self.brushes_dropdown = QComboBox(self)
        self.brushes_dropdown.setFixedWidth(self.tab_width_button)  # Set fixed width for the dropdown
        self.brushes_dropdown.addItems(["Single", "Crosshair", "3x3", "5x5", "CLEAR"])
        layout.addWidget(QLabel("Brushes"))
        layout.addWidget(self.brushes_dropdown)

        layout.addStretch()
        terrain_tab.setLayout(layout)
        return terrain_tab

    def create_entities_tab(self):
        entities_tab = QWidget()
        layout = QVBoxLayout()

        self.entities_checkbox = QPushButton('Entities', self)
        self.entities_checkbox.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.entities_checkbox.setCheckable(True)
        self.entities_checkbox.setChecked(True)
        layout.addWidget(self.entities_checkbox)
        self.entities_checkbox.clicked.connect(lambda: self.toggle_layer('entities'))

        self.entity_common_name = QLabel('Entity-Name', self)
        self.entity_common_name.setFixedWidth(self.tab_width_button)  # Set fixed width for the QTextEdit
        layout.addWidget(self.entity_common_name)
        
        self.entity_data_edit = QTextEdit(self)
        self.entity_data_edit.setFixedWidth(self.tab_width - 20)  # Set initial width
        self.entity_data_edit.setFixedHeight(600)  # Set fixed height for the QTextEdit
        font = QFont()
        font.setPointSize(8)  # Set the desired font size
        self.entity_data_edit.setFont(font)
        self.entity_data_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.entity_data_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.entity_data_edit)

        self.save_entity_button = QPushButton('Save Entity', self)
        self.save_entity_button.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.save_entity_button.clicked.connect(self.save_entity_data)
        layout.addWidget(self.save_entity_button)
        
        self.delete_entity_button = QPushButton('Delete Entity', self)
        self.delete_entity_button.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.delete_entity_button.clicked.connect(self.delete_entity_data)
        layout.addWidget(self.delete_entity_button)
        
        self.entity_select_dropdown = QComboBox(self)
        self.entity_select_dropdown.setFixedWidth(self.tab_width_button)  # Set fixed width for the dropdown
        self.entity_select_dropdown.addItems([value['Name'] for key, value in self.entity_template_dict.items() if 'Name' in value])
        layout.addWidget(QLabel("Entity"))
        layout.addWidget(self.entity_select_dropdown)
        
        self.add_new_entity_button = QPushButton('Add New Entity', self)
        self.add_new_entity_button.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.add_new_entity_button.setCheckable(True)
        self.add_new_entity_button.setChecked(False)
        self.add_new_entity_button.clicked.connect(self.enable_add_new_entity_mode)
        layout.addWidget(self.add_new_entity_button)

        layout.addStretch()
        entities_tab.setLayout(layout)
        return entities_tab

    def create_zombie_gen_tab(self):
        zombies_gen_tab = QWidget()
        self.zombies_layout = QVBoxLayout()
        self.zombies_layout.addSpacerItem(QSpacerItem(50, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        label = QLabel('Mininum Distance from Command center')
        self.zombies_layout.addWidget(label)
        self.min_distance = QLineEdit(self)
        self.max_distance = QLineEdit(self)
        self.min_distance.setText('50')
        self.max_distance.setText('55')
        self.min_distance.editingFinished.connect(self.update_circles)
        self.max_distance.editingFinished.connect(self.update_circles)
        
        int_validator = QIntValidator(0, 512, self)
        self.min_distance.setValidator(int_validator)
        self.max_distance.setValidator(int_validator)
        self.zombies_layout.addWidget(self.min_distance)
        self.zombies_layout.addWidget(self.max_distance)
        
        zombies_gen_tab.setLayout(self.zombies_layout)
        new_widget = CheckboxWidget(self,LayerZombies.values(),self.zombies_layout)
        self.zombies_layout.addWidget(new_widget)
        self.map_view.circles = []
        
        return zombies_gen_tab
    
    def update_circles(self):
        self.map_view.circles = []
        if self.max_distance.text():
            self.map_view.circles.append(int(self.min_distance.text()))
            self.map_view.update_map('none')
        if self.min_distance.text():
            self.map_view.circles.append(int(self.max_distance.text()))
            self.map_view.update_map('none')
    
    def create_extras_tab(self):
        extras_tab = QWidget()
        layout = QVBoxLayout()
        label = QLabel('Enter a size (0-512):')
        layout.addWidget(label)
        self.int_input_1 = QLineEdit(self)
        int_validator = QIntValidator(0, 512, self)
        self.int_input_1.setValidator(int_validator)
        layout.addWidget(self.int_input_1)
        
        label = QLabel('Enter a x offset (0-512):\nMax value = new map size - current map size')
        layout.addWidget(label)
        self.int_input_x = QLineEdit(self)
        int_validator = QIntValidator(0, 512, self)
        self.int_input_x.setValidator(int_validator)
        layout.addWidget(self.int_input_x)
        
        label = QLabel('Enter a y offset (0-512):\nMax value = new map size - current map size')
        layout.addWidget(label)
        self.int_input_y = QLineEdit(self)
        int_validator = QIntValidator(0, 512, self)
        self.int_input_y.setValidator(int_validator)
        layout.addWidget(self.int_input_y)
        
        self.upscale_button = QPushButton('Upscale Map', self)
        self.upscale_button.setFixedWidth(self.tab_width_button)  # Set fixed width for the button
        self.upscale_button.clicked.connect(self.upscale_map)
        
        layout.addWidget(self.upscale_button)
        layout.addStretch()
        extras_tab.setLayout(layout)
        return extras_tab
    
    def upscale_map(self):
        
        def replace_line(match):
            spaces = match.group(1)
            name = match.group(2)
            num1 = float(match.group(3)) + x_offset
            num2 = float(match.group(4)) + y_offset
            return f'{spaces}<Simple name="{name}" value="{num1};{num2}" />'
        
        # Error checking
        if not self.int_input_1.text() or not self.int_input_x.text() or not self.int_input_y.text():
            return
        if not self.current_map or not self.current_map.data_size:
            return

        old_size = self.current_map.data_size
        new_size = int(self.int_input_1.text())
        x_offset = int(self.int_input_x.text())
        y_offset = int(self.int_input_y.text())

        self.current_map.cell_size_change(old_size, new_size)

        # Update layers
        self.data64_LayerTerrain = self.resize_layer(self.data64_LayerTerrain, new_size, x_offset, y_offset)
        self.data64_LayerObjects = self.resize_layer(self.data64_LayerObjects, new_size, x_offset, y_offset)
        self.data64_LayerRoads = self.resize_layer(self.data64_LayerRoads, new_size, x_offset, y_offset)
        self.data64_LayerZombies = self.resize_layer(self.data64_LayerZombies, new_size, x_offset, y_offset)
        self.data64_LayerFortress = self.resize_layer(self.data64_LayerFortress, new_size, x_offset, y_offset)
        self.data64_LayerPipes = self.resize_layer(self.data64_LayerPipes, new_size, x_offset, y_offset)
        self.data64_LayerBelts = self.resize_layer(self.data64_LayerBelts, new_size, x_offset, y_offset)

        for entity in self.all_entities:
            entity_data = self.all_entities[entity]['template']
            pattern = re.compile(r'(\s*)<Simple name="(LastPosition|Position)" value="([\d.]+);([\d.]+)" />')
            # Substitute all matching lines using the replace function
            self.all_entities[entity]['template'] = pattern.sub(replace_line, "".join(entity_data)).split("\n")
        
        for entity in self.all_entities.keys():
            self.current_map.update_entity(entity, self.all_entities[entity]['template'])
        
    def resize_layer(self, layer, new_size, x_offset, y_offset):
        new_list = np.zeros((new_size, new_size))
        old_size = layer.shape[0]
        for i in range(old_size):
            for j in range(old_size):
                if i + x_offset < new_size and j + y_offset < new_size:
                    new_list[i + x_offset][j + y_offset] = layer[i][j]
        return new_list
        # Function to replace matched lines with updated values
        
    def create_delete_shortcut(self):
        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        delete_shortcut.activated.connect(self.handle_delete_key)
        
    def create_arrow_shortcuts(self):
        arrow_up = QShortcut(QKeySequence(Qt.Key_Up), self)
        arrow_down = QShortcut(QKeySequence(Qt.Key_Down), self)
        arrow_left = QShortcut(QKeySequence(Qt.Key_Left), self)
        arrow_right = QShortcut(QKeySequence(Qt.Key_Right), self)
        
        arrow_up.activated.connect(lambda: self.handle_arrow_key("Up"))
        arrow_down.activated.connect(lambda: self.handle_arrow_key("Down"))
        arrow_left.activated.connect(lambda: self.handle_arrow_key("Left"))
        arrow_right.activated.connect(lambda: self.handle_arrow_key("Right"))
        
        # Add shortcuts for Alt + Arrow keys
        alt_up = QShortcut(QKeySequence(Qt.AltModifier | Qt.Key_Up), self)
        alt_down = QShortcut(QKeySequence(Qt.AltModifier | Qt.Key_Down), self)
        alt_left = QShortcut(QKeySequence(Qt.AltModifier | Qt.Key_Left), self)
        alt_right = QShortcut(QKeySequence(Qt.AltModifier | Qt.Key_Right), self)
        
        alt_up.activated.connect(lambda: self.handle_arrow_key("Up", Qt.AltModifier))
        alt_down.activated.connect(lambda: self.handle_arrow_key("Down", Qt.AltModifier))
        alt_left.activated.connect(lambda: self.handle_arrow_key("Left", Qt.AltModifier))
        alt_right.activated.connect(lambda: self.handle_arrow_key("Right", Qt.AltModifier))
        
        # Add shortcuts for Ctrl + Arrow keys
        ctrl_up = QShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Up), self)
        ctrl_down = QShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Down), self)
        ctrl_left = QShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Left), self)
        ctrl_right = QShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Right), self)
        
        ctrl_up.activated.connect(lambda: self.handle_arrow_key("Up", Qt.ControlModifier))
        ctrl_down.activated.connect(lambda: self.handle_arrow_key("Down", Qt.ControlModifier))
        ctrl_left.activated.connect(lambda: self.handle_arrow_key("Left", Qt.ControlModifier))
        ctrl_right.activated.connect(lambda: self.handle_arrow_key("Right", Qt.ControlModifier))
        
        # Add shortcuts for Alt + Ctrl + Arrow keys
        alt_ctrl_up = QShortcut(QKeySequence(Qt.AltModifier | Qt.ControlModifier | Qt.Key_Up), self)
        alt_ctrl_down = QShortcut(QKeySequence(Qt.AltModifier | Qt.ControlModifier | Qt.Key_Down), self)
        alt_ctrl_left = QShortcut(QKeySequence(Qt.AltModifier | Qt.ControlModifier | Qt.Key_Left), self)
        alt_ctrl_right = QShortcut(QKeySequence(Qt.AltModifier | Qt.ControlModifier | Qt.Key_Right), self)
        
        alt_ctrl_up.activated.connect(lambda: self.handle_arrow_key("Up", Qt.AltModifier | Qt.ControlModifier))
        alt_ctrl_down.activated.connect(lambda: self.handle_arrow_key("Down", Qt.AltModifier | Qt.ControlModifier))
        alt_ctrl_left.activated.connect(lambda: self.handle_arrow_key("Left", Qt.AltModifier | Qt.ControlModifier))
        alt_ctrl_right.activated.connect(lambda: self.handle_arrow_key("Right", Qt.AltModifier | Qt.ControlModifier))

    def handle_arrow_key(self, key, modifier=None):
        # Ensure Tab 2
        if self.tabs.currentIndex() != 1:
            return
        
        # Ensure Entity Selected
        if not self.map_view.selected_entity:
            return
        
        # Ensure Valid Entity Selected
        if self.map_view.selected_entity not in self.map_view.all_entities:
            return
        
        standard_offset = 1
        alt_offset = 5
        ctrl_offset = 10
        altctrl_offset = 50
        
        offset = standard_offset
        
        if modifier == Qt.AltModifier:
            offset = alt_offset
        elif modifier == Qt.ControlModifier:
            offset = ctrl_offset
        elif modifier == (Qt.AltModifier | Qt.ControlModifier):
            offset = altctrl_offset
        
        if key == "Up":
            x_offset = 0
            y_offset = -offset
        elif key == "Down":
            x_offset = 0
            y_offset = offset
        elif key == "Left":
            x_offset = -offset
            y_offset = 0
        elif key == "Right":
            x_offset = offset 
            y_offset = 0
        
        def replace_line(match):
            spaces = match.group(1)
            name = match.group(2)
            num1 = float(match.group(3)) + x_offset
            num2 = float(match.group(4)) + y_offset
            return f'{spaces}<Simple name="{name}" value="{num1};{num2}" />'
        
        entity_data =  self.map_view.all_entities[self.map_view.selected_entity]['template']
        pattern = re.compile(r'(\s*)<Simple name="(LastPosition|Position)" value="([\d.]+);([\d.]+)" />')
        # Substitute all matching lines using the replace function
        self.map_view.all_entities[self.map_view.selected_entity]['template'] = pattern.sub(replace_line, "".join(entity_data)).split("\n")
        
        new_entity_location = self.current_map.update_entity(self.map_view.selected_entity, self.map_view.all_entities[self.map_view.selected_entity]['template'])
        self.reload_entity_data()
        
        self.map_view.selected_entity = new_entity_location
        self.map_view.update_entity_data_text_edit()
        self.map_view.draw_map()
    
    def handle_delete_key(self):
        if self.tabs.currentIndex() == 1:  # Only trigger if on the Entities tab
            self.delete_entity_data()
    
    def on_splitter_moved(self, pos, index):
        # Resize the entity data edit box based on the new width of the tab widget
        tab_width = self.tabs.width()
        self.entity_data_edit.setFixedWidth(tab_width - 20)
    
    def import_entity_template(self):
        file = "entity_dict.json"
        with open(file,'r') as file:
            self.entity_template_dict = json.load(file)
        
    def enable_add_new_entity_mode(self):
        self.add_new_entity_button.checkStateSet = not self.add_new_entity_button.checkStateSet
        if self.add_new_entity_button.isChecked():
            self.add_new_entity_button.setChecked(True)
            self.map_view.setCursor(Qt.CrossCursor)
        else:
            self.add_new_entity_button.setChecked(False)
            self.map_view.setCursor(Qt.ArrowCursor)

    def add_new_entity(self, grid_x, grid_y):
        selected_entity_name = self.entity_select_dropdown.currentText()
        selected_entity_template = None
        for key, value in self.entity_template_dict.items():
            if value.get('Name') == selected_entity_name:
                selected_entity_template = value.get('template')
                if ("Rail" in selected_entity_template and
                    "5720808135500898894" not in selected_entity_template and
                    "3393198510858167203" not in selected_entity_template and
                    "2589476676823118189" not in selected_entity_template and
                    "1005025118540253051" not in selected_entity_template):
                    grid_x += .5
                    grid_y += .5
                break

        selected_entity_template = selected_entity_template.replace('<Simple name="Position" value=" 0;0" />',f'<Simple name="Position" value="{grid_y};{grid_x}" />')
        selected_entity_template = selected_entity_template.replace('<Simple name="LastPosition" value=" 0;0" />',f'<Simple name="LastPosition" value="{grid_y};{grid_x}" />')
        
        if selected_entity_template:
            last_newline_pos = selected_entity_template.rfind('\n')
            selected_entity_template = selected_entity_template[:last_newline_pos]
            selected_entity_template = "      " + selected_entity_template
            self.current_map.push_new_entity(selected_entity_template)
            
        self.reload_entity_data()
        self.map_view.selected_entity = None
        self.map_view.draw_map()

    def save_entity_data(self):
        if self.map_view.selected_entity:
            entity_data_text = self.entity_data_edit.toPlainText()
            entity_data_list = entity_data_text.split('\n')
            if self.map_view.selected_entity:
                new_entity_location = self.current_map.update_entity(self.map_view.selected_entity, entity_data_list)
                self.reload_entity_data()
                self.map_view.selected_entity = new_entity_location
                self.map_view.update_entity_data_text_edit()
                self.map_view.draw_map()
        
    def delete_entity_data(self):
        if self.map_view.selected_entity:
            if self.map_view.selected_entity in self.map_view.all_entities:
                entity_data_text = self.entity_data_edit.toPlainText()
                entity_data_list = entity_data_text.split('\n')
                entity_index = self.map_view.selected_entity
                self.current_map.delete_entity(entity_index,entity_data_list)
                self.reload_entity_data()
                self.map_view.update_entity_data_text_edit()
                self.map_view.draw_map()
    
    def reload_entity_data(self):
        self.all_entities = self.current_map.entities
        self.map_view.all_entities = self.all_entities
            
    def load_map(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Map", "", "All Files (*);;Map Files (*.dxlevel)", options=options)
        if file_name:
            print(f"Selected file: {file_name}")
            self.current_map = Map(self.directory, file_name, self.sevenzip_executable)
            self.load_map_data()

    def save_map(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Map", "", "All Files (*);;Map Files (*.dxlevel)", options=options)
        if file_path:
            self.current_map.layers[0] = self.data64_LayerTerrain
            self.current_map.layers[1] = self.data64_LayerObjects
            self.current_map.layers[2] = self.data64_LayerRoads
            self.current_map.layers[3] = self.data64_LayerZombies
            self.current_map.layers[4] = self.data64_LayerFortress
            self.current_map.layers[5] = self.data64_LayerPipes
            self.current_map.layers[6] = self.data64_LayerBelts
            
            file_name  = os.path.basename(file_path)
            unzipped_location = os.path.join(self.directory,"ZXGame_Data\Levels\custom_maps_unzipped",file_name)
            self.current_map.push_layer_strings()
            
            print(f"Saving file to: {unzipped_location}")
            self.current_map.write_to_file(unzipped_location)
            print(f"Zipping file to: {file_path}")
            self.current_map.zip_files_with_7zip(unzipped_location, file_path)

    def change_zoom(self, value):
        self.map_view.cell_size = int(5 * (value / 10.0))
        self.map_view.draw_map()

    def change_layer(self, index):
        layer_name = self.layer_select_dropdown.currentText()
        if layer_name == 'terrain':
            self.layer_objects_dropdown.clear()
            self.layer_objects_dropdown.addItems(LayerTerrain.values())
        elif layer_name == 'objects':
            self.layer_objects_dropdown.clear()
            self.layer_objects_dropdown.addItems(LayerObjects.values())
        elif layer_name == 'zombies':
            self.layer_objects_dropdown.clear()
            self.layer_objects_dropdown.addItems(LayerZombies.values())
        elif layer_name == 'pipes':
            self.layer_objects_dropdown.clear()
            self.layer_objects_dropdown.addItems(LayerPipes.values())
        elif layer_name == 'roads':
            self.layer_objects_dropdown.clear()
            self.layer_objects_dropdown.addItems(LayerRoads.values())
        elif layer_name == 'fortress':
            self.layer_objects_dropdown.clear()
            self.layer_objects_dropdown.addItems(LayerFortress.values())
        elif layer_name == 'belts':
            self.layer_objects_dropdown.clear()
            self.layer_objects_dropdown.addItems(LayerBelts.values())    
        
        print(f"Selected layer: {layer_name}")

    def toggle_layer(self, layer_name):
        self.map_view.layers_visibility[layer_name] = not self.map_view.layers_visibility[layer_name]
        self.map_view.draw_map()

    def toggle_grid(self):
        self.map_view.toggle_grid()
        
    def toggle_random(self):
        pass
        
    def load_map_data(self):
        self.data64_LayerTerrain  = self.current_map.layers[0]
        self.data64_LayerObjects  = self.current_map.layers[1]
        self.data64_LayerRoads    = self.current_map.layers[2]
        self.data64_LayerZombies  = self.current_map.layers[3]
        self.data64_LayerFortress = self.current_map.layers[4]
        self.data64_LayerPipes    = self.current_map.layers[5]
        self.data64_LayerBelts    = self.current_map.layers[6]
        
        self.all_entities = self.current_map.entities
        self.map_view.all_entities = self.all_entities  # Pass entities to the map view
        
        self.map_view.set_layer_data('terrain', self.data64_LayerTerrain)
        self.map_view.set_layer_data('objects', self.data64_LayerObjects)
        self.map_view.set_layer_data('zombies', self.data64_LayerZombies)
        self.map_view.set_layer_data('roads', self.data64_LayerRoads)
        self.map_view.set_layer_data('fortress', self.data64_LayerFortress)
        self.map_view.set_layer_data('pipes', self.data64_LayerPipes)
        self.map_view.set_layer_data('belts', self.data64_LayerBelts)
        
        self.map_view.load_zombie_sprites(os.path.join(self.directory, "ZXGame_Data"))
        self.map_view.load_entity_sprites(os.path.join(self.directory, "ZXGame_Data"))
        self.map_view.draw_map()        

class Map:
    def __init__(self, directory, map_name, sevenzip_executable):
        self.directory = directory
        self.sevenzip_executable = sevenzip_executable
        
        self.filename = os.path.basename(map_name)
        print(self.filename)
        self.loaded_folder_path = os.path.join(self.directory)
        self.loaded_original_file_path = map_name
        self.svnzip_unzipped_folder_path = os.path.join(self.directory, "ZXGame_Data\\Levels\\custom_maps_unzipped_no_changes")
        self.unzipped_file_path = os.path.join(self.directory, f"ZXGame_Data\\Levels\\custom_maps_unzipped_no_changes\\{self.filename}")
        
        self.unzipped_modded_folder_path = os.path.join(self.directory, "custom_maps_unzipped")
        self.unzipped_modded_file_path = os.path.join(self.directory, "custom_maps_unzipped", map_name)
        
        self.rezipped_folder_path = os.path.join(self.directory, "ZXGame_Data", "Levels", "custom_maps_backups")
        self.rezipped_file_path = os.path.join(self.directory, "custom_maps", map_name)

        self.file_name = map_name
        self.extract()
        self.parse()
        self.valid_map = self.get_indices()
        if self.valid_map:
            self.pull_layer_strings()
            self.pull_entity_data()

    def extract(self):
        try:
            command = [
                self.sevenzip_executable,
                'x',
                '-y',
                f'-o{self.svnzip_unzipped_folder_path}',
                self.loaded_original_file_path
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if DEBUG:
                print(f'{self.loaded_original_file_path} successfully unzipped to {self.svnzip_unzipped_folder_path}')
        except subprocess.CalledProcessError as e:
            pass
            if DEBUG:
                print(e)
                print(f'{self.loaded_original_file_path} could not be unzipped to {self.svnzip_unzipped_folder_path}')

    def push_new_entity(self,template):
        #inside template into file_data
        for i, line in enumerate(template.split("\n")):
            self.file_data.insert(7+i,line+"\n")
        #pull new indicies for everything
        self.get_indices()
        self.pull_entity_data()

    def update_entity(self,index,template):
        #inside template into file_data
        
        for i, line in enumerate(template[:-1]):
            self.file_data[index+i] = line+"\n"

        #pull new indicies for everything
        self.get_indices()
        self.pull_entity_data()
        return index
    
    def delete_entity(self,index,template):
        #inside template into file_data
        
        for i, line in enumerate(template[:-1]):
            #fail safe for bug when deleting last entry likes to delete these lines for some reason even though the length looks to be correct..
            if i == len(template)-2:
                if "</Items>" in self.file_data[index] or "</Collection>" in self.file_data[index]:
                    print("Tried to delete a bad line... ")
                    continue
            self.file_data.pop(index)

        #pull new indicies for everything
        self.get_indices()
        self.pull_entity_data()
    
    def parse(self):
        self.file_data = []
        try:
            with open(self.unzipped_file_path, 'r') as file:
                self.file_data = file.readlines()
        except FileNotFoundError:
            print(f"Failed to read {self.unzipped_file_path}")

    def get_indices(self):
        #print(self.file_data)
        substring_to_find = "LayerTerrain"
        index = None
        for i, item in enumerate(self.file_data):
            if substring_to_find in item:
                
                index = i
                break
        if index != None:
            self.MapThemeLine = index - 1
            self.LayerTerrainLine = index + 2
            self.LayerObjectsLine = index + 8
            self.LayerRoadsLine = index + 14
            self.LayerZombiesLine = index + 20
            self.LayerFortressLine = index + 26
            self.LayerPipesLine = index + 32
            self.LayerBeltsLine = index + 38
            substring_to_find = "ZX.Entities.CommandCenter, TheyAreBillions"
            index = None
            for i, item in enumerate(self.file_data):
                if substring_to_find in item:
                    index = i
                    self.entity_insterLine = index - 1
                    break
            return True
        else:
            return False
    
    def cell_size_change(self,old_size,new_size):
        self.data_size = new_size
        old_capacity = old_size **2
        new_capacity = new_size **2
        for index, line in enumerate(self.file_data):
            if f'<Simple name="NCells" value="{old_size}' in line:
                self.file_data[index] = self.file_data[index].replace(f'<Simple name="NCells" value="{old_size}',f'<Simple name="NCells" value="{new_size}')
            if f'<Simple name="Capacity" value="{old_capacity}" /' in line:
                self.file_data[index] = self.file_data[index].replace(f'<Simple name="Capacity" value="{old_capacity}" /',f'<Simple name="Capacity" value="{new_capacity}" /')
    
    def pull_layer_strings(self):
        pattern = r'<Simple name="Cells" value="(?P<size>1024|512|256|128)\|(?P=size)\|(?P<data>.+?)" \/>'
        self.data_LayerTerrain = re.search(pattern, self.file_data[self.LayerTerrainLine]).group('data')
        self.data_LayerObjects = re.search(pattern, self.file_data[self.LayerObjectsLine]).group('data')
        self.data_LayerRoads = re.search(pattern, self.file_data[self.LayerRoadsLine]).group('data')
        self.data_LayerZombies = re.search(pattern, self.file_data[self.LayerZombiesLine]).group('data')
        self.data_LayerFortress = re.search(pattern, self.file_data[self.LayerFortressLine]).group('data')
        self.data_LayerPipes = re.search(pattern, self.file_data[self.LayerPipesLine]).group('data')
        self.data_LayerBelts = re.search(pattern, self.file_data[self.LayerBeltsLine]).group('data')

        self.data_size = int(re.search(pattern, self.file_data[self.LayerTerrainLine]).group('size'))

        self.data64_LayerTerrain = self.base64_map_to_array(self.data_LayerTerrain)
        self.data64_LayerObjects = self.base64_map_to_array(self.data_LayerObjects)
        self.data64_LayerRoads = self.base64_map_to_array(self.data_LayerRoads)
        self.data64_LayerZombies = self.base64_map_to_array(self.data_LayerZombies)
        self.data64_LayerFortress = self.base64_map_to_array(self.data_LayerFortress)
        self.data64_LayerPipes = self.base64_map_to_array(self.data_LayerPipes)
        self.data64_LayerBelts = self.base64_map_to_array(self.data_LayerBelts)

        self.layers = [
            self.data64_LayerTerrain,
            self.data64_LayerObjects,
            self.data64_LayerRoads,
            self.data64_LayerZombies,
            self.data64_LayerFortress,
            self.data64_LayerPipes,
            self.data64_LayerBelts
        ]
        
    def push_layer_strings(self):
        start_pattern = '<Simple name="Cells" value="'
        end_pattern = '" />'

        data64_LayerTerrain  = self.array_to_base64_map(self.layers[0])
        data64_LayerObjects  = self.array_to_base64_map(self.layers[1])
        data64_LayerRoads    = self.array_to_base64_map(self.layers[2])
        data64_LayerZombies  = self.array_to_base64_map(self.layers[3])
        data64_LayerFortress = self.array_to_base64_map(self.layers[4])
        data64_LayerPipes    = self.array_to_base64_map(self.layers[5])
        data64_LayerBelts    = self.array_to_base64_map(self.layers[6])
        self.data_LayerTerrain = f'{self.file_data[self.LayerTerrainLine].split(start_pattern, maxsplit=1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerTerrain}{end_pattern}\n'
        self.data_LayerObjects = f'{self.file_data[self.LayerObjectsLine].split(start_pattern, maxsplit=1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerObjects}{end_pattern}\n'
        self.data_LayerRoads   = f'{self.file_data[self.LayerRoadsLine].split(start_pattern, maxsplit=1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerRoads}{end_pattern}\n'
        self.data_LayerZombies = f'{self.file_data[self.LayerZombiesLine].split(start_pattern, maxsplit=1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerZombies}{end_pattern}\n'
        self.data_LayerFortress = f'{self.file_data[self.LayerFortressLine].split(start_pattern, maxsplit=1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerFortress}{end_pattern}\n'
        self.data_LayerPipes = f'{self.file_data[self.LayerPipesLine].split(start_pattern, maxsplit=1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerPipes}{end_pattern}\n'
        self.data_LayerBelts = f'{self.file_data[self.LayerBeltsLine].split(start_pattern, maxsplit=1)[0]}{start_pattern}{str(self.data_size)}|{str(self.data_size)}|{data64_LayerBelts}{end_pattern}\n'

        self.file_data[self.LayerTerrainLine] = self.data_LayerTerrain
        self.file_data[self.LayerObjectsLine] = self.data_LayerObjects
        self.file_data[self.LayerRoadsLine]   = self.data_LayerRoads
        self.file_data[self.LayerZombiesLine] = self.data_LayerZombies
        self.file_data[self.LayerFortressLine] = self.data_LayerFortress
        self.file_data[self.LayerPipesLine] = self.data_LayerPipes
        self.file_data[self.LayerBeltsLine] = self.data_LayerBelts

    def push_new_cc_pos(self, new_y, new_x):
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
            temp_front = self.file_data[cc_pos_index].split("Position", maxsplit=1)[0]
            new_string = f'{temp_front}Position" value="{new_x};{new_y}" />\n'
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
            temp_front = self.file_data[cc_pos_index].split("LastPosition", maxsplit=1)[0]
            new_string = f'{temp_front}LastPosition" value="{new_x};{new_y}" />\n'
            self.file_data[cc_pos_index] = new_string

    def pull_entity_data(self):
        self.entities = {}
        current_entity = ""
        start = False
        complex_count = 0
        first = False

        for index, line in enumerate(self.file_data):
            if "<Items>" in line and not first:
                start = True
                first = True
    
                continue
            if '<Complex name="Extension" type="ZX.GameSystems.ZXLevelExtension, TheyAreBillions">' in line:
                break
            if start == True:

                if '<Complex' in line and 'Properties' in self.file_data[index+1] and "</Properties>" not in self.file_data[index+1]:
                    if complex_count == 0:
                        self.entities[index] = {}
                        self.entities[index] = {'template':[]}
                        current_entity = index

                    complex_count += 1
                        
                elif '/Complex' in line:
                    complex_count -= 1     
            
                self.entities[current_entity]['template'].append(line)
                
                if current_entity and '<Simple name=' in line:
                    simplenameid = line.split('<Simple name=')[1]
                    simplenameid, value = simplenameid.split('value="', maxsplit=1)
                    simplenameid = simplenameid.strip().replace('"', '')
                    if " />" in value:
                        value = value.split(" />")[0]

                    self.entities[current_entity][simplenameid] = value.strip().replace('"', '')
       
        for entity in self.entities.keys():
            if "</Collection>" in self.entities[entity]['template'][-1]:
                self.entities[entity]['template'].pop()
                self.entities[entity]['template'].pop()
                break
                    
        if DEBUG:
            with open(os.path.join(os.getcwd(), "Entities.json"), 'w') as f:
                json.dump(self.entities, f, indent=4)

    def write_to_file(self, file_path):
        #Save Location
        try:
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            
            with open(file_path, 'w') as file:
                for i in range(len(self.file_data)):
                    file.writelines(self.file_data[i])
                         
        except Exception as e:
            print(f"Error writing to file: {e}")
        
        # #Auto Backup Location
        time_stamp = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        temp = os.path.join(f'{self.rezipped_folder_path}', time_stamp ,'unzipped',f'{os.path.basename(file_path)}')

        try:
            if not os.path.exists(os.path.dirname(temp)):
                os.makedirs(os.path.dirname(temp))
            
            with open(temp, 'w') as file:
                for i in range(len(self.file_data)):
                    file.writelines(self.file_data[i])
        
        except Exception as e:
            print(f"Error writing to file: {e}")
        
        try:
            self.zip_files_with_7zip(temp,os.path.join(f'{self.rezipped_folder_path}',time_stamp,'zipped', f'{os.path.basename(file_path)}'))
        except Exception as e:
            print(f'Error backing up file to {e}')

    def base64_map_to_array(self, data):
        decoded_data = base64.b64decode(data)
        output_array = []
        for i in range(0, len(decoded_data), 4):
            int_val = int.from_bytes(decoded_data[i:i+4], byteorder='little')
            output_array.append(int_val)
        return np.array(output_array).reshape((self.data_size, self.data_size))

    def array_to_base64_map(self, data_array):
        
        # Collect bytes in a list to avoid repeated concatenation
        bytes_list = []
        
        for int_val in data_array.flatten():
            bytes_list.append(int(int_val).to_bytes(4, byteorder='little'))
        
        # Join all byte sequences once
        bytes_data = b''.join(bytes_list)
        
        # Base64 encode the bytes
        encoded_data = base64.b64encode(bytes_data)
        encoded_str = encoded_data.decode('utf-8')
        
        return encoded_str

    def zip_files_with_7zip(self, file_path, path_to_save_to):

        command = [
            self.sevenzip_executable,
            'a',
            '-tzip',
            '-mx9',
            path_to_save_to,
            file_path
        ]
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'{self.file_name} Successfully Rezipped')
        except subprocess.CalledProcessError as e:
            print(f"Error compressing file '{self.unzipped_modded_file_path}': {e}")
        
def launch_from_gui(r01, directory, sevenzip_executable):
    app = QApplication(sys.argv)
    launched_map = Map(directory, r01, sevenzip_executable)
    windowclass = MainWindow(launched_map, directory, sevenzip_executable)
    windowclass.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    lines = []
    try:
        with open('entry_values.txt', 'r') as file:
            for line in file:
                lines.append(line)
        
        if len(lines) > 0:
            directory = lines[0].replace("/", "\\").replace("\n", "")
            r01 = os.path.join(directory, "ZXGame_Data", "Levels", "R01.dxlevel")
            
        if len(lines) > 3:
            sevenzip_executable = lines[3].replace("/", "\\").replace("\n", "")
            
    except FileNotFoundError:
        print("No file found trying defaults")
        sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'
        r01 = r"C:\Program Files (x86)\Steam\steamapps\common\They Are Billions\ZXGame_Data\Levels\R01.dxlevel"
        directory = r"C:\Program Files (x86)\Steam\steamapps\common\They Are Billions"

    app = QApplication(sys.argv)
    launched_map = Map(directory, r01, sevenzip_executable)
    windowclass = MainWindow(launched_map, directory, sevenzip_executable)
    windowclass.show()
    sys.exit(app.exec_())
