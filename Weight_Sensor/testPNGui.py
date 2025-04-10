#TKinterでpngを表示できなくなったからテスト用　<-- VScodeから実行すると表示されないけどコマンドラインから実行すれば正常に表示された！

import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()
root.title("画像表示テスト")

# フルパスに変更して確認
image_path = "/Users/shikakutarou/Git/weight/WeightApp/Weight_Sensor/png/sample.png"  # ← パスを自分のに書き換えて！
image = Image.open(image_path)

# サイズを変えてみる（大きすぎて表示できてない場合もあるので）
image = image.resize((300, 300))

photo = ImageTk.PhotoImage(image)

label = tk.Label(root, image=photo)
label.image = photo
label.pack()

root.mainloop()
