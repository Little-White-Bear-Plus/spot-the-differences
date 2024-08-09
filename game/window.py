import math
import win32gui, win32ui, win32con

from game.mouse import Mouse
from constant import LIMIT
from PIL import Image, ImageChops


def getWindowHwnd(className, width=0, height=0):
    """获取指定类名（以及宽高）的窗口句柄"""
    mainHwndList = []
    hwndList = []
    # lambda 就是匿名函数，这里的作用就是将检测到的所有hwnd写入mainHwndList
    win32gui.EnumWindows(lambda hwnd, hwnds: hwnds.append(hwnd), mainHwndList)
    for hwnd in mainHwndList:
        name = win32gui.GetClassName(hwnd)
        if name == className:
            hwndList.append(hwnd)
    if hwndList == []:
        # 查找上述窗口的子窗口
        for hwnd in mainHwndList:
            childHwndList = []
            # 同上，将子窗口的句柄全部写入childHwndList
            win32gui.EnumChildWindows(hwnd, lambda hwnd, hwnds: hwnds.append(hwnd), childHwndList)
            for child_hwnd in childHwndList:
                name2 = win32gui.GetClassName(child_hwnd)
                if name2 == className:
                    hwndList.append(child_hwnd)
    if not width and not height:
        return hwndList
    else:
        # print(hwndList)
        newHwndList = []
        for hwnd in hwndList:
            x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
            # print(x2 - x1, y2 - y1)
            if x2 - x1 == width and y2 - y1 == height:
                newHwndList.append(hwnd)
        return newHwndList


def compareImage(img1: Image.Image, img2: Image.Image):
    if img1 is None or img2 is None:
        return False
    # 打开图片的直方图
    h1 = img1.histogram()
    h2 = img2.histogram()
    # 计算两个图片每一个点的平方差 求和 求平均值 求平方根
    differ = math.sqrt(sum((a - b) ** 2 for a, b in zip(h1, h2)) / len(h1))
    # return differ
    return differ <= LIMIT if True else False


class Window:

    def __init__(self, hwnd):
        self.hwnd = hwnd  # 窗口句柄

    def click(self, pos: tuple):
        Mouse().click(self.hwnd, pos)

    def screenShot(self, rect: list = None):
        """
        截取指定区域的图片（后台）
        :return: PIL.Image.Image
        """
        isNone = False
        if rect is None:
            isNone = True
            rect = win32gui.GetWindowRect(self.hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        # DC（Device Context）即设备上下文，是Windows中用于绘制图形的核心对象，包含了绘图所需的各种属性和状态，用于进行绘制操作
        hwndDC = win32gui.GetWindowDC(self.hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 将DC转换为Python对象
        # 创建一个内存DC（虚拟DC），其绘制操作在内存中进行，可进行离屏绘制
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建一个空的位图对象，并返回该对象的句柄；用于存储绘制结果或者作为绘制目标
        saveBitmap = win32ui.CreateBitmap()
        # 执行位图对象的属性，并与DC兼容
        saveBitmap.CreateCompatibleBitmap(mfcDC, width, height)
        # 将一个GDI对象（位图、字体等）选入DC中，使其可以在DC上进行操作
        saveDC.SelectObject(saveBitmap)
        # 核心函数，可以用于在不同DC之间传输位图等（复制）
        if isNone:
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        else:
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (rect[0], rect[1]), win32con.SRCCOPY)
        bmpInfo = saveBitmap.GetInfo()
        # 获取位图句柄中的数据
        bmpStr = saveBitmap.GetBitmapBits(True)  
        # 在字节缓冲区中引用像素数据创建图像内存
        image = Image.frombuffer('RGB', (bmpInfo['bmWidth'], bmpInfo['bmHeight']), bmpStr, 'raw', 'BGRX', 0, 1)
        win32gui.DeleteObject(saveBitmap.GetHandle())  # 删除位图对象
        # 删除DC对象
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwndDC)
        return image


class WindowManage:

    def __init__(self, windowList):
        self.windowList = windowList

    def setMainWindow(self):
        """将最右端的窗口设置为主窗口"""
        maxRight = -1
        mainWindow = None
        for window in self.windowList:
            _, _, right, _ = win32gui.GetWindowRect(window.hwnd)
            if right > maxRight:
                maxRight = right
                mainWindow = window
        return mainWindow


if __name__ == '__main__':
    hwnds = getWindowHwnd('#32770', 1024, 768)
    window = Window(hwnds[0])
    leftImage = window.screenShot([93, 312, 474, 598])
    leftImage.save('../temp/left.png')
    rightImage = window.screenShot([550, 312, 931, 598])
    rightImage.save('../temp/right.png')
    difimg = ImageChops.difference(leftImage, rightImage)
    difimg.save('../temp/dif.png')
