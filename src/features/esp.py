import threading
import time
import random
import dearpygui.dearpygui as dpg
import pyMeow as pm
import win32api
import ctypes
from src.core.colors import Colors

user32 = ctypes.WinDLL("user32")

class ESP:
    def __init__(self, obsidian):
        self.obsidian = obsidian

    def bind_listener(self):
        while not hasattr(self.obsidian, "focused_process"):
            time.sleep(0.1)
        
        while True:
            if self.obsidian.focused_process != "cs2.exe":
                time.sleep(1)
                continue
            
            time.sleep(0.001)
            bind = self.obsidian.config["esp"]["bind"]
            if win32api.GetAsyncKeyState(bind) == 0:
                continue
            
            self.obsidian.config["esp"]["enabled"] = not self.obsidian.config["esp"]["enabled"]
            if self.obsidian.config["esp"]["enabled"] and not self.obsidian.overlay_thread_exists:
                threading.Thread(target=self.run, daemon=True).start()
            
            while True:
                try:
                    from src.gui.gui import checkbox_toggle_esp
                    dpg.set_value(checkbox_toggle_esp, not dpg.get_value(checkbox_toggle_esp))
                    break
                except:
                    time.sleep(1)
                    pass
            
            while win32api.GetAsyncKeyState(bind) != 0:
                time.sleep(0.001)

    def run(self):
        self.obsidian.overlay_thread_exists = True
        
        while not hasattr(self.obsidian, "focused_process"):
            time.sleep(0.1)
        
        pm.overlay_init("Counter-Strike 2", fps=144, 
                       title="".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8)),
                       trackTarget=True)
        
        self.obsidian.overlay_window_handle = pm.get_window_handle()
        
        if self.obsidian.config["misc"]["obsbypass"]:
            user32.SetWindowDisplayAffinity(self.obsidian.overlay_window_handle, 0x00000011)
        else:
            user32.SetWindowDisplayAffinity(self.obsidian.overlay_window_handle, 0x00000000)
        
        while pm.overlay_loop():
            pm.begin_drawing()
            
            if self.obsidian.focused_process != "cs2.exe":
                pm.end_drawing()
                time.sleep(1)
                continue
            
            if self.obsidian.config["misc"]["watermark"]:
                self._draw_watermark()
            
            if not self.obsidian.config["esp"]["enabled"] and not self.obsidian.config["misc"]["watermark"]:
                pm.end_drawing()
                pm.overlay_close()
                break
            elif not self.obsidian.config["esp"]["enabled"]:
                pm.end_drawing()
                time.sleep(0.001)
                continue
            
            view_matrix = pm.r_floats(self.obsidian.proc, self.obsidian.mod + self.obsidian.offsets.dwViewMatrix, 16)
            
            for ent in self.obsidian.get_entities():
                self._draw_entity(ent, view_matrix)
            
            pm.end_drawing()
        
        self.obsidian.overlay_thread_exists = False

    def _draw_watermark(self):
        watermark = f"Obsidian | {pm.get_fps()} fps"
        x_pos = -(-(185 - pm.measure_text(watermark, 20)) // 2) + 1
        pm.draw_rectangle_rounded(5, 5, 180, 30, 0.2, 4, Colors.blackFade)
        pm.draw_rectangle_rounded_lines(5, 5, 180, 30, 0.2, 4, self.obsidian.esp_background_color, 2)
        pm.draw_text(watermark, x_pos, 11, 20, Colors.whiteWatermark)

    def _draw_entity(self, ent, view_matrix):
        try:
            if (ent.is_dormant or 
                (self.obsidian.config["esp"]["onlyEnemies"] and self.obsidian.local_team == ent.team) or 
                ent.health == 0):
                return
        except:
            pass
        
        if self.obsidian.config["esp"]["snapline"]:
            self._draw_snapline(ent, view_matrix)
        
        if ent.world_to_screen(view_matrix):
            self._draw_esp_elements(ent)

    def _draw_snapline(self, ent, view_matrix):
        try:
            bounds, pos = pm.world_to_screen_noexc(view_matrix, ent.bone_pos(6), 1)
            pos_x = pos["x"]
            pos_y = pos["y"]
            if not bounds:
                pos_x = pm.get_screen_width() - pos_x
                pos_y = pm.get_screen_height()
            width = pm.get_screen_width() / 2
            height = pm.get_screen_height() - 50
            pm.draw_line(width, height, pos_x, pos_y, self.obsidian.esp_color)
        except:
            pass

    def _draw_esp_elements(self, ent):
        head = ent.pos2d["y"] - ent.head_pos2d["y"]
        width = head / 2
        center = width / 2
        x_start = ent.head_pos2d["x"] - center
        y_start = ent.head_pos2d["y"] - center / 2
        
        if self.obsidian.config["esp"]["boxBackground"]:
            pm.draw_rectangle_rounded(
                x_start, y_start, width, head + center / 2,
                self.obsidian.config["esp"]["boxRounding"], 1, self.obsidian.esp_background_color
            )
        
        if self.obsidian.config["esp"]["box"]:
            pm.draw_rectangle_rounded_lines(
                x_start, y_start, width, head + center / 2,
                self.obsidian.config["esp"]["boxRounding"], 1, self.obsidian.esp_color, 1.2
            )
        
        if self.obsidian.config["esp"]["redHead"]:
            pm.draw_circle_sector(
                ent.head_pos2d["x"], ent.head_pos2d["y"], center / 3,
                0, 360, 0, Colors.red
            )
        
        if self.obsidian.config["esp"]["skeleton"]:
            self._draw_skeleton(ent)
        
        if self.obsidian.config["esp"]["health"]:
            self._draw_health_bar(ent, x_start, y_start, width, head, center)
        
        if self.obsidian.config["esp"]["name"]:
            pm.draw_text(
                ent.name,
                ent.head_pos2d["x"] - pm.measure_text(ent.name, 15) // 2,
                ent.head_pos2d["y"] - center / 2 - 15,
                15, Colors.white
            )

    def _draw_skeleton(self, ent):
        try:
            view_matrix = pm.r_floats(self.obsidian.proc, self.obsidian.mod + self.obsidian.offsets.dwViewMatrix, 16)
            
            bones = {
                'neck': pm.world_to_screen(view_matrix, ent.bone_pos(5), 1),
                'shoulder_r': pm.world_to_screen(view_matrix, ent.bone_pos(8), 1),
                'shoulder_l': pm.world_to_screen(view_matrix, ent.bone_pos(13), 1),
                'elbow_r': pm.world_to_screen(view_matrix, ent.bone_pos(9), 1),
                'elbow_l': pm.world_to_screen(view_matrix, ent.bone_pos(14), 1),
                'hand_r': pm.world_to_screen(view_matrix, ent.bone_pos(11), 1),
                'hand_l': pm.world_to_screen(view_matrix, ent.bone_pos(16), 1),
                'waist': pm.world_to_screen(view_matrix, ent.bone_pos(0), 1),
                'knee_r': pm.world_to_screen(view_matrix, ent.bone_pos(23), 1),
                'knee_l': pm.world_to_screen(view_matrix, ent.bone_pos(26), 1),
                'foot_r': pm.world_to_screen(view_matrix, ent.bone_pos(24), 1),
                'foot_l': pm.world_to_screen(view_matrix, ent.bone_pos(27), 1),
            }
            
            connections = [
                ('neck', 'shoulder_r'), ('neck', 'shoulder_l'),
                ('shoulder_l', 'elbow_l'), ('shoulder_r', 'elbow_r'),
                ('elbow_r', 'hand_r'), ('elbow_l', 'hand_l'),
                ('neck', 'waist'), ('waist', 'knee_r'), ('waist', 'knee_l'),
                ('knee_l', 'foot_l'), ('knee_r', 'foot_r')
            ]
            
            for start, end in connections:
                pm.draw_line(bones[start]["x"], bones[start]["y"], 
                           bones[end]["x"], bones[end]["y"], Colors.white, 1)
        except:
            pass

    def _draw_health_bar(self, ent, x_start, y_start, width, head, center):
        pm.draw_rectangle_rounded(
            ent.head_pos2d["x"] - center - 10,
            ent.head_pos2d["y"] - center / 2 + (head * 0 / 100),
            3, head + center / 2 - (head * 0 / 100),
            self.obsidian.config["esp"]["boxRounding"], 1, self.obsidian.esp_background_color
        )
        pm.draw_rectangle_rounded(
            ent.head_pos2d["x"] - center - 10,
            ent.head_pos2d["y"] - center / 2 + (head * (100 - ent.health) / 100),
            3, head + center / 2 - (head * (100 - ent.health) / 100),
            self.obsidian.config["esp"]["boxRounding"], 1, Colors.green
        )
