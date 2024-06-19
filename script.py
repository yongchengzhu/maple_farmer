import tkinter as tk
import pygetwindow as gw
import signal
import sys
from PIL import ImageGrab
import numpy as np
import win32gui, win32ui
from win32api import GetSystemMetrics

def get_window_dimensions(window_name):
  windows = gw.getWindowsWithTitle(window_name)
  return windows[0].size if len(windows) > 0 else None

def move_window_to_corner(window_name):
  windows = gw.getWindowsWithTitle(window_name)
  windows[0].moveTo(0, 0)

def get_character_location():
    target_color = (255, 221, 68)
    screen = ImageGrab.grab(bbox=(0, 0, 150, 130))
    img_rgb = np.array(screen)
    height, width, _ = img_rgb.shape
    for x in range(width):
      for y in range(height):
          pixel_color = tuple(img_rgb[y, x])
          if pixel_color == target_color:
              print(f"Found character at {(x, y)}")
              return (x, y)

def draw_rectangle_at_location(x, y):
  dc = win32gui.GetDC(0)
  dcObj = win32ui.CreateDCFromHandle(dc)
  hwnd = win32gui.WindowFromPoint((0,0))
  dcObj.Rectangle((x-5, y-5, x+10, y+10))

def main():
  maplestory_dimensions = get_window_dimensions("MapleStory")
  print(f"Maplestory dimensions: {maplestory_dimensions}")
  move_window_to_corner("MapleStory")
  while True:
    x, y = get_character_location()
    draw_rectangle_at_location(x, y)

if __name__ == "__main__":
  main()

