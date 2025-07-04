import json
import os

CONFIG_FILE_PATH = f"{os.environ['LOCALAPPDATA']}\\temp\\obsidian"

class ConfigListener(dict):
    def __init__(self, initial_dict):
        for k, v in initial_dict.items():
            if isinstance(v, dict):
                initial_dict[k] = ConfigListener(v)
        super().__init__(initial_dict)

    def __setitem__(self, item, value):
        if isinstance(value, dict):
            value = ConfigListener(value)
        super().__setitem__(item, value)
        
        # Import here to avoid circular imports
        from src.obsidian import Obsidian
        instance = Obsidian()
        if hasattr(instance, "config"):
            json.dump(instance.config, open(CONFIG_FILE_PATH, "w", encoding="utf-8"), indent=4)
