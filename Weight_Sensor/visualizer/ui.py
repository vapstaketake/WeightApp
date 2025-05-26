import tkinter as tk
import importlib
import mock_weight_reader as moc
import ImageOpen as io
import DemoWave as demo
from PIL import Image, ImageTk
from header import EXECUTABLE_PATH,PATH
from hx711_wrapper import HX711

count=0
before_value=10
is_animating = True
dir=1

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
    global count,before_value
    #テスト用↓(sin波を使用)
    value=demo.sin_wave
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
    if count % 50 ==0:
        Animation2()
    label.config(text=f"コーヒーの粉: {new_value} g\nカフェイン量: {round(caffeine_value,2)} mg")
    root.after(10, update_value,caffeine_amount)  # 0.1秒ごとに更新

def Animation(Levelvalue):
    global Amimation_image,zun_Animation_image
    #コーヒーカップのアニメーション
    Amimation_image=ImageTk.PhotoImage(image=createcup(default_cup,Levelvalue))
    canvas.itemconfig(imagearea_cup, image=Amimation_image)
    #ずんだもんのアニメーション
    zun_Animation_image=ImageTk.PhotoImage(image=createzundamon(UI_zun[Levelvalue],Levelvalue))
    canvas.itemconfig(imagearea_zun, image=zun_Animation_image)

def Animation2():
    global dir
    canvas.move(imagearea_zun,0,dir*5) 
    dir=(-1)*dir

def wait_Animation(direction=1):
    if not is_animating:
        return
    canvas.move(imagearea_zun,0,direction*5) 
    canvas.after(500,wait_Animation,-direction)

def createcup(cup,n):
    return_cup = Image.alpha_composite(cup, cupLevel[n])
    return return_cup

def createzundamon(zun,n):
    return_zun = Image.alpha_composite(zun,UI_zun[n])
    return return_zun

def stop_animation():
    global is_animating
    is_animating = False

def combined_function():
    start_realtime_display()
    stop_animation()

# Tkinterウィンドウを作成
root = tk.Tk()
root.title("カフェイン量の入力とリアルタイム表示")
root.geometry("800x600")
root.resizable(False, False)

#画像読み込み
default_cup=io.default_cup
cupLevel=io.cupLevel
wait_zun=io.waitUI_zun_Animation
UI_zun=io.UI_zun_Animation

#デフォルト作成
default_coffee_image=ImageTk.PhotoImage(image=createcup(default_cup,0))
default_zundamon_image=ImageTk.PhotoImage(image=createzundamon(UI_zun[0],0))

#コーヒー＆ずんだもんのアイコンを設定して表示
canvas = tk.Canvas(root, width=400, height=320, bd=0, highlightthickness=0, relief='ridge')
imagearea_cup = canvas.create_image(0, 0, image=default_coffee_image, anchor=tk.NW)
imagearea_zun = canvas.create_image(290, 140, image=default_zundamon_image, anchor=tk.NW)
canvas.pack(side="top", pady=10)

wait_Animation()

# カフェイン量の入力を促すラベルとエントリー
caffeine_label = tk.Label(root, text="コーヒーの粉100gに対してのカフェイン量(mg) を入力:", font=("Helvetica", 14))
caffeine_label.pack(pady=10)

caffeine_entry = tk.Entry(root, font=("Helvetica", 14))
caffeine_entry.pack(pady=10)

# 入力開始ボタン
start_button = tk.Button(root, text="開始", font=("Helvetica", 14), command=combined_function)
start_button.pack(pady=10)

label = tk.Label(root, text="カフェイン量: --", font=("Helvetica", 20))
label.pack(pady=20)

root.mainloop()
