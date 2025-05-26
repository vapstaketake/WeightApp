import os
from PIL import Image, ImageTk
from header import EXECUTABLE_PATH,PATH

default_cup=Image.open(os.path.join(PATH,"png","weight_coffee_UI","coffee_cup.png"))
cupLevel = [Image.open(os.path.join(PATH,"png","weight_coffee_UI","coffee_cup.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level1.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level2.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level3.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level4.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level5.png"))]

waitUI_zun_file_names = ["normal_zun.png", "normal_zun_float.png"]
waitUI_zun_Animation = []
for waitUI_zun_file_name in waitUI_zun_file_names:
    img_path = os.path.join(PATH, "png", "zundamon", waitUI_zun_file_name)
    img = Image.open(img_path).resize((129, 123))
    waitUI_zun_Animation.append(img)
 
UI_zun_file_names = ["normal_zun.png", "zun_ani1.png", "zun_ani2.png", "zun_ani3.png", "zun_ani4.png", "zun_ani5.png"]
UI_zun_Animation = []
for UI_zun_file_name in UI_zun_file_names:
    img_path = os.path.join(PATH, "png", "zundamon", UI_zun_file_name)
    img = Image.open(img_path).resize((129, 123))
    UI_zun_Animation.append(img)