import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

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
        
        try:
            while True:
                data = [random.randint(0, 100) for _ in range(4096)]
                message = f"data: {data}\n\n"
                self.wfile.write(message.encode('utf-8'))
                self.wfile.flush()  # Ensure the data is sent immediately
                time.sleep(1)
        except BrokenPipeError:
            pass
        finally:
            print(f"Client disconnected: {self.client_address}")
            clients.remove(self)

def run(server_class=HTTPServer, handler_class=SSEHandler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'SSE server running on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
