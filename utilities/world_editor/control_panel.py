# control_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
import json

class ControlPanel(QWidget):
    def __init__(self, image_dict, map_scene):
        super().__init__()
        self.image_dict = image_dict
        self.map_scene = map_scene
        self.selected_item = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Map Items"))
        self.item_list = QListWidget()
        layout.addWidget(self.item_list)

        layout.addWidget(QLabel("Properties"))
        self.property_editor = QTextEdit()
        layout.addWidget(self.property_editor)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_properties)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.populate_list()
        self.item_list.itemSelectionChanged.connect(self.on_item_selected)

    def populate_list(self):
        self.item_list.clear()
        for key, val in sorted(self.image_dict.items()):
            if key == "@Map" or val['Map_Details'].get('Modified') == 'Deleted':
                continue
            self.item_list.addItem(key)

    def on_item_selected(self):
        items = self.item_list.selectedItems()
        if not items:
            return
        name = items[0].text()
        self.selected_item = name
        self.map_scene.highlight_item(name)
        details = self.image_dict[name]['Map_Details']
        self.property_editor.setPlainText(json.dumps(details, indent=4))

    def save_properties(self):
        if not self.selected_item:
            return
        try:
            details = json.loads(self.property_editor.toPlainText())
            self.image_dict[self.selected_item]['Map_Details'].update(details)
            QMessageBox.information(self, "Saved", "Properties updated!")
            self.map_scene.add_ic_map_layer()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
