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
cyclic = math.sin(phase * 2 * math.pi) * variation * 0.5
random_var = random.uniform(-variation * 0.2, variation * 0.2)

reading = base_weight + cyclic + random_var
print(reading)
