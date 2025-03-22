import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')  # Tkinter互換のバックエンドを使用
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import subprocess
import time
import os
import sys
import threading

# 設定
MAX_POINTS = 100
UPDATE_INTERVAL = 200
EXECUTABLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_reader")
OFFSET = 8156931
FACTOR = 300.0 / 113318.0

# Windowsでの実行かどうかを確認
is_windows = sys.platform.startswith('win')
if is_windows:
    # Windows環境ではwiringPiを使わないモックモードを使用
    EXECUTABLE_PATH = "mock_weight_reader"
    print("Windows environment detected. Using mock weight data.")

class WeightPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weight Sensor Monitor")
        self.root.geometry("800x600")
        
        # 例外ハンドラを設定
        self._setup_exception_handling()
        
        # メインフレーム
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 設定フレーム
        self.settings_frame = ttk.Frame(self.main_frame)
        self.settings_frame.pack(fill=tk.X, pady=5)
        
        # オフセットとファクターの調整
        self.offset_var = tk.DoubleVar(value=OFFSET)
        self.factor_var = tk.DoubleVar(value=FACTOR)
        
        ttk.Label(self.settings_frame, text="Offset:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.settings_frame, textvariable=self.offset_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.settings_frame, text="Factor:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.settings_frame, textvariable=self.factor_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # 現在の重量表示
        self.weight_var = tk.StringVar(value="Weight: 0.0g")
        self.weight_label = ttk.Label(self.settings_frame, textvariable=self.weight_var, font=("Arial", 14, "bold"))
        self.weight_label.pack(side=tk.RIGHT, padx=10)
        
        # グラフフレーム
        self.graph_frame = ttk.Frame(self.main_frame)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Matplotlibの図を作成
        try:
            self.fig, self.ax = plt.subplots(figsize=(8, 5))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # グラフの初期設定
            self.line, = self.ax.plot([], [], 'b-', lw=2)
            self.ax.set_xlim(0, 60)
            self.ax.set_ylim(-10, 500)
            self.ax.set_xlabel('Time (seconds)')
            self.ax.set_ylabel('Weight (g)')
            self.ax.set_title('Real-time Weight Measurement')
            self.ax.grid(True)
            
            # データ保持用の配列
            self.times = np.array([])
            self.weights = np.array([])
            self.start_time = time.time()
        except Exception as e:
            messagebox.showerror("Graph Error", f"Failed to create graph: {e}")
            self._log_error(e)
        
        # 制御ボタン
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=5)
        
        self.running = False
        self.run_button = ttk.Button(self.control_frame, text="Start", command=self.toggle_run)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(self.control_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(self.control_frame, text="Save Data", command=self.save_data)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Starting application...")
        
        # 終了時の処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # システム環境に応じた実行準備
        self._prepare_executable()

    def _setup_exception_handling(self):
        """未処理の例外を捕捉するハンドラを設定"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            """未処理の例外を処理するハンドラ"""
            import traceback
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self._log_error(error_msg)
            messagebox.showerror("Error", f"An unexpected error occurred:\n{exc_value}")
        
        # 現在の例外ハンドラを保存
        self.default_exception_handler = sys.excepthook
        # 新しい例外ハンドラを設定
        sys.excepthook = handle_exception

    def _log_error(self, error):
        """エラーをログファイルに記録"""
        import datetime
        with open("error_log.txt", "a") as f:
            f.write(f"\n--- {datetime.datetime.now()} ---\n")
            f.write(str(error))
            f.write("\n")

    def _prepare_executable(self):
        """環境に応じた実行ファイルの準備"""
        try:
            if is_windows:
                # Windows環境ではモックスクリプトを作成
                self.create_mock_reader_file()
                self.status_var.set("Mock data generator ready")
            else:
                # Linux/Raspberry Pi環境では実行ファイルをコンパイル
                if not os.path.exists(EXECUTABLE_PATH):
                    self.status_var.set("Compiling executable...")
                    self.root.update()
                    cpp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hx711.cpp")
                    try:
                        subprocess.run(["g++", cpp_file, "-o", EXECUTABLE_PATH, "-lwiringPi"], check=True)
                        self.status_var.set("Compilation successful")
                    except subprocess.CalledProcessError:
                        self.status_var.set("Compilation error. Creating weight_reader.cpp...")
                        self.root.update()
                        self.create_weight_reader_file()
                        try:
                            subprocess.run(["g++", "weight_reader.cpp", "-o", EXECUTABLE_PATH, "-lwiringPi"], check=True)
                            self.status_var.set("Compilation successful")
                        except subprocess.CalledProcessError as e:
                            self.status_var.set("Failed to compile. Check your setup.")
                            messagebox.showerror("Compilation Error", f"Failed to compile: {e}")
                            self._log_error(e)
                else:
                    self.status_var.set("Executable found")
        except Exception as e:
            self.status_var.set(f"Error initializing: {e}")
            messagebox.showerror("Initialization Error", f"Error during initialization: {e}")
            self._log_error(e)

    def create_mock_reader_file(self):
        """Windows環境用のモックデータ生成スクリプト"""
        with open("mock_weight_reader.py", "w") as f:
            f.write("""
import random
import time

# 疑似的な重量データを生成
base_weight = 8300000
variation = 50000
reading = base_weight + random.uniform(-variation, variation)
print(reading)
            """)

    def create_weight_reader_file(self):
        with open("weight_reader.cpp", "w") as f:
            f.write("""
#include <iostream>
#include <wiringPi.h>

double readHx711Count(int GpioPinDT = 2, int GpioPinSCK = 3) {
    wiringPiSetupGpio();
    
    int i;
    unsigned int Count = 0;
    pinMode(GpioPinDT, OUTPUT);
    digitalWrite(GpioPinDT, HIGH);
    pinMode(GpioPinSCK, OUTPUT);
    digitalWrite(GpioPinSCK, LOW);
    pinMode(GpioPinDT, INPUT);
    while (digitalRead(GpioPinDT) == 1) {
        i = 0;
    }
    for (i = 0; i < 24; i++) {
        digitalWrite(GpioPinSCK, HIGH);
        Count = Count << 1;
        
        digitalWrite(GpioPinSCK, LOW);
        if (digitalRead(GpioPinDT) == 0) {
            Count = Count + 1;
        }
    }
    digitalWrite(GpioPinSCK, HIGH);
    Count = Count ^ 0x800000;
    digitalWrite(GpioPinSCK, LOW);
    return double(Count);
}

int main() {
    double reading = readHx711Count();
    std::cout << reading << std::endl;
    return 0;
}
            """)

    def get_weight(self):
        try:
            if is_windows:
                # Windowsではモックスクリプトを実行
                result = subprocess.run(["python", "mock_weight_reader.py"], 
                                      capture_output=True, text=True, check=True)
            else:
                # Linux/Raspberry Piではコンパイル済み実行ファイルを実行
                result = subprocess.run([EXECUTABLE_PATH], 
                                      capture_output=True, text=True, check=True)
                
            reading = float(result.stdout.strip())
            weight = (reading - self.offset_var.get()) * self.factor_var.get()
            return weight
        except (subprocess.CalledProcessError, ValueError) as e:
            self.status_var.set(f"Sensor reading error: {e}")
            self._log_error(f"Sensor reading error: {e}")
            return None

    def update_graph(self):
        """グラフデータを更新"""
        if not self.running:
            return
        
        try:
            weight = self.get_weight()
            
            if weight is not None:
                current_time = time.time() - self.start_time
                
                # データを追加
                self.times = np.append(self.times, current_time)
                self.weights = np.append(self.weights, weight)
                
                # データ点が多すぎる場合は古いものを削除
                if len(self.times) > MAX_POINTS:
                    self.times = self.times[-MAX_POINTS:]
                    self.weights = self.weights[-MAX_POINTS:]
                
                # X軸の自動スクロール
                if current_time > 60:
                    self.ax.set_xlim(current_time - 60, current_time)
                
                # グラフを更新
                self.line.set_data(self.times, self.weights)
                self.canvas.draw_idle()
                
                # 重量表示を更新
                self.weight_var.set(f"Weight: {weight:.1f}g")
            
            # 次の更新をスケジュール
            if self.running:
                self.root.after(UPDATE_INTERVAL, self.update_graph)
        except Exception as e:
            self.status_var.set(f"Error updating graph: {e}")
            self._log_error(f"Graph update error: {e}")
            messagebox.showerror("Graph Error", f"Error updating graph: {e}")
            self.running = False
            self.run_button.config(text="Start")

    def toggle_run(self):
        """測定の開始/停止を切り替え"""
        if self.running:
            self.running = False
            self.run_button.config(text="Start")
            self.status_var.set("Monitoring stopped")
        else:
            self.running = True
            self.run_button.config(text="Stop")
            self.status_var.set("Monitoring active")
            self.update_graph()

    def clear_graph(self):
        """グラフデータをクリア"""
        self.times = np.array([])
        self.weights = np.array([])
        self.start_time = time.time()
        self.line.set_data([], [])
        self.ax.set_xlim(0, 60)
        self.canvas.draw_idle()
        self.status_var.set("Graph cleared")

    def save_data(self):
        """現在のグラフデータを保存"""
        if len(self.times) == 0:
            messagebox.showinfo("No Data", "No data to save")
            return
            
        try:
            # ファイル名の設定
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 出力ディレクトリの作成
            os.makedirs("weight_data", exist_ok=True)
            
            # CSVファイルにデータを保存
            csv_filename = f"weight_data/weight_data_{timestamp}.csv"
            with open(csv_filename, "w") as f:
                f.write("Time,Weight\n")
                for t, w in zip(self.times, self.weights):
                    f.write(f"{t:.2f},{w:.2f}\n")
            
            # グラフ画像を保存
            img_filename = f"weight_data/weight_graph_{timestamp}.png"
            plt.savefig(img_filename)
            
            self.status_var.set(f"Data saved to {csv_filename}")
            messagebox.showinfo("Data Saved", f"Data saved to {csv_filename}\nGraph image saved to {img_filename}")
        except Exception as e:
            self.status_var.set(f"Error saving data: {e}")
            self._log_error(f"Save error: {e}")
            messagebox.showerror("Save Error", f"Failed to save data: {e}")

    def on_close(self):
        """アプリケーション終了時の処理"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.running = False
            self.root.destroy()


def main():
    """メイン関数"""
    try:
        root = tk.Tk()
        app = WeightPlotterApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        with open("crash_log.txt", "a") as f:
            f.write("\n--- CRASH LOG ---\n")
            f.write(traceback.format_exc())
        messagebox.showerror("Fatal Error", f"Application crashed: {e}\nSee crash_log.txt for details")


if __name__ == "__main__":
    main()
