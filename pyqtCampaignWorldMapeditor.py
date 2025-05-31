import sys
import numpy as np
from PIL import Image, ImageEnhance
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox,
    QPushButton, QVBoxLayout, QWidget, QSlider, QComboBox, QLabel, QGraphicsRectItem, QGraphicsPixmapItem,
    QTabWidget, QHBoxLayout, QLineEdit, QLabel, QGraphicsItemGroup, QSizePolicy, QTextEdit, QSplitter, QMenu, QMenuBar, QAction
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QBrush, QPen, QKeySequence
from PyQt5.QtCore import QRectF, Qt, QSize, QPoint
import copy
from pyqt_ZXGAME_Processor import ZXGame_Parser
from PyQt5.QtWidgets import QShortcut
import re

base_location = 'C:/Program Files (x86)/Steam/steamapps/common/They Are Billions/ZXGame_Data/Images'

map_file             = f'{base_location}/WorldMap/Atlas1_HQ.dat'
map_file_atlas       = f'{base_location}/WorldMap/Atlas1_HQ/Atlas1_HQ.dxatlas'
interface_file       = f'{base_location}/Interface/Atlas1_HQ.dat'
interface_file_atlas = f'{base_location}/Interface/Atlas1_HQ/Atlas1_HQ.dxatlas' 

class ImageHandler:
    def __init__(self, file, x1, y1, x2, y2, entire_image=None, rotate=0):
        self.file = file
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.rotate = rotate

        # Load the entire image first
        if entire_image is None:
            self.entire_image = self.load_entire_image(file)
        else:
            self.entire_image = entire_image

        # Then get the cut image
        self.cut_image = self.get_cut_image(self.entire_image, x1, y1, x2, y2)
        
        # Store the original cut image before any scaling
        self.original_cut = self.cut_image
        
        # Initialize final image
        self.final_image = self.cut_image

    def load_entire_image(self, file):
        """Load the entire atlas image with rotation if needed"""
        image = Image.open(file)
        image = image.convert("RGBA")

        # Apply brightness filter
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.25)

        # Rotate the image if required
        if self.rotate != 0:
            image = image.rotate(self.rotate, expand=True)

        # Convert to QPixmap
        data = np.array(image)
        height, width, channel = data.shape
        qimage = QImage(data.data, width, height, width * channel, QImage.Format_RGBA8888)
        if qimage.isNull():
            raise ValueError("Failed to load image data. Unsupported format or corrupted file.")
        return QPixmap.fromImage(qimage)

    def get_cut_image(self, entire_image, x1, y1, x2, y2):
        """Crop a portion from the entire image"""
        # Ensure coordinates are within bounds
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(entire_image.width(), int(x2))
        y2 = min(entire_image.height(), int(y2))
        x2 = x1 + x2
        y2 = y1 + y2
        # Ensure valid dimensions
        if x2 <= x1 or y2 <= y1:
            return entire_image.copy()  # fallback to full image
            
        return entire_image.copy(x1, y1, x2 - x1, y2 - y1)

    def scale_image(self, target_width, target_height):
        """Scale the already cropped image"""
        if target_width <= 0 or target_height <= 0:
            print(f"Invalid target dimensions: {target_width}x{target_height}")
            return
            
        self.target_width = target_width
        self.target_height = target_height
        self.final_image = self.cut_image.scaled(
            target_width, 
            target_height, 
            Qt.IgnoreAspectRatio, 
            Qt.SmoothTransformation
        )

class MainWindow(QMainWindow):
    def __init__(self, image_dict, zxgame_file):
        super().__init__()
        self.zxgame_file = zxgame_file
        self.image_dict = image_dict

        self.setWindowTitle("Global Map Viewer")
        self.setGeometry(100, 100, 2660, 1272)

        # Create a QWidget to hold the layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a QVBoxLayout to manage the layout
        self.layout = QVBoxLayout(self.central_widget)

        # Create a QGraphicsView
        self.view = QGraphicsView(self.central_widget)
    
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)

        # Create a QGraphicsScene
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.layout.addWidget(self.view)
        
        # Add the GlobalMap image as a layer
        self.add_global_map_layer()
        
        # Add the IC image as a layer
        self.add_ic_map_layer()
        
        self.create_arrow_shortcuts()
        self.create_delete_shortcut()
        
    def add_global_map_layer(self):
        self.global_map_item = QGraphicsPixmapItem(self.image_dict['@Map']['Image'].final_image)
        self.scene.addItem(self.global_map_item)

    def add_ic_map_layer(self):
        pass
        for item in self.image_dict:
            if item != "@Map":
                self.item = QGraphicsPixmapItem(self.image_dict[item]['Image'].final_image)
                self.item.setPos(float(self.image_dict[item]['Map_Details']['X']), float(self.image_dict[item]['Map_Details']['Y']))
                self.scene.addItem(self.item)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            self.handle_mouse_click(pos.x(), pos.y())  
    
    def handle_mouse_click(self,x,y):
        
        def point_in_boxes_dict(px, py, boxes_dict):
            for key, box in boxes_dict.items():
                min_x = float(box['Map_Details']["X"])
                max_x = float(box['Map_Details']["X"]) + float(box['Map_Details']["Width"])
                min_y = float(box['Map_Details']["Y"])
                max_y = float(box['Map_Details']["Y"]) + float(box['Map_Details']["Height"])
                if min_x <= px <= max_x and min_y <= py <= max_y and key != '@Map':
                    return key

        self.selected_map = point_in_boxes_dict(x,y,self.image_dict)
        
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

        # Ensure Entity Selected
        if not self.selected_map:
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
        
        
        def reconstruct_template(template, data):
            new_template = []
            simple_pattern = re.compile(r'<Simple name="([^"]+)" value="([^"]+)"')

            for line in template:
                matches = simple_pattern.findall(line)
                if matches: 
                    for name, _ in matches:
                        if name in data:
                            value = data[name]
                            try:
                                temp_str = 'value="'
                                simple,old_value = line.split(temp_str,maxsplit=1)
                                line = simple + temp_str + str(value) + '" />\n'
                            except:
                                print(f'failed to update line {line}')
        
                new_template.append(line)
            return new_template
        
        def format_num(num):
            return format(num, '.3f')
        
        self.image_dict[self.selected_map]['Map_Details']['X']        = str(format_num(float(self.image_dict[self.selected_map]['Map_Details']['X']) + x_offset))
        self.image_dict[self.selected_map]['Map_Details']['Y']        = str(format_num(float(self.image_dict[self.selected_map]['Map_Details']['Y']) + y_offset))
        self.image_dict[self.selected_map]['Map_Details']['Location'] = self.image_dict[self.selected_map]['Map_Details']['X'] + ';' + self.image_dict[self.selected_map]['Map_Details']['Y']
        self.image_dict[self.selected_map]['Map_Details']['CenterX']  = str(format_num(float(self.image_dict[self.selected_map]['Map_Details']['CenterX']) + x_offset))
        self.image_dict[self.selected_map]['Map_Details']['CenterY']  = str(format_num(float(self.image_dict[self.selected_map]['Map_Details']['CenterY']) + y_offset))
        self.image_dict[self.selected_map]['Map_Details']['Center']   = self.image_dict[self.selected_map]['Map_Details']['CenterX'] + ';' + self.image_dict[self.selected_map]['Map_Details']['CenterY']
        self.image_dict[self.selected_map]['Map_Details']['template'] = reconstruct_template(self.image_dict[self.selected_map]['Map_Details']['template'], self.image_dict[self.selected_map]['Map_Details'])
        self.image_dict[self.selected_map]['Map_Details']['MODIFIED'] = True
        
        self.scene.clear()
        self.add_global_map_layer()
        self.add_ic_map_layer()
    
    def handle_delete_key(self):
        self.image_dict = self.zxgame_file.update_file(self.image_dict)

def atlas_parsing(atlas_dict,file_path) -> dict:
    with open(file_path) as file:
        lines = file.readlines()

    for index, line in enumerate(lines):
        if '<Simple name="n" value="' in line:
            match = re.search(r'<Simple\s+name="n"[^>]*\svalue="([^"]+)"', line)
            atlas_dict[str(match.group(1))] = {}
            for subline in lines[index+1:]:
                
                if '<Simple name="n" value="' in subline:
                    break

                else:
                    submatch = re.search(r'<Simple\s+name="([^"]+)"\s+value="([^"]+)"', subline)
                    if submatch:
                        atlas_dict[str(match.group(1))][str(submatch.group(1))] = str(submatch.group(2))
    
    return atlas_dict

def main():
    app = QApplication(sys.argv)
    
    zxgame_file = ZXGame_Parser(r'C:\Program Files (x86)\Steam\steamapps\common\They Are Billions',r'C:\Program Files (x86)\Steam\steamapps\common\They Are Billions\temp')
    Level1 = zxgame_file.Level1
    image_atlas = {}
    image_atlas = atlas_parsing(image_atlas,map_file_atlas)
    image_atlas = atlas_parsing(image_atlas,interface_file_atlas)

    map_entire_image = ImageHandler(map_file, 0, 0, 1, 1).entire_image
    interface_entire_image =ImageHandler(interface_file, 0, 0, 1, 1).entire_image

    map_data_location = Level1['Clips']['Data']['4104776980463107687']['objects']
    map_detail_location = Level1['Clips']['Data']['4104776980463107687']['frames']

    no_image_id   = []
    no_image_file = []
    my_image_dict = {}
    
    for image in map_data_location:
        if 'IDImage' in map_data_location[image]:
            if map_data_location[image]['IDImage'] in Level1['my_reversed_dict']:
                if Level1['my_reversed_dict'][map_data_location[image]['IDImage']].rsplit('\\',1)[1] in image_atlas:
                    if map_data_location[image]['ID'] in map_detail_location:
                        my_image_dict[image] = {}
                        my_image_dict[image]['Map_Details'] = map_detail_location[map_data_location[image]['ID']]
                        image_location = Level1['my_reversed_dict'][map_data_location[image]['IDImage']].rsplit('\\',1)[0].rsplit('\\',1)[1]
                        image_name = Level1['my_reversed_dict'][map_data_location[image]['IDImage']].rsplit('\\',1)[1]
                        temp = image_atlas[image_name]
                        if image_location == 'WorldMap':
                            full_image = ImageHandler(map_file,int(temp['x']),int(temp['y']),int(temp['w']),int(temp['h']),map_entire_image)

                        elif image_location == 'Interface':
                            full_image = ImageHandler(interface_file,int(temp['x']),int(temp['y']),int(temp['w']),int(temp['h']),interface_entire_image)
                        else:
                            print(f'image location {image_location} not found')
                            break
                            
                        full_image.scale_image(int(float(my_image_dict[image]['Map_Details']['Width'])),int(float(my_image_dict[image]['Map_Details']['Height'])))
                        my_image_dict[image]['Image'] = full_image
                        my_image_dict[image]['image_name'] = Level1['my_reversed_dict'][map_data_location[image]['IDImage']].rsplit('\\',1)[1]

                    else:
                        print('not on map')
                else:
                    print('not_found')
                    
            else:
                no_image_file.append(image['IDImage'])
        else:
            no_image_id.append(image)


    main_window = MainWindow(my_image_dict,zxgame_file)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
