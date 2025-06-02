import sys
import numpy as np
from PIL import Image, ImageEnhance
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialogButtonBox, QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox,
    QPushButton, QVBoxLayout, QWidget, QSlider, QComboBox, QLabel, QGraphicsRectItem, QGraphicsPixmapItem,
    QTabWidget, QHBoxLayout, QDialog, QInputDialog, QLineEdit, QLabel, QGraphicsItemGroup, QSizePolicy, QTextEdit, QSplitter, QMenu, QMenuBar, QAction
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QBrush, QPen, QKeySequence
from PyQt5.QtCore import QRectF, Qt, QSize, QPoint, QPointF
import copy
from pyqt_ZXGAME_Processor import ZXGame_Parser
from PyQt5.QtWidgets import QShortcut, QInputDialog, QListWidget
import re
import json

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
        self.selected_map = None
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
            self.selected_map = selected[0].text()
            self.update_property_editor()
            self.highlight_selected_item()

    def highlight_selected_item(self):
        """Highlight the currently selected item on the map"""
        # Clear any existing selection rectangle
        if self.selection_rect and self.selection_rect in self.scene.items():
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None
        
        # If we have a valid selection, create a new highlight rectangle
        if self.selected_map and self.selected_map in self.image_dict:
            details = self.image_dict[self.selected_map]['Map_Details']
            
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
        self.scene.addItem(self.global_map_item)

    def add_ic_map_layer(self):
        # Store selection info before clearing
        selected_info = None
        
        if self.selected_map and self.selected_map in self.image_dict:
            details = self.image_dict[self.selected_map]['Map_Details']
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
            self.handle_mouse_click(scene_pos.x(), scene_pos.y()) 

    def handle_mouse_click(self, x, y):
        """Improved item selection with accurate hit testing"""
        if self.selection_rect and self.selection_rect in self.scene.items():
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None
        
        self.selected_map = None
        
        # Find all items at the click position
        items = self.scene.items(QPointF(x, y), Qt.IntersectsItemShape, Qt.DescendingOrder)
        
        # Filter for pixmap items (excluding the base map)
        for item in items:
            if isinstance(item, QGraphicsPixmapItem) and item != self.global_map_item:
                # Find which map item this belongs to
                for key, data in self.image_dict.items():
                    if key == "@Map":
                        continue
                    item_x = float(data['Map_Details']['X'])
                    item_y = float(data['Map_Details']['Y'])
                    item_width = float(data['Map_Details']['Width'])
                    item_height = float(data['Map_Details']['Height'])
                    
                    # Accurate hit test using item bounds
                    if (item_x <= x <= item_x + item_width and 
                        item_y <= y <= item_y + item_height):
                        self.selected_map = key
                        break
                
                if self.selected_map:
                    # Update list selection
                    for i in range(self.item_list.count()):
                        if self.item_list.item(i).text() == self.selected_map:
                            self.item_list.setCurrentRow(i)
                            break
                    
                    # Draw selection rectangle
                    details = self.image_dict[self.selected_map]['Map_Details']
                    self.selection_rect = QGraphicsRectItem(
                        float(details['X']),
                        float(details['Y']),
                        float(details['Width']),
                        float(details['Height'])
                    )
                    self.selection_rect.setPen(QPen(Qt.red, 3, Qt.SolidLine))
                    self.scene.addItem(self.selection_rect)
                    self.update_property_editor()
                    break

        

    def update_property_editor(self):
        """Update the property editor with current item's properties"""
        if not self.selected_map or self.selected_map not in self.image_dict:
            self.property_editor.clear()
            return
            
        details = self.image_dict[self.selected_map]['Map_Details']
        
        # Convert properties to JSON for easy editing
        properties = {
            'name': self.selected_map,
            'position': {
                'x': details.get('X', '0'),
                'y': details.get('Y', '0')
            },
            'size': {
                'width': details.get('Width', '0'),
                'height': details.get('Height', '0')
            },
            'image': self.image_dict[self.selected_map].get('image_name', ''),
            'other_properties': {k: v for k, v in details.items() 
                               if k not in ['X', 'Y', 'Width', 'Height', 'template']}
        }
        
        self.property_editor.setPlainText(json.dumps(properties, indent=4))
        
    def save_properties(self):
        """Save edited properties back to the item"""
        if not self.selected_map or self.selected_map not in self.image_dict:
            return
            
        try:
            # Parse the edited JSON
            new_properties = json.loads(self.property_editor.toPlainText())
            
            # Update basic properties
            details = self.image_dict[self.selected_map]['Map_Details']
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

        if not self.selected_map or self.selected_map not in self.image_dict:
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
            details = self.image_dict[self.selected_map]['Map_Details']
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
        
        print(self.image_dict[self.selected_map]['Map_Details']['template'])
        self.image_dict[self.selected_map]['Map_Details']['X']        = str(format_num(float(self.image_dict[self.selected_map]['Map_Details']['X']) + x_offset))
        self.image_dict[self.selected_map]['Map_Details']['Y']        = str(format_num(float(self.image_dict[self.selected_map]['Map_Details']['Y']) + y_offset))
        self.image_dict[self.selected_map]['Map_Details']['Location'] = self.image_dict[self.selected_map]['Map_Details']['X'] + ';' + self.image_dict[self.selected_map]['Map_Details']['Y']
        self.image_dict[self.selected_map]['Map_Details']['CenterX']  = str(format_num(float(self.image_dict[self.selected_map]['Map_Details']['CenterX']) + x_offset))
        self.image_dict[self.selected_map]['Map_Details']['CenterY']  = str(format_num(float(self.image_dict[self.selected_map]['Map_Details']['CenterY']) + y_offset))
        self.image_dict[self.selected_map]['Map_Details']['Center']   = self.image_dict[self.selected_map]['Map_Details']['CenterX'] + ';' + self.image_dict[self.selected_map]['Map_Details']['CenterY']
        self.image_dict[self.selected_map]['Map_Details']['template'] = reconstruct_template(self.image_dict[self.selected_map]['Map_Details']['template'], self.image_dict[self.selected_map]['Map_Details'])
        self.image_dict[self.selected_map]['Map_Details']['Modified'] = 'Moved'
        print(self.image_dict[self.selected_map]['Map_Details']['template'])
        self.scene.clear()
        self.add_global_map_layer()
        self.add_ic_map_layer()

    def handle_delete_key(self):
        """Handle deleting the currently selected item"""
        if self.selected_map and self.selected_map in self.image_dict:
            # Mark as deleted in the data structure
            self.image_dict[self.selected_map]['Map_Details']['Modified'] = 'Deleted'
            
            # Remove from the list widget
            items = self.item_list.findItems(self.selected_map, Qt.MatchExactly)
            if items:
                row = self.item_list.row(items[0])
                self.item_list.takeItem(row)
            
            # Clear selection
            self.selected_map = None
            self.property_editor.clear()
            
            # Refresh the display
            self.scene.clear()
            self.add_global_map_layer()
            self.add_ic_map_layer()

    def add_item(self):

        #Needs a new map
        if self.selected_map in self.image_dict:
            self.image_dict[self.selected_map]['Map_Details']['Modified'] = 'Added'

        
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
                        pass
                        #print('not on map')
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
