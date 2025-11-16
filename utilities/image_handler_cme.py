from PIL import Image, ImageEnhance
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
from PyQt5.QtWidgets import  QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt5.QtCore import QTimer

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
