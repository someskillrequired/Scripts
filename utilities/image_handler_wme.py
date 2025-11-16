import numpy as np
from PIL import Image, ImageEnhance
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

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

    def get_cut_image(self, entire_image, x1, y1, width, height):
        """Crop a portion from the entire image"""
        # Ensure coordinates are within bounds
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(entire_image.width(), int(width))
        y2 = min(entire_image.height(), int(height))
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