import matplotlib
# GUI表示の前にバックエンドを設定
matplotlib.use('Agg')  # 非対話型バックエンド（画像出力用）
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
FACTOR = 300.0 / 113318.0

# Windowsでの実行かどうかを確認
is_windows = sys.platform.startswith('win')
if is_windows:
    # Windows環境ではwiringPiを使わないモックモードを使用
    EXECUTABLE_PATH = "mock_weight_reader"
    print("Windows environment detected. Using mock weight data.")

class WeightPlotter:
    def __init__(self):
        # グラフ初期化
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.times = np.array([])
        self.weights = np.array([])
        self.start_time = time.time()
        
        # グラフの設定
        self.line, = self.ax.plot([], [], 'b-', lw=2)
        self.ax.set_xlim(0, 60)
        self.ax.set_ylim(-10, 500)
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Weight (g)')
        self.ax.set_title('Real-time Weight Measurement')
        self.ax.grid(True)
        
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
            weight = (reading - OFFSET) * FACTOR
            return weight
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"Sensor reading error: {e}")
            return None

    def collect_data(self, duration=60, interval=0.2):
        """指定された期間、データを収集してファイルに保存"""
        print(f"Collecting weight data for {duration} seconds...")
        end_time = time.time() + duration
        
        # 出力ファイル名の設定
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"weight_data_{timestamp}.csv")
        
        with open(filename, "w") as f:
            f.write("time,raw_reading,weight\n")
            
            while time.time() < end_time:
                weight = self.get_weight()
                if weight is not None:
                    current_time = time.time() - self.start_time
                    self.times = np.append(self.times, current_time)
                    self.weights = np.append(self.weights, weight)
                    
                    # データをファイルに書き込む
                    f.write(f"{current_time:.2f},{OFFSET + weight/FACTOR:.2f},{weight:.2f}\n")
                    f.flush()  # すぐに書き込みを反映
                    
                    # コンソールに現在の重量を表示
                    print(f"Time: {current_time:.2f}s, Weight: {weight:.2f}g")
                    
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
            
        # グラフを更新
        self.line.set_data(self.times, self.weights)
        
        # X軸の範囲を調整
        self.ax.set_xlim(0, max(self.times) + 5)
        
        # Y軸の範囲を調整
        min_weight = min(self.weights) - 10 if len(self.weights) > 0 else -10
        max_weight = max(self.weights) + 10 if len(self.weights) > 0 else 500
        self.ax.set_ylim(min_weight, max_weight)
        
        # グラフのタイトルを更新
        avg_weight = np.mean(self.weights) if len(self.weights) > 0 else 0
        self.ax.set_title(f'Weight Measurement: Avg={avg_weight:.1f}g')
        
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
