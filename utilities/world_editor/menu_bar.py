# menu_bar.py
from PyQt5.QtWidgets import QAction

def create_menu_bar(window, zxgame_file):
    menubar = window.menuBar()
    file_menu = menubar.addMenu('&File')

    save = QAction('&Save', window)
    save.triggered.connect(lambda: zxgame_file.save_file(window.image_dict))
    file_menu.addAction(save)

    exit = QAction('&Exit', window)
    exit.triggered.connect(window.close)
    file_menu.addAction(exit)
