from data_generator import WeightDataGenerator
from weight_visualizer import WeightVisualizer
from hx711_wrapper import HX711
from header import EXECUTABLE_PATH

def main():
    # テスト用のデータジェネレーターを初期化 (初期重量: 0g)
    #data_generator = WeightDataGenerator(initial_weight=0, noise_level=0.2)
    current_data=HX711.get_raw_reading(EXECUTABLE_PATH)
    # 可視化ツールの初期化と実行
    visualizer = WeightVisualizer(current_data, window_size=200, update_interval=50)
    visualizer.start()

if __name__ == "__main__":
    main()
