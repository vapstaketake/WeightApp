"""
重量センサー キャリブレーションユーティリティ

このスクリプトは、HX711重量センサーのキャリブレーションを行い、
結果を設定ファイルに保存します。
"""
import os
import sys
import time
import subprocess
import json
import statistics
from datetime import datetime

# 設定
EXECUTABLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_reader")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_config.json")
CALIBRATION_SAMPLES = 20  # キャリブレーションに使用するサンプル数
SAMPLE_INTERVAL = 0.1     # サンプリング間隔（秒）

# Windowsでの実行かどうかを確認
is_windows = sys.platform.startswith('win')
if is_windows:
    MOCK_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_weight_reader.py")
    print("Windows環境を検出しました。モックデータを使用します。")

class CalibrationUtility:
    def __init__(self):
        # 設定の読み込み
        self.config = self.load_config()
        
        # 環境に応じた実行準備
        self.prepare_executable()
        
        print("HX711重量センサー キャリブレーションユーティリティ")
        print("=" * 50)

    def load_config(self):
        """設定ファイルの読み込み（存在しない場合はデフォルト値を返す）"""
        default_config = {
            "initial_offset": 8156931,
            "factor": -300.0 / 113318.0,
            "last_calibration": "",
            "calibration_weights": []
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            return default_config
        except Exception as e:
            print(f"設定ファイルの読み込みに失敗しました: {e}")
            return default_config

    def save_config(self):
        """設定の保存"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"設定を保存しました: {CONFIG_FILE}")
        except Exception as e:
            print(f"設定の保存に失敗しました: {e}")

    def prepare_executable(self):
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
variation = 10000  # キャリブレーション用に変動を少なくする

# ランダム変動
random_var = random.uniform(-variation, variation)
reading = base_weight + random_var
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

    def get_reading(self):
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

    def measure_zero_point(self):
        """ゼロポイント（何も載せていない状態）の測定"""
        print("\nゼロポイントのキャリブレーションを開始します")
        print("プラットフォームから全ての重りを取り除いてください")
        input("準備ができたらEnterキーを押してください...")
        
        print(f"{CALIBRATION_SAMPLES}回の測定を行います...")
        
        # 複数回測定
        readings = []
        for i in range(CALIBRATION_SAMPLES):
            print(f"測定 {i+1}/{CALIBRATION_SAMPLES}...", end="", flush=True)
            reading = self.get_reading()
            if reading is not None:
                readings.append(reading)
                print(f" 読み取り値: {reading:.2f}")
            else:
                print(" エラー")
            time.sleep(SAMPLE_INTERVAL)
        
        if not readings:
            print("エラー: 有効な測定値がありません")
            return None
            
        # 統計情報の計算
        mean_value = statistics.mean(readings)
        if len(readings) > 1:
            stddev = statistics.stdev(readings)
            print(f"\n測定結果: 平均={mean_value:.2f}, 標準偏差={stddev:.2f}")
        else:
            print(f"\n測定結果: 値={mean_value:.2f}")
        
        # 設定に保存
        self.config["initial_offset"] = mean_value
        self.config["last_calibration"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return mean_value

    def measure_known_weight(self):
        """既知の重さを使ったキャリブレーション"""
        print("\n既知の重さを使ったキャリブレーションを行います")
        
        try:
            weight = float(input("使用する重りの重さをグラムで入力してください: "))
        except ValueError:
            print("有効な数値を入力してください")
            return
        
        print(f"{weight}グラムの重りをプラットフォームに載せてください")
        input("準備ができたらEnterキーを押してください...")
        
        print(f"{CALIBRATION_SAMPLES}回の測定を行います...")
        
        # 複数回測定
        readings = []
        for i in range(CALIBRATION_SAMPLES):
            print(f"測定 {i+1}/{CALIBRATION_SAMPLES}...", end="", flush=True)
            reading = self.get_reading()
            if reading is not None:
                readings.append(reading)
                print(f" 読み取り値: {reading:.2f}")
            else:
                print(" エラー")
            time.sleep(SAMPLE_INTERVAL)
        
        if not readings:
            print("エラー: 有効な測定値がありません")
            return
            
        # 統計情報の計算
        mean_value = statistics.mean(readings)
        
        # 係数の計算
        raw_diff = self.config["initial_offset"] - mean_value
        if raw_diff != 0:
            factor = weight / raw_diff
            
            # 係数の符号を保持（極性反転の考慮）
            if self.config["factor"] < 0:
                factor = -abs(factor)
            else:
                factor = abs(factor)
                
            print(f"\n計算された係数: {factor:.8f}")
            self.config["factor"] = factor
            
            # キャリブレーション履歴に追加
            self.config["calibration_weights"].append({
                "weight": weight,
                "raw_value": mean_value,
                "factor": factor,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # 最大5つまで保持
            if len(self.config["calibration_weights"]) > 5:
                self.config["calibration_weights"] = self.config["calibration_weights"][-5:]
        else:
            print("\nエラー: ゼロポイントとの差分がありません。正しく重りが載っていますか？")

    def run(self):
        """キャリブレーションプロセスを実行"""
        while True:
            print("\n=== キャリブレーションメニュー ===")
            print("1. ゼロポイントのキャリブレーション")
            print("2. 既知の重さでのキャリブレーション")
            print("3. 現在の設定を表示")
            print("4. 設定を保存して終了")
            print("0. 保存せずに終了")
            
            choice = input("\n選択してください: ")
            
            if choice == "1":
                self.measure_zero_point()
            elif choice == "2":
                self.measure_known_weight()
            elif choice == "3":
                print("\n=== 現在の設定 ===")
                print(f"初期オフセット: {self.config['initial_offset']:.2f}")
                print(f"係数: {self.config['factor']:.8f}")
                print(f"最終キャリブレーション: {self.config['last_calibration']}")
                
                if self.config["calibration_weights"]:
                    print("\nキャリブレーション履歴:")
                    for i, cal in enumerate(self.config["calibration_weights"]):
                        print(f"{i+1}. {cal['date']} - {cal['weight']}g (係数: {cal['factor']:.8f})")
            elif choice == "4":
                self.save_config()
                break
            elif choice == "0":
                print("変更を保存せずに終了します")
                break
            else:
                print("無効な選択です")


if __name__ == "__main__":
    calibrator = CalibrationUtility()
    calibrator.run()
