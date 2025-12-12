import os
import sys
from tkinter import *
from tkinter import ttk
import pyautogui
import time
import pytesseract
from PIL import Image

running_corner1 = False
running_corner2 = False
corner1 = None
corner2 = None

def resource_path(relative_path: str) -> str:
    
    if hasattr(sys, "_MEIPASS"):
        
        base_path = sys._MEIPASS
    else:
        
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


pytesseract.pytesseract.tesseract_cmd = resource_path(
    os.path.join("Tesseract-OCR", "tesseract.exe")
)


def update_corner1():
    
    global corner1, running_corner1

    if not running_corner1:
        return
     
    x, y = pyautogui.position()
    corner1 = (x,y)
    corner1_text.set(f"Corner 1: X={x}, Y={y}")


    root.after(50, update_corner1)  


def start_corner1():
    
    global running_corner1
    running_corner1 = True
    update_corner1()

def lock_corner(event=None):

    global running_corner1, running_corner2
    if running_corner1:
        running_corner1 = False
    if running_corner2:
        running_corner2 = False
    

def update_corner2():
    
    global corner2, running_corner2

    if not running_corner2:
        return
     
    x, y = pyautogui.position()
    corner2 = (x,y)
    corner2_text.set(f"Corner 2: X={x}, Y={y}")

    root.after(50, update_corner2)  


def start_corner2():
    
    global running_corner2
    running_corner2 = True
    update_corner2()

def run_bot():

    global corner1, corner2

    if corner1 == None or corner2 == None: 
        print("Set both corners")
    x1, y1 = corner1
    x2, y2 = corner2

    CHAR_GAP = float(temp.get())

    left = min(x1, x2)
    top = min(y1, y2)
    right = max(x1, x2)
    bottom = max(y1, y2)
    width = right - left
    height = bottom - top
    region=(left,top,width,height)
    pyautogui.screenshot("text.png",region=region)
    img = Image.open('text.png')

    raw_text = pytesseract.image_to_string(img, config="--psm 6")
    text = raw_text.strip().replace("\n", " ")

    time.sleep(3)
    pyautogui.write(text, interval=CHAR_GAP)
    
root = Tk()
root.title("Typing Bot")
root.bind("<Return>", lock_corner)
corner1_text = StringVar(value="Corner 1: not set")
corner2_text = StringVar(value="Corner 2: not set")

mainframe = ttk.Frame(root, padding=(10,10,10,10))
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))


label_corner1 = ttk.Label(mainframe, textvariable=corner1_text).grid(column=1, row=3, sticky=W)
label_corner2 = ttk.Label(mainframe, textvariable=corner2_text).grid(column=1, row=5, sticky=W)

button_corner1 = ttk.Button(mainframe, text="Set corner 1", command=start_corner1).grid(column=3, row=3, sticky=W)
button_corner2 = ttk.Button(mainframe, text="Set corner 2", command=start_corner2).grid(column=3, row=5, sticky=W)
run_button = ttk.Button(mainframe, text="RUN", command=run_bot).grid(column=10, row=3, sticky=W)
temp = StringVar(value="0.1")
speed = ttk.Entry(mainframe, textvariable=temp).grid(column=10, row=5, sticky=W)

instructions = ttk.Label(mainframe, text="Use enter to lock in your coordinates for each corner.\nAdjust the numerical value above to change the delay between characters typed. (ex: 0.1 = 10ms)\nUpon clicking run, you will have ~3 seconds to enter the typespace.").grid(column=1, row=6, sticky=W)


root.mainloop()
