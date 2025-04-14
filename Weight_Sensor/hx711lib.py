from hx711_memory import get_weight_data
import threading
import time

class HX711:
    def __init__(self):
        self.reference_weight = None
        self.current_weight = 0
        self.is_running = False
        self._thread = None
        self._lock = threading.Lock()
    
    def start(self):
        """センサーの読み取りを開始する"""
        if self.is_running:
            return
            
        self.is_running = True
        self._thread = threading.Thread(target=self._read_weight_loop)
        self._thread.daemon = True
        self._thread.start()
        
    def stop(self):
        """センサーの読み取りを停止する"""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            
    def _read_weight_loop(self):
        """バックグラウンドでセンサーから読み取りを行うスレッド関数"""
        def weight_callback(weight):
            with self._lock:
                # 初回の計測は基準値として設定
                if self.reference_weight is None:
                    self.reference_weight = weight
                    self.current_weight = 0
                else:
                    # 2回目以降は差分を計算
                    self.current_weight = weight - self.reference_weight
        
        # センサーからの読み取り開始（コールバック関数を渡す）
        get_weight_data(callback=weight_callback)
    
    def get_weight(self):
        """現在の重量を取得（基準値との差分）"""
        with self._lock:
            return self.current_weight
    
    def tare(self):
        """現在の重量を0にリセット（基準値を再設定）"""
        with self._lock:
            self.reference_weight = None