import base64
import numpy as np
from PIL import Image
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import time
from math import sin, pi, sqrt
import math
import struct
output_file_path = 'output_image.h'

def rgb888_to_rgb565(r, g, b):
    r = (r >> 3) & 0x1F
    g = (g >> 2) & 0x3F
    b = (b >> 3) & 0x1F
    return (r << 11) | (g << 5) | b

def image_to_rgb565(image_path):
    image = Image.open(image_path).resize((64, 64))
    image = image.convert("RGB")
    width, height = image.size
    rgb565_data = np.zeros((height, width), dtype=np.uint16)
    
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            rgb565_data[y, x] = rgb888_to_rgb565(r, g, b)
    return rgb565_data.tobytes()

def image_to_rgb565_array(image_path):
    """Convert an image to a list of RGB565 values."""
    with Image.open(image_path) as img:
        img = img.convert('RGB')  # Ensure image is in RGB mode
        width, height = img.size
        pixel_data = []

        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                rgb565 = rgb888_to_rgb565(r, g, b)
                pixel_data.append(rgb565)
        
    return pixel_data, width, height
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

clients = []
class SSEHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global clients
        clients.append(self)
        self.send_response(200)
        self.send_header('Content-type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        print(f"Client connected: {self.client_address}")
        self.t =  0
        # Path to the image file
        #image_path = '/home/qthi/Documents/quyth/Image/64x64/img2.png'
        #rgb565_data = image_to_rgb565_array(image_path)
        #base64_rgb565_data = base64.b64encode(rgb565_data).decode('utf-8')
        try:
            while True:
                rgb565_data = generate_colorful_plasma_rgb565(64,64,self.t)
                message = f"d: {rgb565_data}\n\n"
                self.wfile.write(message.encode('utf-8'))
                self.wfile.flush()  # Ensure the data is sent immediately
                self.t += 1
                #time.sleep(0.05)
                # Optionally add a delay before starting again
                

        except BrokenPipeError:
            pass
        finally:
            print(f"Client disconnected: {self.client_address}")

def run(server_class=HTTPServer, handler_class=SSEHandler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'SSE server running on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()