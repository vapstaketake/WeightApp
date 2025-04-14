#!/usr/bin/env python3
from hx711lib import HX711
import time

def main():
    # HX711インスタンスの作成
    scale = HX711()
    
    try:
        # センサーの読み取りを開始
        print("重量センサーの初期化中...")
        scale.start()
        
        # 初期化のための少し待機
        time.sleep(2)
        
        # ゼロ点調整
        print("ゼロ点調整を行います...")
        scale.tare()
        time.sleep(1)
        
        print("重量測定を開始します。Ctrl+Cで終了。")
        print("-" * 50)
        
        # 連続的に重量を表示
        while True:
            weight = scale.get_weight()
            print(f"現在の重量: {weight:.2f} g")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n測定を終了します。")
    finally:
        # センサーの読み取りを停止
        scale.stop()

if __name__ == "__main__":
    main()