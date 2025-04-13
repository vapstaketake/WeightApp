import mmap
import ctypes
import time
import posix_ipc

SHM_NAME = "/weight_shm"

class SensorData(ctypes.Structure):
    _fields_ = [
        ("weight", ctypes.c_double),
        ("ready", ctypes.c_bool)
    ]

memory=posix_ipc.SharedMemory(SHM_NAME)
map_file=mmap.mmap(memory.fd,ctypes.sizeof(SensorData),mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
memory

sensor_data=SensorData.from_buffer(map_file)

while True:
    if sensor_data.ready:
        weight = sensor_data.weight
        print(f"Weight: {weight} g")
        sensor_data.ready=False
    time.sleep(0.1)