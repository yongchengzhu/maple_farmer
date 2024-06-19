import pygetwindow as gw
from PIL import ImageGrab
import numpy as np
import win32gui, win32ui
import sched
import pydirectinput
import threading
import time

MINIMAP_BOUNDING_BOX = (0, 0, 280, 175)
CHARACTER_LOCATION = None
TARGET_LOCATIONS = [(70, 160), (100, 160), (150, 160)]
TARGET_LOCATIONS_INDEX = 0
TARGET_LOCATIONS_DIRECTION = 1 # 1 means to go right, -1 means to go left.
WALKING_RIGHT = False
WALKING_LEFT = False
STANDING = True

def get_window_dimensions(window_name):
  windows = gw.getWindowsWithTitle(window_name)
  windows[0].activate()
  return windows[0].size if len(windows) > 0 else None

def move_window_to_corner(window_name):
  windows = gw.getWindowsWithTitle(window_name)
  windows[0].moveTo(0, 0)

def draw_rectangle_at_location(x, y):
  dc = win32gui.GetDC(0)
  dcObj = win32ui.CreateDCFromHandle(dc)
  hwnd = win32gui.WindowFromPoint((0,0))
  dcObj.Rectangle((x-5, y-5, x+10, y+10))

def jump_up():
  pydirectinput.keyDown('up')
  pydirectinput.press('alt')
  pydirectinput.press('alt')
  pydirectinput.keyUp('up')

def jump_down(times):
  for _ in range(times):
    pydirectinput.keyDown('down')
    pydirectinput.press('space')
    pydirectinput.keyUp('down')
    time.sleep(1)
    pydirectinput.press('ctrl')
    time.sleep(1)

def get_character_location(location_scheduler):
  target_color = (255, 221, 68)
  screen = ImageGrab.grab(bbox=MINIMAP_BOUNDING_BOX)
  img_rgb = np.array(screen)
  height, width, _ = img_rgb.shape
  for y in range(height):
    for x in range(width):
      pixel_color = tuple(img_rgb[y, x])
      if pixel_color == target_color:
        # print(f"Found character at {(x, y)}")
        global CHARACTER_LOCATION
        CHARACTER_LOCATION = (x, y)
        draw_rectangle_at_location(x, y)
        break
    else:
      continue
    break
  location_scheduler.enter(0, 1, get_character_location, (location_scheduler,))

def move_character_to_location(move_scheduler):
  global WALKING_RIGHT
  global WALKING_LEFT
  global STANDING
  global TARGET_LOCATIONS_INDEX
  global TARGET_LOCATIONS_DIRECTION
  x_error_margin = 5
  if CHARACTER_LOCATION:
    if (CHARACTER_LOCATION[0] - TARGET_LOCATIONS[TARGET_LOCATIONS_INDEX][0]) < (0 - x_error_margin) and not WALKING_RIGHT:
      print(f"WALKING RIGHT, CHARACTER_LOCATION_X: {CHARACTER_LOCATION}, TARGET_LOCATIONS_X: {TARGET_LOCATIONS[0][0]}")
      WALKING_RIGHT = True
      STANDING = False
      pydirectinput.keyDown('right')
    elif (CHARACTER_LOCATION[0] - TARGET_LOCATIONS[TARGET_LOCATIONS_INDEX][0]) > x_error_margin and not WALKING_LEFT:
      print(f"WALKING LEFT, CHARACTER_LOCATION_X: {CHARACTER_LOCATION}, TARGET_LOCATIONS_X: {TARGET_LOCATIONS[0][0]}")
      WALKING_LEFT = True
      STANDING = False
      pydirectinput.keyDown('left')
    elif abs(CHARACTER_LOCATION[0] - TARGET_LOCATIONS[TARGET_LOCATIONS_INDEX][0]) <= x_error_margin and not STANDING:
      print("Arrived at location.")
      STANDING = True
      WALKING_LEFT = False
      WALKING_RIGHT = False
      pydirectinput.keyUp('left')
      pydirectinput.keyUp('right')
      if TARGET_LOCATIONS_INDEX == 1:
        pydirectinput.press('e')
        pydirectinput.press('ctrl')
      else:
        pydirectinput.press('ctrl')
        time.sleep(0.5)
        pydirectinput.press('alt')
        time.sleep(2)
        pydirectinput.press('ctrl')
        time.sleep(1)
        jump_down(2)


      if TARGET_LOCATIONS_INDEX == 0:
        TARGET_LOCATIONS_DIRECTION = 1
      elif TARGET_LOCATIONS_INDEX == len(TARGET_LOCATIONS) - 1:
        TARGET_LOCATIONS_DIRECTION = -1
      TARGET_LOCATIONS_INDEX = TARGET_LOCATIONS_INDEX + TARGET_LOCATIONS_DIRECTION
  move_scheduler.enter(0, 2, move_character_to_location, (move_scheduler,))


def main():
  maplestory_dimensions = get_window_dimensions("MapleStory")
  move_window_to_corner("MapleStory")
  location_scheduler = sched.scheduler()
  location_scheduler.enter(0, 1, get_character_location, (location_scheduler,))
  move_scheduler = sched.scheduler()
  move_scheduler.enter(0, 2, move_character_to_location, (move_scheduler,))

  # Create threads for each scheduler and start them
  thread1 = threading.Thread(target=location_scheduler.run)
  thread2 = threading.Thread(target=move_scheduler.run)

  thread1.start()
  thread2.start()

  # Wait for threads to complete (this won't happen as they run indefinitely)
  #thread1.join()
  #thread2.join()

if __name__ == "__main__":
  main()

