import asyncio
import websockets
import numpy as np
import struct
from PIL import Image, ImageSequence
import numpy as np
import cv2
import yt_dlp as youtube_dl
from pytube import YouTube
def rgb888_to_rgb565(r, g, b):
    """Chuyển đổi từ RGB888 sang RGB565"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
def create_test_pattern():
    """Tạo mẫu màu đơn giản để kiểm tra"""
    width, height = 128, 128
    frame_data = bytearray()

    for y in range(height):
        for x in range(width):
            # Tạo màu đơn giản: Red, Green, Blue, and White stripes
            r, b, g = 0, 255, 0  # Red
            rgb565 = rgb888_to_rgb565(r, g, b)
            frame_data.extend(struct.pack('!' + 'H', rgb565))

    return frame_data

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
        frame_data = bytearray()
        for y in range(height):
            for x in range(width):
                r, g, b = frame[y, x]
                rgb565 = rgb888_to_rgb565(r, g, b)
                frame_data.append(rgb565)
        frame_data.extend(struct.pack('!' + 'H', rgb565))
    cap.release()
    return frames

def load_image_to_rgb565(file_path):
    """Tải tệp ảnh và chuyển đổi từng pixel sang định dạng RGB565"""
    img = Image.open(file_path)
    img = img.convert('RGB')  # Đảm bảo ảnh ở định dạng RGB

    width, height = img.size
    frame_data = bytearray()

    for y in range(height):
        for x in range(width):
            r, b, g = img.getpixel((x, y))
            rgb565 = rgb888_to_rgb565(r, g, b)
            frame_data.extend(struct.pack('!' + 'H', rgb565))  # 'H' là định dạng cho uint16_t

    return frame_data
def load_gif_to_rgb565(file_path):
    """Tải tệp GIF và chuyển đổi từng khung hình sang định dạng RGB565"""
    gif = Image.open(file_path)
    frames = []

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert('RGB')
        width, height = frame.size
        frame_data = bytearray()
        for y in range(height):
            for x in range(width):
                r, g, b = frame.getpixel((x, y))
                rgb565 = rgb888_to_rgb565(r, g, b)
                frame_data.extend(struct.pack('!' + 'H', rgb565))
        frames.append((frame_data, width, height))

    return frames

# Function to process and send frames
async def process_and_send_frames(stream_url, websocket_url):
    # Create a video capture object for the stream
    cap = cv2.VideoCapture(stream_url)
    async with websockets.connect(websocket_url) as websocket:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize frame to 128x128
            frame_resized = cv2.resize(frame, (128, 128))
            
            width, height = frame_resized.size
            frame_data = bytearray()

            for y in range(height):
                for x in range(width):
                    r, b, g = frame_resized.getpixel((x, y))
                    
                    rgb565 = rgb888_to_rgb565(r, g, b)
                    frame_data.extend(struct.pack('!' + 'H', rgb565))  # 'H' là định dạng cho uint16_t
                
            chunk_size = 1024  # Kích thước mỗi phần dữ liệu
            for i in range(0, len(frame_data), chunk_size):
                chunk = frame_data[i:i + chunk_size]
                await websocket.send(chunk)
            await asyncio.sleep(0.05)  # Giữ tốc độ gửi dữ liệu
    cap.release()
# Function to download video
def download_video(youtube_url, output_path='video.mp4'):
    yt = YouTube(youtube_url)
    video = yt.streams.filter(res="720p").first()
    video.download(output_path=output_path)
# Example usage
stream_url = 'https://www.youtube.com/watch?v=kQHUeF4gRQU'  # This is just an example URL; actual live streaming URL needed

# Ví dụ sử dụng
# file_path = '/home/qthi/Documents/quyth/Image/128x128/img1.png'
file_path = '/home/qthi/Documents/quyth/Image/128x128/gif2.gif'
video_path = 'video.mp4'
frame_data = load_image_to_rgb565(file_path)
uri = "ws://192.168.2.243:81"
async def send_image_data(file_path):
      # Thay <ESP32_IP> bằng địa chỉ IP của ESP32
    # uri = "ws://localhost:8765"  # Thay <ESP32_IP> bằng địa chỉ IP của ESP32
    frames = load_gif_to_rgb565(file_path)
    async with websockets.connect(uri) as websocket:
        while True:
            #frame_data = load_image_to_rgb565(file_path)
            # frame_data = create_test_pattern()
            for frame_data, _, _ in frames:
                # Chia nhỏ dữ liệu nếu cần (tùy thuộc vào kích thước của dữ liệu và giới hạn của WebSocket)
                chunk_size = 1024  # Kích thước mỗi phần dữ liệu
                for i in range(0, len(frame_data), chunk_size):
                    chunk = frame_data[i:i + chunk_size]
                    await websocket.send(chunk)
                await asyncio.sleep(0.01)  # Giữ tốc độ gửi dữ liệu

asyncio.get_event_loop().run_until_complete(send_image_data(file_path))
# download_video('https://www.youtube.com/watch?v=kQHUeF4gRQU')
# asyncio.get_event_loop().run_until_complete(process_and_send_frames(video_path,uri))
