import tkinter as tk
import mock_weight_reader as mock
import importlib
import os
import numpy as np
from tkinter import PhotoImage
from PIL import Image, ImageTk
from header import EXECUTABLE_PATH,PATH
from hx711_wrapper import HX711

count=0 #テスト用

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
    global count
    value=demo_wave()
    new_value=value[count]
    count += 1

    #mockから値を取得↓
    #importlib.reload(mock)
    #new_value = round(mock.reading,2)
    
    #センサーからの生の読み取り値を取得↓
    #new_value = HX711.get_raw_reading(EXECUTABLE_PATH)
    
    caffeine_value=new_value*caffeine_amount #カフェイン計算方法はわからん！
    label.config(text=f"コーヒーの粉: {new_value} g\nカフェイン量: {caffeine_value} mg")
    root.after(100, update_value,caffeine_amount)  # 0.1秒ごとに更新

# Tkinterウィンドウを作成
root = tk.Tk()
root.title("カフェイン量の入力とリアルタイム表示")
root.geometry("800x600")
root.resizable(False, False)

photo=Image.open(os.path.join(PATH,"png","weight_coffee_UI","coffee_cup.png"))
image=ImageTk.PhotoImage(photo)

# コーヒーのアイコンを設定して表示
image_label = tk.Label(root, image=image)
image_label.pack(side="top", pady=10)  # 上部に表示

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
