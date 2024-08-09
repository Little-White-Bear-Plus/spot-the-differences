from ctypes import windll
from ctypes.wintypes import HWND


class Mouse:

    def __init__(self):
        self.PostMessageW = windll.user32.PostMessageW
        self.ClientToScreen = windll.user32.ClientToScreen

        self.WM_MOUSEMOVE = 0x0200
        self.WM_LBUTTONDOWN = 0x0201
        self.WM_LBUTTONUP = 0x202
        self.WM_MOUSEWHEEL = 0x020A
        self.WHEEL_DELTA = 120

    def leftDown(self, handle: HWND, x: int, y: int):
        """在坐标(x, y)按下鼠标左键"""
        wparam = 0
        lparam = y << 16 | x
        self.PostMessageW(handle, self.WM_LBUTTONDOWN, wparam, lparam)

    def leftUp(self, handle: HWND, x: int, y: int):
        """在坐标(x, y)放开鼠标左键"""
        wparam = 0
        lparam = y << 16 | x
        self.PostMessageW(handle, self.WM_LBUTTONUP, wparam, lparam)

    def click(self, handle: HWND, pos: tuple):
        self.leftDown(handle, pos[0], pos[1])
        self.leftUp(handle, pos[0], pos[1])
