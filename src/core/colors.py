import pyMeow as pm

class Colors:
    white = pm.get_color("white")
    whiteWatermark = pm.get_color("#f5f5ff")
    black = pm.get_color("black")
    blackFade = pm.fade_color(black, 0.6)
    red = pm.get_color("#e03636")
    green = pm.get_color("#43e06d")
