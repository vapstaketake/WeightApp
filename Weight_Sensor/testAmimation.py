#TKinterでアニメーションを作成するテストコード
import os
import tkinter
import time
from PIL import Image, ImageTk

script_path = os.path.dirname(os.path.abspath(__file__))
charactor =  "CoffeeCup"

root = tkinter.Tk()
root.title("CoffeeAnimation")
root.geometry("500x380")
root['background']='#fff'

cup = Image.open("png/weight_coffee_UI/coffee_cup.png")
cupLevel = [Image.open("png/weight_coffee_UI/coffee_cup.png"),
        Image.open("png/weight_coffee_UI/Level1.png"),
        Image.open("png/weight_coffee_UI/Level2.png"),
        Image.open("png/weight_coffee_UI/Level3.png"),
        Image.open("png/weight_coffee_UI/Level4.png"),
        Image.open("png/weight_coffee_UI/Level5.png")]

def createface(n):
    default_cup = Image.alpha_composite(cup, cupLevel[n])
    return default_cup

charactor_image = ImageTk.PhotoImage(image=createface(1))
canvas = tkinter.Canvas(root, width=400, height=320, bd=0, highlightthickness=0, relief='ridge')
canvas['background']=root['background']
imagearea = canvas.create_image(0, 0, image=charactor_image, anchor=tkinter.NW)
canvas.pack()


def animation():
    global charactor_image
    for i in range(6):
        time.sleep(0.05)
        charactor_image = ImageTk.PhotoImage(image=createface(i))
        canvas.itemconfig(imagearea, image=charactor_image)
        canvas.update()
    for i in reversed(range(6)):
        time.sleep(0.05)
        charactor_image = ImageTk.PhotoImage(image=createface(i))
        canvas.itemconfig(imagearea, image=charactor_image)
        canvas.update()
    root.after(10, animation)


root.after(10, animation)
root.mainloop()