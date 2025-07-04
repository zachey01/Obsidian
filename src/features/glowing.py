import pymem
import keyboard
import threading
import time

class Glowing:
    def __init__(self, obsidian):
        self.obsidian = obsidian
        self.pm = None
        self.client = None
        self.pattern = "32 c0 48 8b b4 24 ? ? ? ? 48 8b 9c 24"
        self.pattern_address = None
        self.original_pattern_bytes = None
        self.is_enabled = False
        self.initialize()

    def initialize(self):
        try:
            self.pm = pymem.Pymem("cs2.exe")
            self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
            self.pattern_address = self.find_pattern(self.client, self.pattern)
            
            if self.pattern_address:
                self.original_pattern_bytes = self.pm.read_bytes(self.pattern_address, 2)
            else:
                print("Pattern not found in client.dll.")
        except Exception as e:
            print(f"Glowing initialization failed: {e}")

    def find_pattern(self, module, pattern):
        base_address = module.lpBaseOfDll
        module_size = module.SizeOfImage
        memory = self.pm.read_bytes(base_address, module_size)
        pattern_bytes = []
        pattern_parts = pattern.split()
        
        for part in pattern_parts:
            if part == "?":
                pattern_bytes.append(None)
            else:
                pattern_bytes.append(int(part, 16))
        
        pattern_length = len(pattern_bytes)
        for i in range(module_size - pattern_length):
            match = True
            for j in range(pattern_length):
                if pattern_bytes[j] is not None and memory[i + j] != pattern_bytes[j]:
                    match = False
                    break
            if match:
                return base_address + i
        return None

    def toggle_glowing(self):
        if not self.pattern_address:
            return False
        
        try:
            current_bytes = self.pm.read_bytes(self.pattern_address, 2)
            if current_bytes == self.original_pattern_bytes:
                self.pm.write_bytes(self.pattern_address, b"\x90\x90", 2)
                self.is_enabled = True
            else:
                self.pm.write_bytes(self.pattern_address, self.original_pattern_bytes, 2)
                self.is_enabled = False
            return True
        except:
            return False

    def set_glowing(self, enabled):
        if not self.pattern_address:
            return False
        
        try:
            if enabled and not self.is_enabled:
                self.pm.write_bytes(self.pattern_address, b"\x90\x90", 2)
                self.is_enabled = True
            elif not enabled and self.is_enabled:
                self.pm.write_bytes(self.pattern_address, self.original_pattern_bytes, 2)
                self.is_enabled = False
            return True
        except:
            return False

    def run(self):
        while not hasattr(self.obsidian, "focused_process"):
            time.sleep(0.1)
        
        while True:
            time.sleep(0.1)
            if self.obsidian.focused_process != "cs2.exe":
                continue
            
            if self.obsidian.config["esp"]["glowing"]:
                self.set_glowing(True)
            else:
                self.set_glowing(False)
