"""
シンプル版重量センサーグラフ表示プログラム - 自動キャリブレーション対応版
最初の5データを自動的に平均し、それをゼロ点として重量を計算します
"""
import sys
import os
import time
import subprocess
import random
from datetime import datetime

# 設定
OFFSET = 8156931
FACTOR = -300.0 / 113318.0  # 極性を反転（マイナス記号追加）
SAMPLE_INTERVAL = 0.2       # 秒
MAX_DURATION = 60           # 秒
CALIBRATION_SAMPLES = 5     # キャリブレーション用サンプル数
EXECUTABLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_reader")

# 出力ディレクトリの作成
OUTPUT_DIR = "weight_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Windowsでの実行かどうかを確認
is_windows = sys.platform.startswith('win')
if is_windows:
    MOCK_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_weight_reader.py")
    print("Windows環境を検出しました。モックデータを使用します。")

class SimpleWeightMonitor:
    def __init__(self):
        self.times = []
        self.weights = []
        self.raw_readings = []
        self.start_time = time.time()
        self.initial_reading = None  # 初期読み取り値（キャリブレーション後に設定）
        
        # 環境に応じた実行準備
        self._prepare_environment()
        
        # 出力ファイル名の設定
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.data_file = os.path.join(OUTPUT_DIR, f"weight_data_{timestamp}.csv")
        
        print("重量モニターを初期化しました")
        print(f"データは {self.data_file} に保存されます")

    def _prepare_environment(self):
        """環境に応じた実行ファイルの準備"""
        if is_windows:
            # Windows環境ではモックデータ生成スクリプトを作成
            self._create_mock_script()
        else:
            # Linux/Raspberry Pi環境では実行ファイルをコンパイル確認
            if not os.path.exists(EXECUTABLE_PATH):
                print("実行ファイルをコンパイルします...")
                try:
                    cpp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hx711.cpp")
                    subprocess.run(["g++", cpp_file, "-o", EXECUTABLE_PATH, "-lwiringPi"], check=True)
                    print("コンパイル成功")
                except subprocess.CalledProcessError:
                    print("コンパイルエラー。weight_reader.cppを作成します...")
                    self._create_weight_reader_file()
                    try:
                        subprocess.run(["g++", "weight_reader.cpp", "-o", EXECUTABLE_PATH, "-lwiringPi"], check=True)
                        print("コンパイル成功")
                    except subprocess.CalledProcessError as e:
                        print(f"コンパイル失敗: {e}")
                        sys.exit(1)

    def _create_mock_script(self):
        """Windowsテスト用のモックデータ生成スクリプト"""
        with open(MOCK_SCRIPT, "w") as f:
            f.write("""
import random
import time
import math

# 基本データ
base_weight = 8300000
variation = 50000
period = 20

# 時間に基づく変動
elapsed = time.time() % period
phase = elapsed / period
cyclic = math.sin(phase * 2 * math.pi) * variation * 0.5
random_var = random.uniform(-variation * 0.2, variation * 0.2)

reading = base_weight + cyclic + random_var
print(reading)
""")

    def _create_weight_reader_file(self):
        """重量センサー読み取り用のC++ソースファイル作成"""
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

    def get_raw_reading(self):
        """センサーからの生の読み取り値を取得"""
        try:
            if is_windows:
                # Windows環境ではPythonスクリプトで模擬データを生成
                result = subprocess.run([sys.executable, MOCK_SCRIPT], 
                                       capture_output=True, text=True, check=True)
            else:
                # Linux/RaspberryPi環境では実行ファイルを使用
                result = subprocess.run([EXECUTABLE_PATH], 
                                       capture_output=True, text=True, check=True)
                
            reading = float(result.stdout.strip())
            return reading
        except Exception as e:
            print(f"重量センサー読み取りエラー: {e}")
            return None

    def collect_data(self, duration=MAX_DURATION):
        """指定期間のデータ収集（自動キャリブレーション機能付き）"""
        print(f"データ収集を開始します（合計{duration}秒）...")
        print(f"最初の{CALIBRATION_SAMPLES}サンプルは自動キャリブレーションに使用します")
        print("Ctrl+Cで中断できます")
        
        # CSVファイルのヘッダー
        with open(self.data_file, "w") as f:
            f.write("Time,RawReading,RawDiff,Weight\n")
        
        try:
            # 自動キャリブレーションのためのデータ収集
            calibration_readings = []
            print("キャリブレーション中...")
            
            # キャリブレーション用のデータを収集
            while len(calibration_readings) < CALIBRATION_SAMPLES:
                reading = self.get_raw_reading()
                if reading is not None:
                    calibration_readings.append(reading)
                    print(f"キャリブレーション読み取り {len(calibration_readings)}/{CALIBRATION_SAMPLES}: {reading:.2f}")
                time.sleep(SAMPLE_INTERVAL)
            
            # 初期値を設定（キャリブレーションデータの平均）
            self.initial_reading = sum(calibration_readings) / len(calibration_readings)
            print(f"キャリブレーション完了: 初期値 = {self.initial_reading:.2f}")
            
            # メインのデータ収集を開始
            end_time = time.time() + duration
            self.start_time = time.time()  # キャリブレーション後に開始時間をリセット
            
            print("重量測定を開始します...")
            while time.time() < end_time:
                # 生の読み取り値を取得
                reading = self.get_raw_reading()
                if reading is not None:
                    current_time = time.time() - self.start_time
                    
                    # 初期値からの差分に基づいて重量を計算
                    raw_diff = self.initial_reading - reading
                    weight = raw_diff * abs(FACTOR)  # 符号は既にFACTORで考慮
                    
                    # データ保存
                    self.times.append(current_time)
                    self.raw_readings.append(reading)
                    self.weights.append(weight)
                    
                    # CSVに書き込み
                    with open(self.data_file, "a") as f:
                        f.write(f"{current_time:.2f},{reading:.2f},{raw_diff:.2f},{weight:.2f}\n")
                    
                    # コンソール表示
                    print(f"経過時間: {current_time:.2f}秒, 生値: {reading:.2f}, 差分: {raw_diff:.2f}, 重量: {weight:.2f}g")
                
                # 次のサンプルまで待機
                time.sleep(SAMPLE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nユーザーによりデータ収集が中断されました")
        
        print(f"収集完了: {len(self.times)}データポイント")
        return self.data_file

    def generate_text_graph(self):
        """簡易的なテキストベースのグラフ生成"""
        if not self.weights:
            print("データがありません")
            return
            
        # 統計情報
        min_weight = min(self.weights)
        max_weight = max(self.weights)
        avg_weight = sum(self.weights) / len(self.weights)
        
        print("\n===== 重量データの概要 =====")
        print(f"データ点数: {len(self.weights)}")
        print(f"最小重量: {min_weight:.2f}g")
        print(f"最大重量: {max_weight:.2f}g")
        print(f"平均重量: {avg_weight:.2f}g")
        print(f"初期センサー値: {self.initial_reading:.2f}")
        print("===========================\n")
        
        # 簡易グラフ (テキスト)
        WIDTH = 60  # グラフの横幅
        HEIGHT = 15  # グラフの高さ
        
        if max_weight == min_weight:
            # 重量が一定の場合
            print("[ 重量変化がありません ]")
            return
            
        # 簡易アスキーアートグラフの生成
        graph = []
        for _ in range(HEIGHT):
            graph.append([' ' for _ in range(WIDTH)])
            
        # データをグラフに配置
        for i, weight in enumerate(self.weights):
            if i >= WIDTH:
                break
                
            # Y座標を計算 (重量を高さに変換)
            y = int((weight - min_weight) / (max_weight - min_weight) * (HEIGHT-1))
            y = HEIGHT - 1 - y  # Y軸は上が0
            graph[y][i] = '*'
            
        # グラフを表示
        print("+" + "-" * WIDTH + "+")
        for row in graph:
            print("|" + "".join(row) + "|")
        print("+" + "-" * WIDTH + "+")
        print(f"最小: {min_weight:.1f}g" + " " * (WIDTH-20) + f"最大: {max_weight:.1f}g")
        
        print(f"\nデータの詳細はCSVファイルを確認してください: {self.data_file}")
        
        # matplotlibが使用可能なら、グラフも生成します
        try:
            self._try_generate_matplotlib_graph()
        except ImportError:
            print("matplotlibが見つからないため、グラフ画像は生成されませんでした")

    def _try_generate_matplotlib_graph(self):
        """matplotlibを使用してグラフ画像を生成（存在する場合のみ）"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        # 2つのサブプロットを作成（生値と重量）
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # 上のグラフ: 生のセンサー読み取り値
        ax1.plot(self.times, self.raw_readings, 'r-', label='Raw sensor value')
        if self.initial_reading is not None:
            ax1.axhline(y=self.initial_reading, color='g', linestyle='--', label=f'Initial: {self.initial_reading:.1f}')
        ax1.set_ylabel('Raw Reading')
        ax1.set_title('HX711 Sensor Reading')
        ax1.legend()
        ax1.grid(True)
        
        # 下のグラフ: 計算された重量
        ax2.plot(self.times, self.weights, 'b-')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Weight (g)')
        ax2.set_title('Calculated Weight')
        ax2.grid(True)
        
        # 統計情報を表示
        avg_weight = np.mean(self.weights)
        ax2.axhline(y=avg_weight, color='r', linestyle='--', label=f'Avg: {avg_weight:.1f}g')
        ax2.legend()
        
        plt.tight_layout()
        
        # 画像として保存
        graph_file = self.data_file.replace('.csv', '.png')
        plt.savefig(graph_file)
        print(f"グラフ画像を保存しました: {graph_file}")


def main():
    """メイン実行関数"""
    print("HX711重量センサーモニター - 自動キャリブレーション版")
    print("================================================")
    
    monitor = SimpleWeightMonitor()
    
    # データ収集（自動キャリブレーション機能付き）
    monitor.collect_data()
    
    # データ分析と結果表示
    monitor.generate_text_graph()
    
    print("\n完了しました!")


if __name__ == "__main__":
    main()
