import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from datetime import datetime, timedelta
import time
from collections import deque
import threading

class WeightVisualizer:
    """
    重量データをリアルタイムで可視化するクラス
    """
    def __init__(self, data_source, window_size=100, update_interval=100):
        """
        初期化
        
        Args:
            data_source: データを取得するオブジェクト (get_weight_data メソッドを持つ)
            window_size (int): グラフに表示するデータポイントの数
            update_interval (int): グラフの更新間隔 (ミリ秒)
        """
        self.data_source = data_source
        self.window_size = window_size
        self.update_interval = update_interval
        
        # データを保持するバッファ
        self.timestamps = deque(maxlen=window_size)
        self.weights = deque(maxlen=window_size)
        
        # 終了フラグ
        self.running = False
        
        # GUIの構築
        self.root = tk.Tk()
        self.root.title("重量センサーデータ可視化")
        self.root.geometry("800x600")
        
        # グラフの設定
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.line, = self.ax.plot([], [], 'b-')
        
        self.ax.set_title("リアルタイム重量データ")
        self.ax.set_xlabel("時間")
        self.ax.set_ylabel("重量 (g)")
        self.ax.grid(True)
        
        # グラフのキャンバス
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # コントロールフレーム
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X)
        
        # 重量追加ボタン
        self.weight_entry = tk.Entry(control_frame, width=10)
        self.weight_entry.insert(0, "10")
        self.weight_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        add_button = tk.Button(control_frame, text="重量追加", command=self.add_weight)
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 現在の重量表示
        self.weight_label = tk.Label(control_frame, text="現在の重量: 0.0 g")
        self.weight_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def add_weight(self):
        """ユーザーが入力した重量を追加する"""
        try:
            amount = float(self.weight_entry.get())
            self.data_source.add_weight(amount)
        except ValueError:
            pass
    
    def update_plot(self):
        """グラフを更新する"""
        timestamp, weight = self.data_source.get_weight_data()
        
        self.timestamps.append(timestamp)
        self.weights.append(weight)
        
        # 重量表示の更新
        self.weight_label.config(text=f"現在の重量: {weight:.2f} g")
        
        # グラフデータの更新
        self.line.set_data(self.timestamps, self.weights)
        
        # 軸の調整
        if len(self.timestamps) > 0:
            self.ax.set_xlim(
                min(self.timestamps),
                max(self.timestamps) + timedelta(seconds=0.5)
            )
            ymin = min(self.weights) - 1 if self.weights else 0
            ymax = max(self.weights) + 1 if self.weights else 10
            self.ax.set_ylim(max(0, ymin), ymax)
            
            # 日付フォーマットの設定
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            self.fig.autofmt_xdate()
        
        self.canvas.draw()
        
        if self.running:
            self.root.after(self.update_interval, self.update_plot)
    
    def start(self):
        """可視化を開始する"""
        self.running = True
        self.update_plot()
        self.root.mainloop()
    
    def stop(self):
        """可視化を停止する"""
        self.running = False
