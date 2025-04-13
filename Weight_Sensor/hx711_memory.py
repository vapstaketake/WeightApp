import mmap
import ctypes
import time
import posix_ipc
import subprocess
import os
import sys


is_windows = sys.platform.startswith('win')
if is_windows:
    # Windows環境の場合
    EXECUTABLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_reader.exe")
else:
    EXECUTABLE_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)), "weight_reader")

SHM_NAME = "/weight_shm"

class SensorData(ctypes.Structure):
    _fields_ = [
        ("weight", ctypes.c_double),
        ("ready", ctypes.c_bool)
    ]

process = subprocess.Popen([EXECUTABLE_PATH])

memory=posix_ipc.SharedMemory(SHM_NAME)
map_file=mmap.mmap(memory.fd,ctypes.sizeof(SensorData),mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
try:
    while True:
        map_file.seek(0)
        sensor_data = SensorData.from_buffer(map_file)
        if sensor_data.ready:
            weight = sensor_data.weight
            print(f"Weight: {weight} g")
            sensor_data.ready=False
            map_file.seek(0)
            map_file.write(bytearray(sensor_data))
        else:
            print("Waiting for sensor data...")
            print(sensor_data.weight)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("closed")

finally:
    map_file.close()
    memory.close()
    process.terminate()