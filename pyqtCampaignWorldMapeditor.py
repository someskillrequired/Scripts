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

map_file = 'C:/Program Files (x86)/Steam/steamapps/common/They Are Billions/ZXGame_Data/Images/WorldMap/Atlas1_HQ.dat'

class ImageHandler:
    def __init__(self, file, x1, y1, x2, y2, entire_image=None, rotate=0):
        self.file = file
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.rotate = rotate

        if entire_image is None:
            self.entire_image = self.pull_image_data(file)
        else:
            self.entire_image = entire_image

        self.cut_image = self.get_cut_image(self.entire_image, x1, y1, x2, y2)
        self.final_image = self.cut_image

    def pull_image_data(self, file):
        image = Image.open(file)
        image = image.convert("RGBA")

        # Apply brightness filter
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.25)

        # Rotate the image if required
        if self.rotate != 0:
            image = image.rotate(self.rotate, expand=True)

        data = np.array(image)
        height, width, channel = data.shape
        qimage = QImage(data.data, width, height, width * channel, QImage.Format_RGBA8888)
        if qimage.isNull():
            raise ValueError("Failed to load image data. Unsupported format or corrupted file.")
        return QPixmap.fromImage(qimage)

    def get_cut_image(self, entire_image, x1, y1, x2, y2):
        return entire_image.copy(x1, y1, x2 - x1, y2 - y1)

    def scale_image(self, target_width, target_height):
        self.final_image = self.cut_image.scaled(target_width, target_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

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
        for item in self.image_dict:
            if item != "@Map":
                self.item = QGraphicsPixmapItem(self.image_dict[item]['Image'].final_image)
                #print(image_dict[item]['Map_Details']['X'],image_dict[item]['Map_Details']['Y'])
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
        
        print(self.selected_map)
        
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
               
def main():
    app = QApplication(sys.argv)
    
    zxgame_file = ZXGame_Parser(r'C:\Program Files (x86)\Steam\steamapps\common\They Are Billions',r'C:\Program Files (x86)\Steam\steamapps\common\They Are Billions\temp')
    Level1 = zxgame_file.Level1
    
    id_image = {
        "3643163054993724624": "Map",
        "1410269219466599776": "map_type_1",
        "1041987228953333371": "map_type_2",
        "2654636595354274294": "map_type_3",
        "5410779351516259520": "Hero1",
        "3429177597441758845": "Hero2",
        "793800108524638803" : "Hero3",
        "8235020902097885111": "Hero4",
        "6926746045439064138": "Hero5",
        "6326629305443512467": "IC",
        "5216194986254145943": "CraterEmpireCity",
        "2733613961998895088": "LineA"
    }

    entire_image = ImageHandler(map_file, 0, 0, 1, 1).pull_image_data(map_file)
    map_image = ImageHandler(map_file, 0, 0, 3842, 2162, entire_image)
    crater_image = ImageHandler(map_file, 0, 2500, 1920, 3740, entire_image)
    ic_image = ImageHandler(map_file, 0, 3750, 1875, 5600, entire_image)
    map_1_image = ImageHandler(map_file, 3000, 4360, 3500, 4780, entire_image)
    map_2_image = ImageHandler(map_file, 1960, 2740, 2570, 3288, entire_image)
    map_3_image = ImageHandler(map_file, 2580, 3100, 3400, 3800, entire_image)
    hero_1_image = ImageHandler(map_file, 1900, 4600, 2400, 5100, entire_image)
    hero_2_image = ImageHandler(map_file, 2500, 4150, 3000, 4650, entire_image)
    hero_3_image = ImageHandler(map_file, 3700, 4250, 3999, 4475, entire_image)
    hero_4_image = ImageHandler(map_file, 3650, 3050, 3999, 3500, entire_image)
    hero_5_image = ImageHandler(map_file, 3450, 3500, 3999, 3985, entire_image)
    
    image_dict = {
        'Map'             : map_image,
        'CraterEmpireCity': crater_image,
        'IC'              : ic_image,
        'map_type_1'      : map_1_image,
        'map_type_2'      : map_2_image,
        'map_type_3'      : map_3_image,
        'Hero1'           : hero_1_image,
        'Hero2'           : hero_2_image,
        'Hero3'           : hero_3_image,
        'Hero4'           : hero_4_image,
        'Hero5'           : hero_5_image,
    }

    map_data_location = Level1['Clips']['Data']['4104776980463107687']['objects']
    map_detail_location = Level1['Clips']['Data']['4104776980463107687']['frames']

    item_dict = {}
    for image in map_data_location.keys():
        idimage = map_data_location[image].get('IDImage', None)
        if idimage:
            map_details = map_detail_location.get(map_data_location[image]['ID'], None)
            if map_details:
                Height = map_details.get('Height', None)
                Width = map_details.get('Width', None)

                local_image_name = map_data_location[image].get('IDImage', None)
                
                image_name = id_image.get(local_image_name, None)

                global_image = image_dict.get(image_name, None)
                if global_image:
                    item_dict[image] = {}
                    global_image.scale_image(int(float(Width)), int(float(Height)))
                    item_dict[image]['Image']       = global_image
                    item_dict[image]['Map_Details'] = map_details

    main_window = MainWindow(item_dict,zxgame_file)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
