import matplotlib
matplotlib.use('Agg')  # 非対話型バックエンド
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import time
import os
import sys
from datetime import datetime

# 設定
MAX_POINTS = 100
UPDATE_INTERVAL = 200
EXECUTABLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_reader")
OFFSET = 8156931
FACTOR = -300.0 / 113318.0  # 極性を反転（マイナス記号を追加）
CALIBRATION_SAMPLES = 5     # キャリブレーション時のサンプル数

# Windowsでの実行かどうかを確認
is_windows = sys.platform.startswith('win')
if is_windows:
    MOCK_SCRIPT = "mock_weight_reader.py"
    print("Windows環境を検出しました。モックデータを使用します。")

class WeightPlotter:
    def __init__(self):
        # グラフ初期化
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        self.times = np.array([])
        self.raw_readings = np.array([])
        self.weights = np.array([])
        self.start_time = None  # キャリブレーション後に設定
        self.initial_reading = None
        
        # グラフの設定
        self.line_raw, = self.ax1.plot([], [], 'r-', lw=1.5)
        self.line_weight, = self.ax2.plot([], [], 'b-', lw=2)
        
        self.ax1.set_ylabel('Raw Reading')
        self.ax1.set_title('HX711 Sensor Raw Values')
        self.ax1.grid(True)
        
        self.ax2.set_xlim(0, 60)
        self.ax2.set_ylim(-10, 500)
        self.ax2.set_xlabel('Time (seconds)')
        self.ax2.set_ylabel('Weight (g)')
        self.ax2.set_title('Weight Measurement')
        self.ax2.grid(True)
        
        # システム環境に応じた実行準備
        self.prepare_executable()
        
        # 出力フォルダの作成
        self.output_dir = "weight_data"
        os.makedirs(self.output_dir, exist_ok=True)

    def prepare_executable(self):
        if is_windows:
            # Windows環境ではモックデータ生成スクリプトを作成
            self.create_mock_reader_file()
        else:
            # Linux/Raspberry Pi環境ではコンパイル確認
            if not os.path.exists(EXECUTABLE_PATH):
                print("Compiling executable...")
                cpp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hx711.cpp")
                try:
                    subprocess.run(["g++", cpp_file, "-o", EXECUTABLE_PATH, "-lwiringPi"], check=True)
                    print("Compilation successful")
                except subprocess.CalledProcessError:
                    print("Compilation error. Creating weight_reader.cpp...")
                    self.create_weight_reader_file()
                    try:
                        subprocess.run(["g++", "weight_reader.cpp", "-o", EXECUTABLE_PATH, "-lwiringPi"], check=True)
                        print("Compilation successful")
                    except subprocess.CalledProcessError:
                        print("ERROR: Failed to compile. Check your setup.")
                        sys.exit(1)

    def create_mock_reader_file(self):
        """Windows環境用のモックデータ生成スクリプト（極性反転対応）"""
        with open(MOCK_SCRIPT, "w") as f:
            f.write("""
import random
import time
import math

# 時間経過とともに変化する重量をシミュレート
start_time = time.time()
base_weight = 8300000  # 基本重量
variation = 50000      # ランダム変動幅
period = 20            # 周期（秒）

# 時間に基づく周期的な変動を生成
elapsed = time.time() - start_time
phase = elapsed % period / period  # 0～1の周期位置

# サイン波 + ランダム変動で疑似的な重量変化を生成
# 重量が増えるとセンサー値が減少する挙動をシミュレート（-1を掛ける）
cyclic = -1 * math.sin(phase * 2 * math.pi) * variation * 0.5
random_var = random.uniform(-variation * 0.2, variation * 0.2)

reading = base_weight + cyclic + random_var
print(reading)
""")

    def create_weight_reader_file(self):
        """重量センサー読み取り用のC++ソースファイル作成"""
        # ...existing code...

    def get_reading(self):
        """センサーからの生の読み取り値を取得"""
        try:
            if is_windows:
                # Windowsではモックスクリプトを実行
                result = subprocess.run([sys.executable, MOCK_SCRIPT], 
                                       capture_output=True, text=True, check=True)
            else:
                # Linux/Raspberry Piではコンパイル済み実行ファイルを実行
                result = subprocess.run([EXECUTABLE_PATH], 
                                       capture_output=True, text=True, check=True)
                
            reading = float(result.stdout.strip())
            return reading
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"Sensor reading error: {e}")
            return None

    def auto_calibrate(self):
        """自動キャリブレーション - 最初の数サンプルの平均値を基準とする"""
        print(f"自動キャリブレーションを開始します... {CALIBRATION_SAMPLES}個のサンプルを収集中...")
        
        # キャリブレーション用のデータを収集
        readings = []
        for i in range(CALIBRATION_SAMPLES):
            reading = self.get_reading()
            if reading is not None:
                readings.append(reading)
                print(f"キャリブレーション読み取り {i+1}/{CALIBRATION_SAMPLES}: {reading:.2f}")
            else:
                print(f"キャリブレーション読み取り {i+1}/{CALIBRATION_SAMPLES}: エラー")
            time.sleep(0.2)
        
        if readings:
            self.initial_reading = sum(readings) / len(readings)
            print(f"キャリブレーション完了: 初期値 = {self.initial_reading:.2f}")
            return True
        else:
            print("キャリブレーション失敗: 測定値が取得できませんでした")
            self.initial_reading = OFFSET  # フォールバック値
            return False

    def collect_data(self, duration=60, interval=0.2):
        """指定された期間、データを収集してファイルに保存（自動キャリブレーション機能付き）"""
        # まず自動キャリブレーションを実行
        if not self.auto_calibrate():
            print("キャリブレーションに失敗しました。デフォルト値を使用します。")
        
        # 開始時間をキャリブレーション後に設定
        self.start_time = time.time()
        
        print(f"{duration}秒間のデータを収集します...")
        end_time = time.time() + duration
        
        # 出力ファイル名の設定
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"weight_data_{timestamp}.csv")
        
        with open(filename, "w") as f:
            f.write("time,raw_reading,raw_diff,weight\n")
            f.write(f"0.00,{self.initial_reading:.2f},0.00,0.00\n")  # 初期値（ゼロポイント）
            
            while time.time() < end_time:
                reading = self.get_reading()
                if reading is not None:
                    current_time = time.time() - self.start_time
                    raw_diff = self.initial_reading - reading
                    weight = raw_diff * abs(FACTOR)  # 符号はFACTORで考慮済み
                    
                    # データを配列に追加
                    self.times = np.append(self.times, current_time)
                    self.raw_readings = np.append(self.raw_readings, reading)
                    self.weights = np.append(self.weights, weight)
                    
                    # データをファイルに書き込む
                    f.write(f"{current_time:.2f},{reading:.2f},{raw_diff:.2f},{weight:.2f}\n")
                    f.flush()  # すぐに書き込みを反映
                    
                    # コンソールに現在の重量を表示
                    print(f"Time: {current_time:.2f}s, Raw: {reading:.2f}, Diff: {raw_diff:.2f}, Weight: {weight:.2f}g")
                    
                    # 間隔を空ける
                    time.sleep(interval)
        
        # グラフを生成して保存
        self.generate_graph(filename)
        
        return filename

    def generate_graph(self, data_file):
        """収集したデータからグラフを生成して保存"""
        if len(self.times) == 0:
            print("No data to plot")
            return
            
        # 生値のグラフを更新
        self.line_raw.set_data(self.times, self.raw_readings)
        self.ax1.set_xlim(0, max(self.times) + 5)
        self.ax1.set_ylim(min(self.raw_readings) - 10000, max(self.raw_readings) + 10000)
        
        # 初期値の水平線を追加
        if not hasattr(self, 'initial_line'):
            self.initial_line = self.ax1.axhline(y=self.initial_reading, color='g', linestyle='--', 
                                               label=f'Initial: {self.initial_reading:.0f}')
        
        # 重量のグラフを更新
        self.line_weight.set_data(self.times, self.weights)
        self.ax2.set_xlim(0, max(self.times) + 5)
        
        # Y軸の範囲を調整
        min_weight = min(self.weights) - 10 if len(self.weights) > 0 else -10
        max_weight = max(self.weights) + 10 if len(self.weights) > 0 else 500
        self.ax2.set_ylim(min_weight, max_weight)
        
        # 平均値の水平線を追加
        avg_weight = np.mean(self.weights)
        if not hasattr(self, 'avg_line'):
            self.avg_line = self.ax2.axhline(y=avg_weight, color='r', linestyle='--', 
                                           label=f'Avg: {avg_weight:.1f}g')
        else:
            self.avg_line.set_ydata([avg_weight, avg_weight])
            self.avg_line.set_label(f'Avg: {avg_weight:.1f}g')
        
        # 凡例を更新
        self.ax1.legend()
        self.ax2.legend()
        
        # グラフのタイトルを更新
        self.ax2.set_title(f'Weight Measurement: Avg={avg_weight:.1f}g')
        
        # グラフ画像を保存
        graph_file = data_file.replace(".csv", ".png")
        plt.tight_layout()
        plt.savefig(graph_file)
        print(f"Graph saved to {graph_file}")
        
        return graph_file

    def run(self):
        """データ収集を開始"""
        try:
            # 60秒間データを収集
            data_file = self.collect_data(duration=60)
            print(f"Data collection completed. Data saved to {data_file}")
        except KeyboardInterrupt:
            print("\nData collection interrupted by user.")
            # 中断された場合でもグラフは生成
            if len(self.times) > 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                partial_file = os.path.join(self.output_dir, f"partial_data_{timestamp}.csv")
                self.generate_graph(partial_file)


if __name__ == "__main__":
    plotter = WeightPlotter()
    plotter.run()
