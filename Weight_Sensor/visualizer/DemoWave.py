import numpy as np
#アニメーションテスト用に標準のサイン波を生成
frequency = 5  # 周波数（Hz）
sampling_rate = 1000  # サンプリングレート（Hz）
duration = 1.0  # 秒
amplitude = 1.0  # 振幅
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
sin_wave = amplitude * np.sin(2 * np.pi * frequency * t) + amplitude