import threading
import time
import json
import os
import ctypes
import pyMeow as pm
import psutil
import win32api
import win32con
import win32gui
import win32process

from src.config import ConfigListener, CONFIG_FILE_PATH
from src.core import Colors, Entity, Offsets
from src.features import ESP, TriggerBot, FOV, Glowing

VERSION = "1.0.0"
user32 = ctypes.WinDLL("user32")

class Obsidian:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Obsidian, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._init_config()
        self._init_attributes()
        self._init_features()
        self.run()

    def _init_config(self):
        self.config = {
            "version": VERSION,
            "esp": {
                "enabled": False,
                "bind": 0,
                "box": True,
                "boxBackground": False,
                "boxRounding": 0,
                "skeleton": True,
                "redHead": False,
                "snapline": False,
                "onlyEnemies": True,
                "name": False,
                "health": True,
                "glowing": False,
                "color": {"r": 1.0, "g": 0.11, "b": 0.11, "a": 0.8}
            },
            "triggerBot": {
                "enabled": False,
                "bind": 0,
                "onlyEnemies": True,
                "delay": 240,
                "randomDelay": 110
            },
            "fov": {
                "enabled": False,
                "value": 90
            },
            "misc": {
                "watermark": True,
                "obsbypass": False
            },
            "settings": {
                "saveSettings": True,
                "acrylicEffect": False,
                "language": "en"
            }
        }
        
        self._load_config()
        self.config = ConfigListener(self.config)

    def _load_config(self):
        if os.path.isfile(CONFIG_FILE_PATH):
            try:
                config = json.loads(open(CONFIG_FILE_PATH, encoding="utf-8").read())
            
                # Merge configs instead of replacing completely
                def merge_configs(default, loaded):
                    for key, value in loaded.items():
                        if key in default:
                            if isinstance(value, dict) and isinstance(default[key], dict):
                                merge_configs(default[key], value)
                            else:
                                default[key] = value
            
                if config.get("version") == VERSION and config.get("settings", {}).get("saveSettings", True):
                    merge_configs(self.config, config)
            except Exception as e:
                print(f"Error loading config: {e}")

    def _init_attributes(self):
        self.gui_window_handle = None
        self.overlay_window_handle = None
        self.overlay_thread_exists = False
        self.local_team = None
        self.focused_process = ""
        
        self.esp_color = pm.new_color_float(
            self.config["esp"]["color"]["r"],
            self.config["esp"]["color"]["g"],
            self.config["esp"]["color"]["b"],
            self.config["esp"]["color"]["a"]
        )
        self.esp_background_color = pm.fade_color(self.esp_color, 0.1)
        self.offsets = Offsets
        self.triggerbot_thread = None

    def _init_features(self):
        self.esp = ESP(self)
        self.triggerbot = TriggerBot(self)
        self.fov = FOV(self)
        self.glowing = Glowing(self)

    def is_cs_opened(self):
        while True:
            if not pm.process_running(self.proc):
                os._exit(0)
            time.sleep(3)

    def window_listener(self):
        while True:
            try:
                self.focused_process = psutil.Process(
                    win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[-1]
                ).name()
            except:
                self.focused_process = ""
            time.sleep(0.5)

    def update_triggerbot(self):
        if self.config["triggerBot"]["enabled"]:
            self.config["triggerBot"]["enabled"] = False
            if self.triggerbot_thread is not None:
                time.sleep(0.1)
            
            self.triggerbot = TriggerBot(self)
            self.triggerbot_thread = threading.Thread(target=self.triggerbot.run, daemon=True)
            self.config["triggerBot"]["enabled"] = True
            self.triggerbot_thread.start()

    def run(self):
        print("Waiting for CS2...")
        while True:
            time.sleep(1)
            try:
                self.proc = pm.open_process("cs2.exe")
                self.mod = pm.get_module(self.proc, "client.dll")["base"]
                break
            except:
                pass
        
        print("Starting Obsidian!")
        os.system("cls")
        
        try:
            self.offsets.fetch_offsets()
        except Exception as e:
            print(e)
            input("Can't retrieve offsets. Press any key to exit!")
            os._exit(0)
        
        threading.Thread(target=self.is_cs_opened, daemon=True).start()
        threading.Thread(target=self.window_listener, daemon=True).start()
        threading.Thread(target=self.esp.bind_listener, daemon=True).start()
        
        if self.config["esp"]["enabled"] or self.config["misc"]["watermark"]:
            threading.Thread(target=self.esp.run, daemon=True).start()
        
        if self.config["triggerBot"]["enabled"]:
            self.update_triggerbot()
        
        if self.config["esp"]["glowing"]:
            threading.Thread(target=self.glowing.run, daemon=True).start()

    def get_entities(self):
        ent_list = pm.r_int64(self.proc, self.mod + self.offsets.dwEntityList)
        local = pm.r_int64(self.proc, self.mod + self.offsets.dwLocalPlayerController)
        
        for i in range(1, 65):
            try:
                entry_ptr = pm.r_int64(self.proc, ent_list + (8 * (i & 0x7FFF) >> 9) + 16)
                controller_ptr = pm.r_int64(self.proc, entry_ptr + 120 * (i & 0x1FF))
                
                if controller_ptr == local:
                    self.local_team = pm.r_int(self.proc, local + self.offsets.m_iTeamNum)
                    continue
                
                controller_pawn_ptr = pm.r_int64(self.proc, controller_ptr + self.offsets.m_hPlayerPawn)
                list_entry_ptr = pm.r_int64(self.proc, ent_list + 0x8 * ((controller_pawn_ptr & 0x7FFF) >> 9) + 16)
                pawn_ptr = pm.r_int64(self.proc, list_entry_ptr + 120 * (controller_pawn_ptr & 0x1FF))
            except:
                continue
            
            yield Entity(controller_ptr, pawn_ptr, self.proc)
