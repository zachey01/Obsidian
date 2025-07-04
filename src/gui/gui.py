import dearpygui.dearpygui as dpg
import win32gui
import win32con
import ctypes
import threading
import pyMeow as pm
from src.core.colors import Colors
from src.localization import Localization
from src.utils.window_effects import WindowsWindowEffect, get_hwnd
import os

user32 = ctypes.WinDLL("user32")
version = "1.0.0"

checkbox_toggle_esp = None
button_bind_esp = None
checkbox_toggle_triggerbot = None
button_bind_triggerbot = None

def create_gui(obsidian):
    global checkbox_toggle_esp, button_bind_esp, checkbox_toggle_triggerbot, button_bind_triggerbot
    
    loc = Localization()
    window_effect = WindowsWindowEffect()
    
    ui_width = 800
    ui_height = 500
    dpg.create_context()

    def toggle_esp(id, value):
        obsidian.config["esp"]["enabled"] = value
        if value and not obsidian.overlay_thread_exists:
            threading.Thread(target=obsidian.esp.run, daemon=True).start()

    waiting_for_key_esp = [False]
    def status_bind_esp(id):
        if not waiting_for_key_esp[0]:
            with dpg.handler_registry(tag="Esp Bind Handler"):
                dpg.add_key_press_handler(callback=lambda id, value: set_bind_esp(id, value, obsidian))
            dpg.set_item_label(button_bind_esp, "...")
            waiting_for_key_esp[0] = True

    def set_bind_esp(id, value, obsidian):
        if waiting_for_key_esp[0]:
            obsidian.config["esp"]["bind"] = value
            dpg.set_item_label(button_bind_esp, f"{loc.get('esp.bind')}: {chr(value)}")
            dpg.delete_item("Esp Bind Handler")
            waiting_for_key_esp[0] = False

    def toggle_esp_box(id, value):
        obsidian.config["esp"]["box"] = value

    def toggle_esp_box_background(id, value):
        obsidian.config["esp"]["boxBackground"] = value

    def toggle_esp_skeleton(id, value):
        obsidian.config["esp"]["skeleton"] = value

    def toggle_esp_red_head(id, value):
        obsidian.config["esp"]["redHead"] = value

    def toggle_esp_snapline(id, value):
        obsidian.config["esp"]["snapline"] = value

    def toggle_esp_only_enemies(id, value):
        obsidian.config["esp"]["onlyEnemies"] = value

    def toggle_esp_name(id, value):
        obsidian.config["esp"]["name"] = value

    def toggle_esp_health(id, value):
        obsidian.config["esp"]["health"] = value

    def toggle_esp_glowing(id, value):
        obsidian.config["esp"]["glowing"] = value
        if value:
            threading.Thread(target=obsidian.glowing.run, daemon=True).start()

    def set_esp_color(id, value):
        obsidian.config["esp"]["color"] = {
            "r": value[0]/255, "g": value[1]/255, 
            "b": value[2]/255, "a": value[3]/255
        }
        obsidian.esp_color = pm.new_color_float(value[0]/255, value[1]/255, value[2]/255, value[3]/255)
        obsidian.esp_background_color = pm.fade_color(obsidian.esp_color, 0.3)

    def set_esp_box_rounding(id, value):
        obsidian.config["esp"]["boxRounding"] = value

    def toggle_triggerbot(id, value):
        obsidian.config["triggerBot"]["enabled"] = value
        obsidian.update_triggerbot()

    waiting_for_key_triggerbot = [False]
    def status_bind_triggerbot(id):
        if not waiting_for_key_triggerbot[0]:
            with dpg.handler_registry(tag="TriggerBot Bind Handler"):
                dpg.add_key_press_handler(callback=lambda id, value: set_bind_triggerbot(id, value, obsidian))
            dpg.set_item_label(button_bind_triggerbot, "...")
            waiting_for_key_triggerbot[0] = True

    def set_bind_triggerbot(id, value, obsidian):
        if waiting_for_key_triggerbot[0]:
            obsidian.config["triggerBot"]["bind"] = value
            dpg.set_item_label(button_bind_triggerbot, f"{loc.get('triggerbot.bind')}: {chr(value)}")
            dpg.delete_item("TriggerBot Bind Handler")
            waiting_for_key_triggerbot[0] = False
            obsidian.update_triggerbot()

    def toggle_triggerbot_only_enemies(id, value):
        obsidian.config["triggerBot"]["onlyEnemies"] = value
        obsidian.update_triggerbot()

    def slider_triggerbot_min_delay(id, value):
        obsidian.config["triggerBot"]["delay"] = value
        obsidian.update_triggerbot()

    def slider_triggerbot_random_delay(id, value):
        obsidian.config["triggerBot"]["randomDelay"] = value
        obsidian.update_triggerbot()

    def toggle_fov(id, value):
        obsidian.config["fov"]["enabled"] = value
        if value:
            threading.Thread(target=obsidian.fov.run, daemon=True).start()
        else:
            obsidian.config["fov"]["value"] = 90
            obsidian.fov.reset_fov()

    def set_fov_value(id, value):
        obsidian.config["fov"]["value"] = value
        if obsidian.config["fov"]["enabled"]:
            obsidian.fov.set_fov(value)

    def toggle_watermark(id, value):
        obsidian.config["misc"]["watermark"] = value
        if value and not obsidian.overlay_thread_exists:
            threading.Thread(target=obsidian.esp.run, daemon=True).start()

    def toggle_obs_bypass(id, value):
        obsidian.config["misc"]["obsbypass"] = value
        if value:
            if hasattr(obsidian, 'gui_window_handle') and obsidian.gui_window_handle:
                user32.SetWindowDisplayAffinity(obsidian.gui_window_handle, 0x00000011)
            if hasattr(obsidian, 'overlay_window_handle') and obsidian.overlay_window_handle:
                user32.SetWindowDisplayAffinity(obsidian.overlay_window_handle, 0x00000011)
        else:
            if hasattr(obsidian, 'gui_window_handle') and obsidian.gui_window_handle:
                user32.SetWindowDisplayAffinity(obsidian.gui_window_handle, 0x00000000)
            if hasattr(obsidian, 'overlay_window_handle') and obsidian.overlay_window_handle:
                user32.SetWindowDisplayAffinity(obsidian.overlay_window_handle, 0x00000000)

    def toggle_save_settings(id, value):
        obsidian.config["settings"]["saveSettings"] = value

    def toggle_always_on_top(id, value):
        if value:
            win32gui.SetWindowPos(obsidian.gui_window_handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        else:
            win32gui.SetWindowPos(obsidian.gui_window_handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def change_language(sender, app_data):
        loc.set_language(app_data)
        refresh_gui_text()

    def toggle_acrylic_effect(id, value):
        obsidian.config["settings"]["acrylicEffect"] = value
        if value:
            # Применяем акриловый эффект к GUI окну
            if hasattr(obsidian, 'gui_window_handle') and obsidian.gui_window_handle:
                window_effect.setAeroEffect(obsidian.gui_window_handle)
        else:
            # Отключаем акриловый эффект
            if hasattr(obsidian, 'gui_window_handle') and obsidian.gui_window_handle:
                # Сбрасываем эффект на обычное окно
                window_effect.accentPolicy.AccentState = 0
                window_effect.SetWindowCompositionAttribute(obsidian.gui_window_handle, ctypes.pointer(window_effect.winCompAttrData))

    def refresh_gui_text():
        pass

    title = f"[v{version}] {loc.get('title')}"
    
    with dpg.window(label=title, width=ui_width, height=ui_height, 
                   no_collapse=True, no_move=True, no_resize=True, 
                   on_close=lambda: os._exit(0)) as window:
        
        with dpg.tab_bar():
            with dpg.tab(label=loc.get("tabs.esp")):
                dpg.add_spacer(width=75)
                with dpg.group(horizontal=True):
                    checkbox_toggle_esp = dpg.add_checkbox(label=loc.get("esp.toggle"), 
                                                          default_value=obsidian.config["esp"]["enabled"], 
                                                          callback=toggle_esp)
                    button_bind_esp = dpg.add_button(label=loc.get("esp.bind"), callback=status_bind_esp)
                    bind = obsidian.config["esp"]["bind"]
                    if bind != 0:
                        dpg.set_item_label(button_bind_esp, f"{loc.get('esp.bind')}: {chr(bind)}")
                
                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)
                
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label=loc.get("esp.box"), default_value=obsidian.config["esp"]["box"], 
                                   callback=toggle_esp_box)
                    dpg.add_checkbox(label=loc.get("esp.background"), default_value=obsidian.config["esp"]["boxBackground"], 
                                   callback=toggle_esp_box_background)
                
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label=loc.get("esp.skeleton"), default_value=obsidian.config["esp"]["skeleton"], 
                                   callback=toggle_esp_skeleton)
                    dpg.add_checkbox(label=loc.get("esp.red_head"), default_value=obsidian.config["esp"]["redHead"], 
                                   callback=toggle_esp_red_head)
                
                dpg.add_checkbox(label=loc.get("esp.snapline"), default_value=obsidian.config["esp"]["snapline"], 
                               callback=toggle_esp_snapline)
                dpg.add_checkbox(label=loc.get("esp.only_enemies"), default_value=obsidian.config["esp"]["onlyEnemies"], 
                               callback=toggle_esp_only_enemies)
                dpg.add_checkbox(label=loc.get("esp.show_name"), default_value=obsidian.config["esp"]["name"], 
                               callback=toggle_esp_name)
                dpg.add_checkbox(label=loc.get("esp.show_health"), default_value=obsidian.config["esp"]["health"], 
                               callback=toggle_esp_health)
                
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label=loc.get("esp.glowing"), default_value=obsidian.config["esp"]["glowing"], 
                                   callback=toggle_esp_glowing)
                    dpg.add_text(default_value=loc.get("esp.glowing_warning"), color=(255, 100, 100))
                
                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)
                
                dpg.add_color_picker(label=loc.get("esp.global_color"), 
                                   default_value=(obsidian.config["esp"]["color"]["r"]*255,
                                                obsidian.config["esp"]["color"]["g"]*255,
                                                obsidian.config["esp"]["color"]["b"]*255,
                                                obsidian.config["esp"]["color"]["a"]*255),
                                   width=150, no_inputs=True, callback=set_esp_color)
                
                dpg.add_slider_float(label=loc.get("esp.box_rounding"), 
                                   default_value=obsidian.config["esp"]["boxRounding"],
                                   min_value=0, max_value=1, clamped=True, format="%.1f", 
                                   callback=set_esp_box_rounding, width=250)

            with dpg.tab(label=loc.get("tabs.triggerbot")):
                dpg.add_spacer(width=75)
                with dpg.group(horizontal=True):
                    checkbox_toggle_triggerbot = dpg.add_checkbox(label=loc.get("triggerbot.toggle"), 
                                                                default_value=obsidian.config["triggerBot"]["enabled"], 
                                                                callback=toggle_triggerbot)
                    button_bind_triggerbot = dpg.add_button(label=loc.get("triggerbot.bind"), callback=status_bind_triggerbot)
                    bind = obsidian.config["triggerBot"]["bind"]
                    if bind != 0:
                        dpg.set_item_label(button_bind_triggerbot, f"{loc.get('triggerbot.bind')}: {chr(bind)}")
                
                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)
                
                dpg.add_checkbox(label=loc.get("triggerbot.only_enemies"), default_value=obsidian.config["triggerBot"]["onlyEnemies"], 
                               callback=toggle_triggerbot_only_enemies)
                
                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)
                
                dpg.add_slider_int(label=loc.get("triggerbot.min_delay"), default_value=obsidian.config["triggerBot"]["delay"],
                                 min_value=0, max_value=500, callback=slider_triggerbot_min_delay, width=250)
                dpg.add_slider_int(label=loc.get("triggerbot.random_delay"), default_value=obsidian.config["triggerBot"]["randomDelay"],
                                 min_value=0, max_value=200, callback=slider_triggerbot_random_delay, width=250)

            with dpg.tab(label=loc.get("tabs.fov")):
                dpg.add_spacer(width=75)
                dpg.add_checkbox(label=loc.get("fov.enable"), default_value=obsidian.config["fov"]["enabled"], 
                               callback=toggle_fov)
                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)
                dpg.add_slider_int(label=loc.get("fov.value"), default_value=obsidian.config["fov"]["value"],
                                 min_value=60, max_value=120, callback=set_fov_value, width=250)

            with dpg.tab(label=loc.get("tabs.misc")):
                dpg.add_spacer(width=75)
                dpg.add_checkbox(label=loc.get("misc.watermark"), default_value=obsidian.config["misc"]["watermark"], 
                               callback=toggle_watermark)
                dpg.add_checkbox(label=loc.get("misc.obs_bypass"), 
                                default_value=obsidian.config["misc"].get("obsbypass", False), 
                                callback=toggle_obs_bypass)

            with dpg.tab(label=loc.get("tabs.settings")):
                dpg.add_spacer(width=75)
                dpg.add_checkbox(label=loc.get("settings.save_settings"), default_value=obsidian.config["settings"]["saveSettings"], 
                               callback=toggle_save_settings)
                dpg.add_spacer(width=75)
                dpg.add_checkbox(label=loc.get("settings.always_on_top"), callback=toggle_always_on_top)
                dpg.add_checkbox(label=loc.get("settings.acrylic_effect"), default_value=obsidian.config["settings"]["acrylicEffect"], 
                               callback=toggle_acrylic_effect)
                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)
                
                languages = list(loc.get_available_languages().values())
                dpg.add_combo(label=loc.get("settings.language"), items=languages, 
                            default_value=loc.get_available_languages()[loc.current_language],
                            callback=lambda s, v: change_language(s, list(loc.get_available_languages().keys())[languages.index(v)]))
                
                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)
                dpg.add_text(default_value=loc.get("settings.credits"))
                dpg.add_text(default_value=loc.get("settings.github"))

    def drag_viewport(sender, app_data, user_data):
        if dpg.get_mouse_pos(local=False)[1] <= 40:
            drag_deltas = app_data
            viewport_pos = dpg.get_viewport_pos()
            new_x = viewport_pos[0] + drag_deltas[1]
            new_y = max(viewport_pos[1] + drag_deltas[2], 0)
            dpg.set_viewport_pos([new_x, new_y])

    with dpg.handler_registry():
        dpg.add_mouse_drag_handler(button=0, threshold=0.0, callback=drag_viewport)

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (15, 15, 15, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (25, 25, 25, 255))
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (40, 40, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60, 60, 60, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (80, 80, 80, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (50, 50, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (70, 70, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Tab, (35, 35, 35, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (55, 55, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, (75, 75, 75, 255))
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)

    dpg.bind_theme(global_theme)
    dpg.create_viewport(title=title, width=ui_width, height=ui_height, 
                       decorated=False, resizable=False)
    dpg.show_viewport()
    
    obsidian.gui_window_handle = win32gui.FindWindow(None, title)
    
    if obsidian.config["settings"]["acrylicEffect"]:
        window_effect.setAeroEffect(obsidian.gui_window_handle)
    
    dpg.setup_dearpygui()
    dpg.start_dearpygui()
