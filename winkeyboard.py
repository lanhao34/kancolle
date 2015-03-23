# -*- coding: utf-8 -*-
#
# by oldj
# http://oldj.net/
#

import pythoncom
import pyHook
import win32api
import win32con
import win32process
import threading
from time import sleep

class KeyBorad:
	"""docstring for KeyBorad"""
	def __init__(self):
		self.flag = True
		self.argv = False
		print "Press F10 to continue"
		t=threading.Thread(target=self.run)
		t.setDaemon(True)
		t.start()

	def onMouseEvent(self, event):
		# 监听鼠标事件
		print "MessageName:", event.MessageName
		print "Message:", event.Message
		print "Time:", event.Time
		print "Window:", event.Window
		print "WindowName:", event.WindowName
		print "Position:", event.Position
		print "Wheel:", event.Wheel
		print "Injected:", event.Injected
		print "---"

		# 返回 True 以便将事件传给其它处理程序
		# 注意，这儿如果返回 False ，则鼠标事件将被全部拦截
		# 也就是说你的鼠标看起来会僵在那儿，似乎失去响应了
		return True

	def onKeyboardEvent(self, event):
		# 监听键盘事件
		# print "MessageName:", event.MessageName
		# print "Message:", event.Message
		# print "Time:", event.Time
		# print "Window:", event.Window
		# print "WindowName:", event.WindowName
		# print "Ascii:", event.Ascii, chr(event.Ascii)
		# print "Key:", event.Key
		# print "KeyID:", event.KeyID
		# print "ScanCode:", event.ScanCode
		# print "Extended:", event.Extended
		# print "Injected:", event.Injected
		# print "Alt", event.Alt
		# print "Transition", event.Transition
		# print "---"
		# print event.Key
		if event.Key=='F9':
			self.argv=True
		if event.Key=='F10':
			if self.flag:
				print "Press F10 to pause."
				self.flag = False
			else:
				print "Press F10 to continue."
				self.flag = True
		if event.Key=='F12':
			win32api.PostThreadMessage(self.thread_id, win32con.WM_QUIT, 0, 0);
			self.Kill_Process_pid(win32api.GetCurrentProcessId())
		# 同鼠标事件监听函数的返回值
		return True
	def Kill_Process_pid(self, pid) :
	    handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pid) #get process handle
	    win32api.TerminateProcess(handle,0) #kill by handle
	    win32api.CloseHandle(handle) 
	def run(self):
		# 创建一个“钩子”管理对象
		hm = pyHook.HookManager()

		# 监听所有键盘事件
		hm.KeyDown = self.onKeyboardEvent
		# 设置键盘“钩子”
		hm.HookKeyboard()


		self.thread_id = win32api.GetCurrentThreadId()
		# # 监听所有鼠标事件
		# hm.MouseAll = onMouseEvent
		# # 设置鼠标“钩子”
		# hm.HookMouse()

		# 进入循环，如不手动关闭，程序将一直处于监听状态
		pythoncom.PumpMessages()
		exit()
if __name__ == "__main__":
	
	from winmouse import winMouse
	from tryopencv import *
	keyborad=KeyBorad()
	dir_name=os.getcwd()
	mouse.keyborad=keyborad
	os.chdir(dir_name+os.sep+"win")
	ac=AutoClick()
	ac.main()
	