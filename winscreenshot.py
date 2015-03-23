from PIL import ImageGrab
import numpy as np
import cv2
def screenshot(region=None):
	if region is None:
		ImageGrab.grab().save("screen.bmp","BMP")
		return cv2.imread("screen.bmp")
	else:
		ImageGrab.grab(region).save("screen.bmp","BMP")
		return cv2.imread("screen.bmp")
def get_region(region):
	return [region[0],region[1],region[0]+region[2],region[1]+region[3]]
