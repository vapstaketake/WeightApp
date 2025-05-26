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
    PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #.pngを参照する時のパス指定(~/weight/WeightApp/Weight_Sensorを取得)


