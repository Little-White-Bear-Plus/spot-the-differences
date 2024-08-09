import sys
import time
import threading

from PIL import ImageChops

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap

from pynput.keyboard import Key, Listener

from game.window import *
from untitled import Ui_Form
from constant import GAME_WIDTH, GAME_HEIGHT

import detect


class Monitor:
    def __init__(self, onPress):
        self.onPress = onPress

    def listen(self):
        with Listener(on_press=self.onPress) as listen:
            listen.join()


class UI(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.windowList = []
        self.mainWindow = None

        self.start = Image.open('start.png')
        self.stop = Image.open('stop.png')
        self.load = Image.open('load.png')

        self.stopEvent = None  # 控制线程

        self.finishCount = 0  # 单局完成图片的数目

        self.pushButton.clicked.connect(self.runThread)

        detect.run()  # 在创建窗口的同时加载好模型需要的环境

    def runThread(self):
        # 防止 ui 界面卡死
        threading.Thread(target=self.run, daemon=True).start()
        self.finishCount = 0  # 初始化关键参数

    def run(self):
        self.pushButton.setEnabled(False)
        self.bindWindow('#32770', 1024, 768)
        self.stopEvent = threading.Event()
        for window in self.windowList:
            threading.Thread(target=self.injectProcedure, args=(window,), daemon=True).start()
        # 这里除了监听外，更重要的作用是阻断程序（保证injectProcedure的线程能够正常运行）
        Monitor(self.onPress).listen()
        self.pushButton.setEnabled(True)

    def bindWindow(self, className, windowWidth=0, windowHeight=0):
        self.windowList = [Window(i) for i in getWindowHwnd(className, windowWidth, windowHeight)]
        self.mainWindow = WindowManage(self.windowList).setMainWindow()

    def injectProcedure(self, window):
        """注入程序"""
        while not self.stopEvent.is_set():  # 相当于 => while Ture；is_set 的默认值为 False
            if window == self.mainWindow:
                if self.finishCount == 0:
                    while not self.stopEvent.is_set():
                        gameStart = window.screenShot([792, 691, 840, 717])
                        if compareImage(self.start, gameStart):
                            window.click((820, 705))
                            break
                        time.sleep(0.2)

                    # 等待游戏界面加载
                    while not self.stopEvent.is_set():
                        gameLoad = window.screenShot([500, 204, 522, 247])
                        if compareImage(self.load, gameLoad):
                            self.label.setText('提示信息：执行...')
                            break
                        time.sleep(0.2)
                    time.sleep(1)

                else:
                    while not self.stopEvent.is_set():
                        # 中间的水母图案会影响模型处理
                        gameStop = window.screenShot([489, 391, 538, 409])
                        if not compareImage(self.stop, gameStop):
                            time.sleep(0.2)
                            break
                        time.sleep(0.2)

                    leftImage = window.screenShot([93, 312, 474, 598])
                    rightImage = window.screenShot([550, 312, 931, 598])
                    difimg = ImageChops.difference(leftImage, rightImage)
                    difimg.save('images/current.png')
                    self.label_2.setPixmap(QPixmap('images/current.png'))

                    # 模型推理 => 返回识别到的区域的中心坐标
                    res = detect.run()
                    count = len(res)
                    if count > 5:
                        res = res[:5]
                    for centerX, centerY, width, high in res:
                        # print(int(centerX * GAME_WIDTH) + 550, int(centerY * GAME_HEIGHT) + 312)
                        window.click((int(centerX * GAME_WIDTH) + 550, int(centerY * GAME_HEIGHT) + 312))
                        time.sleep(0.02)
                    # 标记出错有两个原因：
                    # 1. 模型不够强大（这里我只用了225张图片进行训练，存在点小问题也很正常）
                    # 2. 方案本身缺陷（其实方案也很简单，将色差较大的部分高亮出来；显然有一个致命的缺陷，如果不同的区域色差很小就没办法检测）
                    if count != 5:
                        self.label.setText('提示信息：标记出错，按tab键继续')
                        Monitor(self.onPress2).listen()
                    else:
                        time.sleep(3.5)

                self.finishCount += 1
                # print(self.finishCount)
                if self.finishCount == 5 + 1:
                    self.label.setText('提示信息：游戏结束')
                    self.finishCount = 0

            else:
                gameStart = window.screenShot([792, 691, 840, 717])
                if compareImage(self.start, gameStart):
                    window.click((820, 705))
                time.sleep(0.2)

    def onPress(self, key):
        if key == Key.esc:
            self.stopEvent.set()  # 结束所有线程（将 is_set 改为 True）
            return False

    def onPress2(self, key):
        if key == Key.tab:
            self.label.setText('提示信息：继续执行...')
            return False


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
