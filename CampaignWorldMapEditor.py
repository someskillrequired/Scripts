import sys
import re
import json
import subprocess
from utilities.image_handler_wme import ImageHandler
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialogButtonBox, QGraphicsView, QGraphicsScene, QMessageBox,
    QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel, QGraphicsRectItem, QGraphicsPixmapItem, 
    QHBoxLayout, QDialog, QLineEdit, QLabel, QTextEdit, QSplitter, QAction
)
from PyQt5.QtGui import QPainter, QPen, QKeySequence
from PyQt5.QtCore import Qt

from utilities.ZXGAME_Processor import ZXGame_Parser
from PyQt5.QtWidgets import QShortcut, QListWidget
from pathlib import Path

sevenzip_executable = 'C:/Program Files/7-Zip/7z.exe'
base_location = 'D:/Steam/steamapps/common/They Are Billions'
base_location_images =f"{base_location}/ZXGame_Data/Images"
ws = 'C:/project_files/Scripts/ws/zxgame_data'

map_file                    = f'{base_location_images}/WorldMap/Atlas1_HQ.dat'
map_file_atlas              = f'{base_location_images}/WorldMap/Atlas1_HQ.dxatlas'
interface_file              = f'{base_location_images}/Interface/Atlas1_HQ.dat'
interface_file_atlas        = f'{base_location_images}/Interface/Atlas1_HQ.dxatlas'
map_file_atlas_folder       = f'{ws}/WorldMap'
interface_file_atlas_folder = f'{ws}/Interface'
map_atlas_unzipped          = f'{map_file_atlas_folder}/Atlas1_HQ.dxatlas'
interface_atlas_unzipped    = f'{interface_file_atlas_folder}/Atlas1_HQ.dxatlas'

class MainWindow(QMainWindow):
    def __init__(self, image_dict, zxgame_file):
        super().__init__()
        self.zxgame_file = zxgame_file
        self.image_dict = image_dict
        self.selected_item = None
        self.selection_rect = None 
        self.setWindowTitle("Global Map Viewer")
        self.setGeometry(100, 100, 1920, 1080)

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
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.layout.addWidget(self.view)
        
        # Add the GlobalMap image as a layer
        self.add_global_map_layer()
        
        # Add the IC image as a layer
        self.add_ic_map_layer()
        
        self.create_arrow_shortcuts()
        self.create_delete_shortcut()
        self.create_menu_bar()
        self.create_combined_control_panel()
    
    def create_combined_control_panel(self):
        """Create a combined control panel with scrollable items"""
        # Create a splitter for main layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Map view
        map_container = QWidget()
        map_layout = QVBoxLayout(map_container)
        map_layout.addWidget(self.view)
        
        # Right side - Controls
        control_container = QWidget()
        control_layout = QVBoxLayout(control_container)
        
        # Scrollable item list
        self.item_list = QListWidget()
        self.item_list.setSelectionMode(QListWidget.SingleSelection)
        self.populate_item_list()
        self.item_list.itemSelectionChanged.connect(self.on_item_selected)
        
        # Property editor
        self.property_editor = QTextEdit()
        self.property_editor.setReadOnly(False)
        
        # Add/Edit controls
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New")
        self.add_button.clicked.connect(self.add_new_item)
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_properties)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.save_button)
        
        # Add widgets to control layout
        control_layout.addWidget(QLabel("Map Items:"))
        control_layout.addWidget(self.item_list)
        control_layout.addWidget(QLabel("Properties:"))
        control_layout.addWidget(self.property_editor)
        control_layout.addLayout(button_layout)
        
        # Add to splitter
        splitter.addWidget(map_container)
        splitter.addWidget(control_container)
        splitter.setSizes([800, 400])  # Adjust initial sizes
        
        # Set as central widget
        self.layout.addWidget(splitter)
        
    def populate_item_list(self):
        """Populate the scrollable item list, excluding deleted items"""
        self.item_list.clear()
        for key in sorted(self.image_dict.keys()):
            if key != "@Map":
                # Skip deleted items
                if 'Modified' in self.image_dict[key]['Map_Details']:
                    if self.image_dict[key]['Map_Details']['Modified'] == 'Deleted':
                        continue
                self.item_list.addItem(key)
                
    def on_item_selected(self):
        """Handle item selection from the list"""
        selected = self.item_list.selectedItems()
        if selected:
            self.selected_item = selected[0].text()
            self.update_property_editor()
            self.highlight_selected_item()

    def highlight_selected_item(self):
        """Highlight the currently selected item on the map"""
        # Clear any existing selection rectangle
        if self.selection_rect and self.selection_rect in self.scene.items():
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None
        
        # If we have a valid selection, create a new highlight rectangle
        if self.selected_item and self.selected_item in self.image_dict:
            details = self.image_dict[self.selected_item]['Map_Details']
            
            # Create red border rectangle around selected item
            self.selection_rect = QGraphicsRectItem(
                float(details['X']),
                float(details['Y']),
                float(details['Width']),
                float(details['Height'])
            )
            # Customize the appearance
            pen = QPen(Qt.red)
            pen.setWidth(3)
            pen.setStyle(Qt.SolidLine)
            self.selection_rect.setPen(pen)
            
            # Add to scene (on top of other items)
            self.selection_rect.setZValue(1)
            self.scene.addItem(self.selection_rect)
            
            # Center view on the selected item if it's not fully visible
            view_rect = self.view.mapToScene(self.view.viewport().geometry()).boundingRect()
            item_rect = self.selection_rect.rect()
            if not view_rect.contains(item_rect):
                self.view.centerOn(self.selection_rect)

    def create_property_editor(self):
        """Create the property editor section"""
        # Create a splitter to separate map view and property editor
        splitter = QSplitter(Qt.Horizontal)
        
        # Create container for the map view
        map_container = QWidget()
        map_layout = QVBoxLayout(map_container)
        map_layout.addWidget(self.view)
        
        # Create property editor
        self.property_editor = QTextEdit()
        self.property_editor.setReadOnly(False)
        self.property_editor.setMinimumWidth(300)
        
        # Save button for properties
        self.save_properties_button = QPushButton("Save Properties")
        self.save_properties_button.clicked.connect(self.save_properties)
        
        # Layout for property editor
        property_container = QWidget()
        property_layout = QVBoxLayout(property_container)
        property_layout.addWidget(QLabel("Item Properties:"))
        property_layout.addWidget(self.property_editor)
        property_layout.addWidget(self.save_properties_button)
        
        # Add widgets to splitter
        splitter.addWidget(map_container)
        splitter.addWidget(property_container)
        
        # Replace the main layout's widget with the splitter
        self.layout.addWidget(splitter)
    
    def add_new_item(self):
        """Add new item with template selection"""
        # Create dialog for template selection
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Item")
        layout = QVBoxLayout(dialog)
        
        # Template selection
        template_combo = QComboBox()
        template_combo.addItem("-- Select Template --")
        for key in sorted(self.image_dict.keys()):
            if key != "@Map":
                template_combo.addItem(key)
        
        # Name input
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter unique name")
        
        # Position inputs
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        x_edit = QLineEdit("100")
        pos_layout.addWidget(x_edit)
        pos_layout.addWidget(QLabel("Y:"))
        y_edit = QLineEdit("100")
        pos_layout.addWidget(y_edit)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Add to layout
        layout.addWidget(QLabel("Select Template:"))
        layout.addWidget(template_combo)
        layout.addWidget(QLabel("New Item Name:"))
        layout.addWidget(name_edit)
        layout.addWidget(QLabel("Initial Position:"))
        layout.addLayout(pos_layout)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            template_name = template_combo.currentText()
            new_name = name_edit.text().strip()
            
            if template_name == "-- Select Template --":
                QMessageBox.warning(self, "Warning", "Please select a template!")
                return
                
            if not new_name:
                QMessageBox.warning(self, "Warning", "Please enter a name!")
                return
                
            if new_name in self.image_dict:
                QMessageBox.warning(self, "Warning", "Name already exists!")
                return
                
            # Get template data without deep copying
            template_data = self.image_dict[template_name]
            
            # Create new item by reconstructing from template
            new_item = {
                'Map_Details': {
                    key: str(value) for key, value in template_data['Map_Details'].items()
                    if key != 'template'  # We'll reconstruct this
                },
                'image_name': template_data['image_name'],
                'Image': ImageHandler(
                    template_data['Image'].file,
                    template_data['Image'].x1,
                    template_data['Image'].y1,
                    template_data['Image'].x2,
                    template_data['Image'].y2,
                    rotate=template_data['Image'].rotate
                )
            }
            
            # Update properties for new item
            details = new_item['Map_Details']
            details['Name'] = new_name
            details['X'] = x_edit.text()
            details['Y'] = y_edit.text()
            details['Modified'] = "Added"
            
            # Reconstruct the template lines if needed
            if 'template' in template_data['Map_Details']:
                new_item['Map_Details']['template'] = [
                    line.replace(template_name, new_name)
                    for line in template_data['Map_Details']['template']
                ]
            
            # Scale the image
            new_item['Image'].scale_image(
                int(float(details['Width'])),
                int(float(details['Height']))
            )
            
            # Add to dictionary
            self.image_dict[new_name] = new_item
            
            # Refresh UI
            self.populate_item_list()
            self.scene.clear()
            self.add_global_map_layer()
            self.add_ic_map_layer()
            
            # Select the new item
            for i in range(self.item_list.count()):
                if self.item_list.item(i).text() == new_name:
                    self.item_list.setCurrentRow(i)
                    break

    def create_menu_bar(self):
        """Create the menu bar with File dropdown"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # Save action
        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save changes')
        save_action.triggered.connect(self.save_changes)
        file_menu.addAction(save_action)
        
        # Exit action
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def save_changes(self):
        """Handle saving changes to the ZXGame file"""
        self.zxgame_file.save_file(self.image_dict)
        QMessageBox.information(self, "Save", "Changes saved successfully!", QMessageBox.Ok)

    def add_global_map_layer(self):
        
        self.global_map_item = QGraphicsPixmapItem(self.image_dict['@Map']['Image'].final_image)
        self.global_map_item.setPos(0,0)
        self.scene.addItem(self.global_map_item)

    def add_ic_map_layer(self):
        # Store selection info before clearing
        selected_info = None
        
        if self.selected_item and self.selected_item in self.image_dict:
            details = self.image_dict[self.selected_item]['Map_Details']
            selected_info = {
                'x': float(details['X']),
                'y': float(details['Y']),
                'width': float(details['Width']),
                'height': float(details['Height'])
            }
        
        # Add all items
        for item in self.image_dict:
            if 'Modified' in self.image_dict[item]['Map_Details']:
                if self.image_dict[item]['Map_Details']['Modified'] == 'Deleted':
                    continue
            if item == "@Map":
                continue

            pixmap_item = QGraphicsPixmapItem(self.image_dict[item]['Image'].final_image)
            x_pos = float(self.image_dict[item]['Map_Details']['X'])
            y_pos = float(self.image_dict[item]['Map_Details']['Y'])
            pixmap_item.setPos(x_pos, y_pos)
            
            self.scene.addItem(pixmap_item)
        
        # Recreate selection rectangle if needed
        if selected_info:
            self.selection_rect = QGraphicsRectItem(
                selected_info['x'],
                selected_info['y'],
                selected_info['width'],
                selected_info['height']
            )
            self.selection_rect.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            self.scene.addItem(self.selection_rect) 

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Map the view coordinates to scene coordinates
            
            scene_pos = self.view.mapToScene(event.pos())
            adjustedx = scene_pos.x()-18
            adjustedy = scene_pos.y()-18

            self.handle_mouse_click(adjustedx, adjustedy) 

    def handle_mouse_click(self, x, y):
        """Improved item selection with early exits and minimal nesting."""
        # --- Remove old highlight ---
        if self.selection_rect and self.selection_rect in self.scene.items():
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None

        new_item = None
        # --- Find the first valid clicked item ---
        
        for key, data in self.image_dict.items():
            if key == "@Map":
                continue
            item_x = float(data['Map_Details']['X'])
            item_y = float(data['Map_Details']['Y'])
            item_w = float(data['Map_Details']['Width'])
            item_h = float(data['Map_Details']['Height'])

            if (item_x <= x <= (item_x + item_w) and 
                item_y <= y <= (item_y + item_h)):
                new_item = key
                break
        
        if self.selected_item == new_item:
            self.highlight_selected_item()
            return
        
        self.selected_item = new_item
        
        # --- Update UI state ---
        if not self.selected_item:
            self.item_list.clearSelection()
            self.property_editor.clear()
            print(f"self.selected item {self.selected_item}")
            self.selected_item = None
            return 

        # --- Sync QListWidget selection ---
        for i in range(self.item_list.count()):
            if self.item_list.item(i).text() == self.selected_item:
                self.item_list.setCurrentRow(i)
                break

    def update_property_editor(self):
        """Update the property editor with current item's properties"""
        if not self.selected_item or self.selected_item not in self.image_dict:
            self.property_editor.clear()
            return
            
        details = self.image_dict[self.selected_item]['Map_Details']
        
        # Convert properties to JSON for easy editing
        properties = {
            'name': self.selected_item,
            'position': {
                'x': details.get('X', '0'),
                'y': details.get('Y', '0')
            },
            'size': {
                'width': details.get('Width', '0'),
                'height': details.get('Height', '0')
            },
            'image': self.image_dict[self.selected_item].get('image_name', ''),
            'other_properties': {k: v for k, v in details.items() 
                               if k not in ['X', 'Y', 'Width', 'Height', 'template']}
        }
        
        self.property_editor.setPlainText(json.dumps(properties, indent=4))
        
    def save_properties(self):
        """Save edited properties back to the item"""
        print("in save")
        if not self.selected_item:
            print(f"self.selected item {self.selected_item}")
            print("cant save 1")
            return
        if self.selected_item not in self.image_dict:
            print("cant save 2")
            return
            
        try:
            # Parse the edited JSON
            new_properties = json.loads(self.property_editor.toPlainText())
            
            # Update basic properties
            details = self.image_dict[self.selected_item]['Map_Details']
            details['X'] = str(new_properties['position']['x'])
            details['Y'] = str(new_properties['position']['y'])
            details['Width'] = str(new_properties['size']['width'])
            details['Height'] = str(new_properties['size']['height'])
            
            # Update other properties
            for key, value in new_properties['other_properties'].items():
                details[key] = str(value)
                
            # Mark as modified
            details['Modified'] = "Moved"
            
            # Refresh display
            self.scene.clear()
            self.add_global_map_layer()
            self.add_ic_map_layer()
            
            QMessageBox.information(self, "Success", "Properties saved!")
            
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Invalid JSON format!")
        except KeyError as e:
            QMessageBox.warning(self, "Error", f"Missing required field: {e}")
        
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

        if not self.selected_item or self.selected_item not in self.image_dict:
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

        if self.selection_rect and self.selection_rect in self.scene.items():
            details = self.image_dict[self.selected_item]['Map_Details']
            self.selection_rect.setRect(
                float(details['X']),
                float(details['Y']),
                float(details['Width']),
                float(details['Height'])
                
            )
            

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
        
        self.image_dict[self.selected_item]['Map_Details']['X']        = str(format_num(float(self.image_dict[self.selected_item]['Map_Details']['X']) + x_offset))
        self.image_dict[self.selected_item]['Map_Details']['Y']        = str(format_num(float(self.image_dict[self.selected_item]['Map_Details']['Y']) + y_offset))
        self.image_dict[self.selected_item]['Map_Details']['Location'] = self.image_dict[self.selected_item]['Map_Details']['X'] + ';' + self.image_dict[self.selected_item]['Map_Details']['Y']
        self.image_dict[self.selected_item]['Map_Details']['CenterX']  = str(format_num(float(self.image_dict[self.selected_item]['Map_Details']['CenterX']) + x_offset))
        self.image_dict[self.selected_item]['Map_Details']['CenterY']  = str(format_num(float(self.image_dict[self.selected_item]['Map_Details']['CenterY']) + y_offset))
        self.image_dict[self.selected_item]['Map_Details']['Center']   = self.image_dict[self.selected_item]['Map_Details']['CenterX'] + ';' + self.image_dict[self.selected_item]['Map_Details']['CenterY']
        self.image_dict[self.selected_item]['Map_Details']['template'] = reconstruct_template(self.image_dict[self.selected_item]['Map_Details']['template'], self.image_dict[self.selected_item]['Map_Details'])
        self.image_dict[self.selected_item]['Map_Details']['Modified'] = 'Moved'
        self.scene.clear()
        self.add_global_map_layer()
        self.add_ic_map_layer()

    def handle_delete_key(self):
        """Handle deleting the currently selected item"""
        if self.selected_item and self.selected_item in self.image_dict:
            # Mark as deleted in the data structure
            self.image_dict[self.selected_item]['Map_Details']['Modified'] = 'Deleted'
            
            # Remove from the list widget
            items = self.item_list.findItems(self.selected_item, Qt.MatchExactly)
            if items:
                row = self.item_list.row(items[0])
                self.item_list.takeItem(row)
            
            # Clear selection
            self.selected_item = None
            self.property_editor.clear()
            
            # Refresh the display
            self.scene.clear()
            self.add_global_map_layer()
            self.add_ic_map_layer()

    def add_item(self):
        #Needs a new map
        if self.selected_item in self.image_dict:
            self.image_dict[self.selected_item]['Map_Details']['Modified'] = 'Added'

def unzip(file,output_location):
        command = [
        sevenzip_executable,
        'x',
        '-y',
        f'-o{output_location}',
        file
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def atlas_parsing(file_path) -> dict:
    atlas_dict = {}
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

def load_all_atlases():
    """
    Unzip and parse both map and interface atlases, returning a merged atlas dictionary.
    """
    unzip(map_file_atlas, map_file_atlas_folder)
    unzip(interface_file_atlas, interface_file_atlas_folder)

    atlas_map = atlas_parsing(map_atlas_unzipped)
    atlas_int = atlas_parsing(interface_atlas_unzipped)

    return atlas_map | atlas_int

def load_source_images():
    """
    Load the full image data for both map and interface atlases.
    """
    return {
        "WorldMap": ImageHandler(map_file, 0, 0, 1, 1).entire_image,
        "Interface": ImageHandler(interface_file, 0, 0, 1, 1).entire_image,
    }

def extract_map_data(Level1):
    """
    Extract map object and frame data from the game Level1 dictionary.
    """
    data = Level1["Clips"]["Data"]["4104776980463107687"]
    return data["objects"], data["frames"]

def build_image_dict(objects, frames, Level1, atlas, images):
    """
    Build a dictionary mapping image identifiers to their processed ImageHandler instances.
    """
    my_image_dict = {}
    no_image_id = []
    no_image_file = []

    for name, data in objects.items():
        # --- Guard clauses for missing info ---
        if "IDImage" not in data:
            no_image_id.append(name)
            continue

        id_image = data["IDImage"]
        if id_image not in Level1["my_reversed_dict"]:
            no_image_file.append(id_image)
            continue

        # --- Extract path and file info ---
        path = Level1["my_reversed_dict"][id_image]
        image_name = Path(path).name
        image_location = Path(path).parent.name

        if image_name not in atlas:
            print(f"[WARN] Image not found in atlas: {image_name}")
            continue

        if data["ID"] not in frames:
            continue

        # --- Determine the correct source image ---
        src_image = images.get(image_location)
        if src_image is None:
            print(f"[WARN] Unknown image location: {image_location}")
            continue

        temp = atlas[image_name]

        # --- Build image handler ---
        handler = ImageHandler(
            map_file if image_location == "WorldMap" else interface_file,
            int(temp["x"]),
            int(temp["y"]),
            int(temp["w"]),
            int(temp["h"]),
            src_image,
        )

        # --- Scale according to map details ---
        details = frames[data["ID"]]
        handler.scale_image(
            int(float(details["Width"])),
            int(float(details["Height"])),
        )

        # --- Store result ---
        my_image_dict[name] = {
            "Map_Details": details,
            "Image": handler,
            "image_name": image_name,
        }

    return my_image_dict

def load_images(zxgame_file):
    """
    Orchestrates the full loading of game images from ZXGame data.
    """
    Level1 = zxgame_file.Level1

    # --- Step 1: Load atlases ---
    atlas = load_all_atlases()

    # --- Step 2: Load source images ---
    images = load_source_images()

    # --- Step 3: Extract object/frame data ---
    objects, frames = extract_map_data(Level1)

    # --- Step 4: Build image dictionary ---
    my_image_dict = build_image_dict(objects, frames, Level1, atlas, images)

    return my_image_dict

def main():
    app = QApplication(sys.argv)
    zxgame_file = ZXGame_Parser(base_location,ws)
    map_images = load_images(zxgame_file)

    main_window = MainWindow(map_images,zxgame_file)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
