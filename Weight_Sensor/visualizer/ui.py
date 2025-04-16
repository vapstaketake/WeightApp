import tkinter as tk
import mock_weight_reader as mock
import importlib
import os
import time
import numpy as np
from tkinter import PhotoImage
from PIL import Image, ImageTk
from header import EXECUTABLE_PATH,PATH
from hx711_wrapper import HX711

count=0 #テスト用
before_value=10

def demo_wave():
    #アニメーションテスト用に標準のサイン波を生成
    frequency = 5  # 周波数（Hz）
    sampling_rate = 1000  # サンプリングレート（Hz）
    duration = 1.0  # 秒
    amplitude = 1.0  # 振幅
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    sin_wave = amplitude * np.sin(2 * np.pi * frequency * t) + amplitude
    return(sin_wave)

def start_realtime_display():
    try:
        # 入力されたカフェイン量を取得
        caffeine_amount = float(caffeine_entry.get())  
        
        # 入力されたカフェイン量を表示
        label.config(text=f"カフェイン量:コーヒーの粉100gに対して{caffeine_amount} mg")  
        
        # 入力フォームを非表示にする
        caffeine_label.pack_forget()
        caffeine_entry.pack_forget()
        start_button.pack_forget()

        # リアルタイム表示の開始
        update_value(caffeine_amount)
    except ValueError:
        label.config(text="無効な入力です。数字を入力してください。")  

def update_value(caffeine_amount):
    #テスト用↓(sin波を使用)
    global count,before_value
    #time.sleep(0.05)
    value=demo_wave()
    new_value=round(value[count],2)
    count += 1

    #mockから値を取得↓
    #importlib.reload(mock)
    #new_value = round(mock.reading,2)
    
    #センサーからの生の読み取り値を取得↓
    #new_value = HX711.get_raw_reading(EXECUTABLE_PATH)

    #重さ変化を表示
    caffeine_value=new_value*caffeine_amount #カフェイン計算方法はわからん！
    
    if new_value>=0 and new_value <0.33:
        check_value=0
    elif new_value>=0.33 and new_value <0.66:
        check_value=1
    elif new_value>=0.66 and new_value <0.99:
        check_value=2
    elif new_value>=0.99 and new_value <1.32:
        check_value=3
    elif new_value>=1.32 and new_value <=1.65:
        check_value=4
    else:
        check_value=5
    
    if before_value != check_value:
        Animation(check_value)
        before_value=check_value
    
    label.config(text=f"コーヒーの粉: {new_value} g\nカフェイン量: {round(caffeine_value,2)} mg")
    root.after(10, update_value,caffeine_amount)  # 0.1秒ごとに更新

def Animation(Levelvalue):
    #コーヒーカップのアニメーション
    global Amimation_image
    Amimation_image=ImageTk.PhotoImage(image=createcup(default_cup,Levelvalue))
    canvas.itemconfig(imagearea, image=Amimation_image)

def createcup(cup,n):
    return_cup = Image.alpha_composite(cup, cupLevel[n])
    return return_cup

# Tkinterウィンドウを作成
root = tk.Tk()
root.title("カフェイン量の入力とリアルタイム表示")
root.geometry("800x600")
root.resizable(False, False)

default_cup=Image.open(os.path.join(PATH,"png","weight_coffee_UI","coffee_cup.png"))
cupLevel = [Image.open(os.path.join(PATH,"png","weight_coffee_UI","coffee_cup.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level1.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level2.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level3.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level4.png")),
        Image.open(os.path.join(PATH,"png","weight_coffee_UI","Level5.png"))]
default_image=ImageTk.PhotoImage(image=createcup(default_cup,0))

#コーヒーのアイコンを設定して表示
canvas = tk.Canvas(root, width=400, height=320, bd=0, highlightthickness=0, relief='ridge')
imagearea = canvas.create_image(0, 0, image=default_image, anchor=tk.NW)
canvas.pack(side="top", pady=10)

# カフェイン量の入力を促すラベルとエントリー
caffeine_label = tk.Label(root, text="コーヒーの粉100gに対してのカフェイン量(mg) を入力:", font=("Helvetica", 14))
caffeine_label.pack(pady=10)

caffeine_entry = tk.Entry(root, font=("Helvetica", 14))
caffeine_entry.pack(pady=10)

# 入力開始ボタン
start_button = tk.Button(root, text="開始", font=("Helvetica", 14), command=start_realtime_display)
start_button.pack(pady=10)

label = tk.Label(root, text="カフェイン量: --", font=("Helvetica", 20))
label.pack(pady=20)

root.mainloop()
