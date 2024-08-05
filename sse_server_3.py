import socket
import struct
import time
from math import sin, sqrt

def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

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

def send_plasma_data(host, port, width, height):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  # Listen for one connection at a time

    while True:
        print('Waiting for a connection')
        connection, client_address = server_socket.accept()
        print(f'Connection from {client_address}')
        t = 0
        try:
            while t < 10:
                rgb565_data = generate_colorful_plasma_rgb565(width, height, t)
                data_bytes = bytearray()
                for value in rgb565_data:
                    data_bytes.append((value >> 8) & 0xFF)
                    data_bytes.append(value & 0xFF)
                
                data_len = struct.pack('!I', len(data_bytes))
                
                connection.sendall(data_len)
                
                # Send data in chunks
                chunk_size = 4096
                for i in range(0, len(data_bytes), chunk_size):
                    connection.sendall(data_bytes[i:i + chunk_size])
                
                print(f'Sent plasma data for t={t:.2f}')
                
                t += 0.1
                time.sleep(0.1)
        except Exception as e:
            print(f'Error: {e}')
        finally:
            connection.close()

# Usage example
width, height = 64, 64
send_plasma_data('0.0.0.0', 10000, width, height)
