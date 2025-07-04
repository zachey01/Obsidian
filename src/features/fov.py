import pymem
import requests
import re
import time

class FOV:
    def __init__(self, obsidian):
        self.obsidian = obsidian
        self.offsets_url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.hpp"
        self.client_url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.hpp"
        self.pm = None
        self.client = None
        self.offsets = {}
        self.default_fov = 90
        self.initialize()

    def initialize(self):
        try:
            self.pm = pymem.Pymem("cs2.exe")
            self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
            self.fetch_offsets()
        except Exception as e:
            print(f"FOV initialization failed: {e}")

    def fetch_offsets(self):
        try:
            offsets_content = requests.get(self.offsets_url).text
            client_content = requests.get(self.client_url).text
            
            # Parse dwLocalPlayerController
            pattern = re.compile(r'dwLocalPlayerController\s*=\s*0x([0-9A-Fa-f]+)')
            match = pattern.search(offsets_content)
            if match:
                self.offsets["dwLocalPlayerController"] = int(match.group(1), 16)
            else:
                raise ValueError("Offset dwLocalPlayerController not found.")
            
            # Parse m_iDesiredFOV
            pattern = re.compile(r'm_iDesiredFOV\s*=\s*0x([0-9A-Fa-f]+)')
            match = pattern.search(client_content)
            if match:
                self.offsets["m_iDesiredFOV"] = int(match.group(1), 16)
            else:
                raise ValueError("Offset m_iDesiredFOV not found.")
        except Exception as e:
            print(f"Failed to fetch FOV offsets: {e}")
            self.offsets = {}

    def set_fov(self, fov_value):
        if not self.pm or not self.client or not self.offsets:
            return
        
        try:
            dw_local_player_controller = self.pm.read_longlong(
                self.client.lpBaseOfDll + self.offsets["dwLocalPlayerController"]
            )
            if dw_local_player_controller:
                self.pm.write_int(
                    dw_local_player_controller + self.offsets["m_iDesiredFOV"], fov_value
                )
        except Exception as e:
            print(f"Failed to set FOV: {e}")

    def reset_fov(self):
        self.set_fov(self.default_fov)

    def run(self):
        while not hasattr(self.obsidian, "focused_process"):
            time.sleep(0.1)
        
        while True:
            time.sleep(0.1)
            if self.obsidian.focused_process != "cs2.exe":
                continue
            
            if not self.obsidian.config["fov"]["enabled"]:
                self.reset_fov()
                continue
            
            self.set_fov(self.obsidian.config["fov"]["value"])
