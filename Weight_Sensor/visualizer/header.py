#Windows環境かどうかを判定
import os
import sys
from hx711_wrapper import HX711

is_windows = sys.platform.startswith('win')
if is_windows:
    # Windows環境の場合
    EXECUTABLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_reader.exe")
else:
    EXECUTABLE_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_reader")

for i in range(10):
    # 生の読み取り値を取得
    weight = HX711.get_raw_reading(EXECUTABLE_PATH)
    if weight is not None:
        print(f"Raw weight reading: {weight} g")
    else:
        print("Failed to get weight reading.")
