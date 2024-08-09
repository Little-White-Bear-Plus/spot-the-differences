import os
import sys
import threading

from window import *
from untitled import Ui_Form
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PIL import ImageChops
from pynput.keyboard import Key, Listener

"""
    获取模型训练的数据集
"""


class UI(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.hwnd = 920254

        self.pushButton.clicked.connect(self.runThread)

    def runThread(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        self.pushButton.setEnabled(False)
        self.monitor(self.on_press)
        self.pushButton.setEnabled(True)

    def _get(self):
        win = Window(self.hwnd)
        leftImage = win.screenShot([93, 312, 474, 598])
        rightImage = win.screenShot([550, 312, 931, 598])
        difimg = ImageChops.difference(leftImage, rightImage)
        current = len(os.listdir('../../train-model/datasets/images'))
        difimg.save(f'../datasets/data/{current}.png')
        self.label.setPixmap(QPixmap(f'../train-model/datasets/images/{current}.png'))

    def on_press(self, key):
        if key == Key.alt_l or key == Key.alt_gr:
            self._get()
        elif key == Key.esc:
            return False

    def monitor(self, on_press):
        with Listener(on_press=on_press) as listen:
            listen.join()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
