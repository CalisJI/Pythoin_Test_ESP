from PIL import Image, ImageSequence
import socket
import struct
import time
import cv2

def rgb888_to_rgb565(r, g, b):
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

def send_frame_data(data, udp_ip, udp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_size = 1450  # Kích thước gói tối đa để tránh tràn UDP

    # Gửi số lượng khung hình trước
    num_frames = len(data)
    num_frames_bytes = struct.pack('I', num_frames)
    sock.sendto(num_frames_bytes, (udp_ip, udp_port))

    # Gửi dữ liệu khung hình
    for frame_data in data:
        num_packets = (len(frame_data) * 2 + packet_size - 1) // packet_size
        for i in range(num_packets):
            start_index = i * packet_size // 2
            end_index = min((i + 1) * packet_size // 2, len(frame_data))
            packet = struct.pack('!' + 'H' * (end_index - start_index), *frame_data[start_index:end_index])
            sock.sendto(packet, (udp_ip, udp_port))
    sock.close()

def main():
    num_frames = 10
    udp_ip = '192.168.1.243'  # IP của ESP32
    udp_port = 5000
    media_path = '/home/qthi/Documents/quyth/Image/64x64/gif1.gif'
    frames = load_gif_to_rgb565(media_path)
    send_frame_data(frames, udp_ip, udp_port)

if __name__ == "__main__":
    main()
