import os
import sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import logging
import pyautogui
import time
import pytesseract
from PIL import Image

logging.basicConfig(
    filename="typing_bot_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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
    global corner1, corner2, CHAR_GAP

    # 1) Check corners
    if corner1 is None or corner2 is None:
        messagebox.showerror("Error", "Set both corners before running the bot.")
        logging.error("run_bot called with corner1=%s, corner2=%s", corner1, corner2)
        return

    x1, y1 = corner1
    x2, y2 = corner2

    left = min(x1, x2)
    top = min(y1, y2)
    right = max(x1, x2)
    bottom = max(y1, y2)
    width = right - left
    height = bottom - top
    region = (left, top, width, height)

    logging.debug("Region calculated: %s", region)

    # Sanity check: positive width/height
    if width <= 0 or height <= 0:
        messagebox.showerror("Error", f"Invalid region: {region}")
        logging.error("Invalid region %s", region)
        return

    # 2) Screenshot
    try:
        img = pyautogui.screenshot("text.png", region=region)
        img.save("debug_region.png")  # see what area was captured
        logging.info("Screenshot saved as debug_region.png")
    except Exception as e:
        messagebox.showerror("Screenshot error", str(e))
        logging.exception("Error during screenshot")
        return

    # 3) OCR
    try:
        raw_text = pytesseract.image_to_string(img, config="--psm 6")
        logging.debug("raw_text repr: %r", raw_text)
    except Exception as e:
        messagebox.showerror("OCR error", str(e))
        logging.exception("Error during OCR")
        return

    text = (raw_text or "").strip().replace("\n", " ")
    logging.info("Final text length: %d", len(text))

    if not text:
        messagebox.showinfo(
            "Info",
            "OCR produced empty text.\n"
            "Check debug_region.png to see what was captured."
        )
        return

    # Optional: show preview of what will be typed
    preview = text if len(text) < 200 else text[:200] + "..."
    messagebox.showinfo("Preview", f"Will type:\n\n{preview}")
    logging.debug("Preview text shown to user")

    # 4) Get typing speed from your Entry if you're using temp/StringVar
    try:
        CHAR_GAP = float(temp.get())
        logging.info("Using CHAR_GAP=%f", CHAR_GAP)
    except Exception as e:
        logging.exception("Error converting typing speed, falling back to default 0.01")
        CHAR_GAP = 0.01

    # 5) Delay so user can focus typing box
    messagebox.showinfo(
        "Typing Bot",
        "Click OK, then quickly focus the typing field.\n"
        "Typing will start in 3 seconds."
    )
    time.sleep(3)

    # 6) Type
    try:
        pyautogui.write(text, interval=CHAR_GAP)
        logging.info("Typing completed")
    except Exception as e:
        messagebox.showerror("Typing error", str(e))
        logging.exception("Error during pyautogui.write")

    
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
