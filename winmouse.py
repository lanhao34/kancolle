# _*_ coding:UTF-8 _*_

import win32api
import win32con
import win32gui
from ctypes import *
from time import sleep
 
class winMouse():
	def __init__(self):
		self.offset_x=0
		self.offset_y=0
		self.ac=None
	def setoffset(self,x,y):
		self.offset_x=x
		self.offset_y=y
 
	def move(self,posx,posy):
		windll.user32.SetCursorPos(int(posx), int(posy))
 
	def click(self,posx,posy):
		while self.ac.flag:
			sleep(1)
		self.move(posx+self.offset_x,posy+self.offset_y)
		sleep(0.05)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
		
 
if __name__ == '__main__':
	mouse = winMouse()
	# mouse.setoffset(100,100)
	mouse.click(*[77,257])
