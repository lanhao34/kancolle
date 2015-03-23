#!/usr/bin/python

from Quartz.CoreGraphics import CGEventCreateMouseEvent
from Quartz.CoreGraphics import CGEventPost
from Quartz.CoreGraphics import kCGEventMouseMoved
from Quartz.CoreGraphics import kCGEventLeftMouseDown
from Quartz.CoreGraphics import kCGEventLeftMouseDown		
from Quartz.CoreGraphics import kCGEventLeftMouseUp
from Quartz.CoreGraphics import kCGMouseButtonLeft
from Quartz.CoreGraphics import kCGHIDEventTap
from time import sleep
 
class macMouse():
    def __init__(self):
        self.offset_x=0
        self.offset_y=0
    def setoffset(self,x,y):
        self.offset_x=x
        self.offset_y=y
    def mouseEvent(self,type, posx, posy):
        theEvent = CGEventCreateMouseEvent(None,type,(posx,posy),kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, theEvent)
 
    def move(self,posx,posy):
        self.mouseEvent(kCGEventMouseMoved, posx,posy);
 
    def click(self,posx,posy):
        self.mouseEvent(kCGEventLeftMouseDown, posx+self.offset_x ,posy+self.offset_y);
        self.mouseEvent(kCGEventLeftMouseUp, posx+self.offset_x ,posy+self.offset_y);
        
 
if __name__ == '__main__':
	mMouse = macMouse()
	mMouse.click(650,170)

#for i in range(110):
#    mMouse.mouseclick(650,170)
#    sleep(0.1)