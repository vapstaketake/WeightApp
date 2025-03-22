from data_generator import WeightDataGenerator
from weight_visualizer import WeightVisualizer

def main():
    # テスト用のデータジェネレーターを初期化 (初期重量: 0g)
    data_generator = WeightDataGenerator(initial_weight=0, noise_level=0.2)
    
    # 可視化ツールの初期化と実行
    visualizer = WeightVisualizer(data_generator, window_size=200, update_interval=50)
    visualizer.start()

if __name__ == "__main__":
    main()
