#include <iostream>
#include <wiringPi.h> //HX711のGPIO制御用,インストールが必要
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <string>
#include <chrono>
#include <thread>

//共有メモリの名前
const char* SHM_NAME = "/weight_shm";

//センサーデータの構造体
struct SensorData {
    double weight;
    bool ready;
};
//共有メモリ作成
static int create_shared_memory(const char* name, size_t size) {
    int fd = shm_open(name, O_CREAT | O_RDWR, 0666);
    if (fd == -1) {
        perror("shm_open");
        return -1;
    }
    if (ftruncate(fd, size) == -1) {
        perror("ftruncate");
        close(fd);
        return -1;
    }
    return fd;
}
//プロセスの仮想空間に割り当て
static void* map_shared_memory(int fd, size_t size) {
    void* ptr = mmap(nullptr, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return nullptr;
    }
    return ptr;
}
//センサーデータの書き込み
static void write_sensor_memory(SensorData* data,double value) {
    if(data->ready) {
    data->weight = value;
    data->ready = true;
    }

}
//センサデータの取得
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
    size_t SHM_SIZE = sizeof(SensorData);
    int shm_fd = create_shared_memory(SHM_NAME, SHM_SIZE);
    if (shm_fd == -1) return 1;

    void* ptr = map_shared_memory(shm_fd, SHM_SIZE);
    if (!ptr) return 1;

    SensorData* data = static_cast<SensorData*>(ptr);
    cout << "Shared memory created and mapped." << std::endl;
    while (true) {
        double current_value = readHx711Count();
        write_sensor_memory(data, current_value);
        while (data->ready) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    // 通常は実行されないが、クリーンアップを書くなら以下
    munmap(ptr, SHM_SIZE);
    close(shm_fd);
    shm_unlink(SHM_NAME);

    return 0;
}
