import time
import random
import numpy as np
from datetime import datetime

class WeightDataGenerator:
    """
    重量センサーからのデータを模擬的に生成するクラス
    """
    def __init__(self, initial_weight=0, noise_level=0.1, drift_rate=0.01):
        """
        初期化
        
        Args:
            initial_weight (float): 初期重量 (g)
            noise_level (float): ノイズレベル
            drift_rate (float): 長期的な変動率
        """
        self.current_weight = initial_weight
        self.noise_level = noise_level
        self.drift_rate = drift_rate
        self.start_time = datetime.now()
    
    def get_weight_data(self):
        """
        現在の重量データを取得
        
        Returns:
            tuple: (timestamp, weight)
        """
        # 時間経過に応じた緩やかな変動
        elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
        drift = np.sin(elapsed_seconds * self.drift_rate) * 2
        
        # ランダムノイズを追加
        noise = random.gauss(0, self.noise_level)
        
        # 重量の計算
        weight = self.current_weight + drift + noise
        timestamp = datetime.now()
        
        return timestamp, max(0, weight)
    
    def add_weight(self, amount):
        """
        重量を追加
        
        Args:
            amount (float): 追加する重量 (g)
        """
        self.current_weight += amount
