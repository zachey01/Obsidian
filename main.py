import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import win32gui
import win32console
import win32con
from src.obsidian import Obsidian
from src.gui.gui import create_gui

if __name__ == "__main__":
    if os.name != "nt":
        print("Obsidian is only working on Windows.")
        os._exit(0)
    
    obsidian = Obsidian()
    win32gui.ShowWindow(win32console.GetConsoleWindow(), win32con.SW_HIDE)
    create_gui(obsidian)
