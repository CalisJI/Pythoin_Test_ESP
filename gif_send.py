from PIL import Image, ImageSequence
import socket
import struct
import time
import cv2
import serial
import struct
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def rgb888_to_rgb565(r, g, b):
    """Chuyển đổi từ RGB888 sang RGB565"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
def load_image_to_rgb565(file_path):
    """Tải tệp ảnh và chuyển đổi từng pixel sang định dạng RGB565"""
    img = Image.open(file_path)
    img = img.convert('RGB')  # Đảm bảo ảnh ở định dạng RGB

    width, height = img.size
    frame_data = []

    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            rgb565 = rgb888_to_rgb565(r, g, b)
            frame_data.append(rgb565)
    print(frame_data)
    return frame_data
def load_gif_to_rgb565(file_path):
    """Tải tệp GIF và chuyển đổi từng khung hình sang định dạng RGB565"""
    gif = Image.open(file_path)
    frames = []

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert('RGB')
        width, height = frame.size
        frame_data = []
        for y in range(height):
            for x in range(width):
                r, g, b = frame.getpixel((x, y))
                rgb565 = rgb888_to_rgb565(r, g, b)
                frame_data.append(rgb565)
        frames.append((frame_data, width, height))

    return frames
def load_video_to_rgb565(file_path):
    """Tải video và chuyển đổi từng khung hình sang định dạng RGB565"""
    cap = cv2.VideoCapture(file_path)
    frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]
        frame_data = []
        for y in range(height):
            for x in range(width):
                r, g, b = frame[y, x]
                rgb565 = rgb888_to_rgb565(r, g, b)
                frame_data.append(rgb565)
        frames.append((frame_data, width, height))
    print(frames)
    cap.release()
    return frames
def send_frame(frame_data, udp_ip, udp_port):
    """Gửi khung hình qua UDP"""
    
    packet_size = 1460 # Kích thước gói tối đa để tránh tràn UDP
    num_packets = (len(frame_data) * 2 + packet_size - 1) // packet_size
    for i in range(num_packets):
        start_index = i * packet_size // 2
        end_index = min((i + 1) * packet_size // 2, len(frame_data))
        packet = struct.pack('!' + 'H' * (end_index - start_index), *frame_data[start_index:end_index])
        sock.sendto(packet, (udp_ip, udp_port))
        # time.sleep(0.1)

def send_data_via_serial(port, baudrate, data):
    with serial.Serial(port, baudrate, timeout=1) as ser:
        # Gửi mảng dữ liệu
        for value in data:
            # Gửi giá trị RGB565 (2 byte)
            ser.write(struct.pack('<H', value))
def main():
    media_path = '/home/qthi/Documents/quyth/Image/128x128/gif2.gif'
    frames = load_gif_to_rgb565(media_path)
    # media_path = '/home/qthi/Documents/quyth/Image/128x128/img2.jpg'
    
    # frames = load_image_to_rgb565(media_path)
    # media_path = '/home/qthi/Documents/quyth/Image/64x64/vid.mp4'
    # frames = load_video_to_rgb565(media_path)
    
    #send_data_via_serial("/dev/ttyUSB0", 115200*2, frames)
    
    udp_ip = '192.168.2.243'  # IP của ESP32
    udp_port = 5000 
    
    # #Sending Image
    # send_frame(frames, udp_ip, udp_port)


    # Sending gif
    while True:
        for frame_data, _, _ in frames:
            # Gửi số lượng khung hình trước
            
            send_frame(frame_data, udp_ip, udp_port)
            time.sleep(1/10)  # Điều chỉnh để đạt được 15 fps
    
    # Sending video

    # dem = 1
    # while dem>0:
    #     num_frames = len(frames)
    #     num_frames_bytes = struct.pack('I', num_frames)
    #     sock.sendto(num_frames_bytes, (udp_ip, udp_port))
    #     time.sleep(1)
    #     for frame_data, _, _ in frames:
    #         # Gửi số lượng khung hình trước
    #         send_frame(frame_data, udp_ip, udp_port)
    #         time.sleep(1/5)  # Điều chỉnh để đạt được 15 fps
    #     dem-=1
if __name__ == "__main__":
    main()
