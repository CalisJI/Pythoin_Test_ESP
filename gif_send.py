from PIL import Image, ImageSequence
import socket
import struct
import time

def rgb888_to_rgb565(r, g, b):
    """Chuyển đổi từ RGB888 sang RGB565"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

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

def send_frame(frame_data, udp_ip, udp_port):
    """Gửi khung hình qua UDP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_size = 1460  # Kích thước gói tối đa để tránh tràn UDP
    num_packets = (len(frame_data) * 2 + packet_size - 1) // packet_size

    for i in range(num_packets):
        start_index = i * packet_size // 2
        end_index = min((i + 1) * packet_size // 2, len(frame_data))
        packet = struct.pack('!' + 'H' * (end_index - start_index), *frame_data[start_index:end_index])
        sock.sendto(packet, (udp_ip, udp_port))

def main():
    gif_path = '/home/qthi/Documents/quyth/Image/64x64/gif1.gif'
    udp_ip = '192.168.1.192'  # IP của ESP32
    udp_port = 5000

    frames = load_gif_to_rgb565(gif_path)
    while True:
        for frame_data, _, _ in frames:
            send_frame(frame_data, udp_ip, udp_port)
            time.sleep(1/8)  # Điều chỉnh để đạt được 15 fps

if __name__ == "__main__":
    main()
