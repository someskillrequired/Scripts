# map_scene.py
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt5.QtGui import QPen, QPainter
from PyQt5.QtCore import Qt

class MapScene:
    def __init__(self, image_dict):
        self.image_dict = image_dict
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.selection_rect = None
        self.selected_item = None

        self.add_global_map_layer()
        self.add_ic_map_layer()

    def add_global_map_layer(self):
        self.scene.clear()
        global_item = self.image_dict['@Map']
        pixmap_item = QGraphicsPixmapItem(global_item['Image'].final_image)
        pixmap_item.setPos(0, 0)
        self.scene.addItem(pixmap_item)

    def add_ic_map_layer(self):
        for key, item in self.image_dict.items():
            if key == "@Map" or item['Map_Details'].get('Modified') == 'Deleted':
                continue
            pixmap_item = QGraphicsPixmapItem(item['Image'].final_image)
            pixmap_item.setPos(float(item['Map_Details']['X']), float(item['Map_Details']['Y']))
            self.scene.addItem(pixmap_item)

    def highlight_item(self, item_key):
        if self.selection_rect:
            self.scene.removeItem(self.selection_rect)
        details = self.image_dict[item_key]['Map_Details']
        rect = QGraphicsRectItem(
            float(details['X']), float(details['Y']),
            float(details['Width']), float(details['Height'])
        )
        pen = QPen(Qt.red, 3)
        rect.setPen(pen)
        rect.setZValue(1)
        self.scene.addItem(rect)
        self.selection_rect = rect
        self.view.centerOn(rect)
