import pymem
import pymem.process
import requests
import win32api
import win32con
import time
import random

class TriggerBot:
    def __init__(self, obsidian):
        self.obsidian = obsidian
        self.random_delay = self.obsidian.config["triggerBot"]["randomDelay"]
        self.min_delay = self.obsidian.config["triggerBot"]["delay"]
        self.key_bind = chr(self.obsidian.config["triggerBot"]["bind"]) if self.obsidian.config["triggerBot"]["bind"] else "E"
        self.attack_all = not self.obsidian.config["triggerBot"]["onlyEnemies"]
        self.mode = "Hold"
        self.is_active = False
        self.prev_key_state = False
        self.pm, self.client = self._init_pymem()
        self.offsets = self._get_offsets()

    def _init_pymem(self):
        try:
            pm = pymem.Pymem("cs2.exe")
            client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
            return pm, client
        except Exception as e:
            print(f"Failed to initialize pymem: {e}")
            return None, None

    def _get_offsets(self):
        try:
            offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
            client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
            return {
                'dwEntityList': offsets['client.dll']['dwEntityList'],
                'dwLocalPlayerPawn': offsets['client.dll']['dwLocalPlayerPawn'],
                'm_iTeamNum': client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum'],
                'm_iHealth': client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth'],
                'm_iIDEntIndex': client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']
            }
        except Exception as e:
            print(f"Failed to fetch offsets: {e}")
            return {}

    def run(self):
        while not hasattr(self.obsidian, "focused_process"):
            time.sleep(0.1)
        
        if not self.pm or not self.client or not self.offsets:
            print("TriggerBot failed to initialize.")
            return

        while True:
            time.sleep(0.001)
            
            if not self.obsidian.config["triggerBot"]["enabled"]:
                time.sleep(0.1)
                self.is_active = False
                continue
            
            if self.obsidian.focused_process != "cs2.exe":
                time.sleep(1)
                self.is_active = False
                continue

            if self._should_shoot():
                self._shoot()

    def _should_shoot(self):
        key_pressed = win32api.GetAsyncKeyState(ord(self.key_bind)) & 0x8000
        
        if self.mode == "Toggle":
            if key_pressed and not self.prev_key_state:
                self.is_active = not self.is_active
                time.sleep(0.1)
            self.prev_key_state = key_pressed
            return self.is_active
        else:  # Hold mode
            return key_pressed

    def _shoot(self):
        try:
            player = self.pm.read_longlong(self.client + self.offsets['dwLocalPlayerPawn'])
            entity_id = self.pm.read_int(player + self.offsets['m_iIDEntIndex'])
            
            if entity_id > 0:
                ent_list = self.pm.read_longlong(self.client + self.offsets['dwEntityList'])
                ent_entry = self.pm.read_longlong(ent_list + 0x8 * (entity_id >> 9) + 0x10)
                entity = self.pm.read_longlong(ent_entry + 120 * (entity_id & 0x1FF))
                
                entity_team = self.pm.read_int(entity + self.offsets['m_iTeamNum'])
                player_team = self.pm.read_int(player + self.offsets['m_iTeamNum'])
                
                if self.attack_all or entity_team != player_team:
                    entity_hp = self.pm.read_int(entity + self.offsets['m_iHealth'])
                    if entity_hp > 0:
                        self._perform_click()
        except:
            time.sleep(0.03)

    def _perform_click(self):
        sleep_in = random.randint(self.min_delay, self.min_delay + self.random_delay)
        time.sleep(sleep_in / 10000)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        
        sleep_out = random.randint(self.min_delay, self.min_delay + self.random_delay)
        time.sleep(sleep_out / 10000)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
