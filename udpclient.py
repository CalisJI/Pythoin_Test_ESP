import numpy as np
from PIL import Image
import socket
import time
from math import sin, pi, sqrt
# ESP32 IP và PORT
UDP_IP = "192.168.1.192"  # Thay đổi thành IP của ESP32
UDP_PORT = 5000  # Thay đổi thành port bạn muốn sử dụng
time_step = 0
# Tạo socket UDP
width = 64
height = 64
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MAX_UDP_SIZE = 1450  # Thay đổi nếu cần
# Hàm chuyển đổi từ RGB888 sang RGB565
def rgb888_to_rgb565(r, g, b):
    r5 = (r * 31) // 255
    g6 = (g * 63) // 255
    b5 = (b * 31) // 255
    return (r5 << 11) | (g6 << 5) | b5
def generate_colorful_plasma_rgb565(width, height, t):
    rgb565_data = []
    
    for y in range(height):
        for x in range(width):
            value1 = 128.0 + (128.0 * sin(x / 16.0 + t))
            value2 = 128.0 + (128.0 * sin(y / 8.0 + t))
            value3 = 128.0 + (128.0 * sin((x + y) / 16.0 + t))
            value4 = 128.0 + (128.0 * sin(sqrt(x * x + y * y) / 8.0 + t))
            
            r = int((value1 + value2) / 2) % 256
            g = int((value2 + value3) / 2) % 256
            b = int((value3 + value4) / 2) % 256
            
            rgb565_data.append(rgb888_to_rgb565(r, g, b))
    
    return rgb565_data

def create_plasma_frame(time_step):
    # Tạo mảng RGB cho hình ảnh
    image_array = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            value1 = 128.0 + (128.0 * sin(x / 16.0 + time_step))
            value2 = 128.0 + (128.0 * sin(y / 8.0 + time_step))
            value3 = 128.0 + (128.0 * sin((x + y) / 16.0 + time_step))
            value4 = 128.0 + (128.0 * sin(sqrt(x * x + y * y) / 8.0 + time_step))
            # Tạo giá trị cho plasma
            r = int((value1 + value2) / 2) % 256
            g = int((value2 + value3) / 2) % 256
            b = int((value3 + value4) / 2) % 256

            # Gán giá trị màu vào mảng hình ảnh
            image_array[y, x] = [int(r), int(g), int(b)]

    return image_array
while True:
    start_time = time.time()
    image = Image.open("/home/qthi/Documents/quyth/Image/32x32/img1.png").resize((width, height))

    # #Đọc ảnh từ file và resize về 64x64
    # if time_step%2 ==1:
    #     image = Image.open("/home/qthi/Documents/quyth/Image/64x64/img1.png").resize((64, 64))
    # else:
    #     image = Image.open("/home/qthi/Documents/quyth/Image/64x64/img2.png").resize((64, 64))

    image_data = np.array(image)
    time_step +=0.5
    # Anh plassma
    #image_data = create_plasma_frame(time_step)
    # Chuẩn bị dữ liệu để truyền
    data = bytearray()

    for y in range(height):
        for x in range(width):
            r, g, b = image_data[y, x][:3]  # Lấy 3 kênh màu (bỏ kênh alpha nếu có)
            rgb565_value = rgb888_to_rgb565(r, g, b)
            data.extend([rgb565_value >> 8, rgb565_value & 0xFF])
    
    # # Truyền dữ liệu qua UDP
    # sock.sendto(data, (UDP_IP, UDP_PORT))
    # print("Sent Data")
    # # Tính thời gian đã trôi qua
    elapsed_time = time.time() - start_time

    # # Đảm bảo tốc độ khung hình là 15fps (tương đương 66.67ms mỗi khung hình)
    # if elapsed_time < 1/15:
    #     time.sleep(1/15 - elapsed_time)
   # Chia nhỏ và gửi dữ liệu
    for i in range(0, len(data), MAX_UDP_SIZE):
        chunk = data[i:i + MAX_UDP_SIZE]
        sock.sendto(chunk, (UDP_IP, UDP_PORT))
        print(f"Sent chunk of size {len(chunk)}:{i}")
    if elapsed_time < 1/10:
        time.sleep(1/10 - elapsed_time)
    # time.sleep(0.05)