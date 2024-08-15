import asyncio
import websockets

async def receive_data():
    uri = "ws://localhost:8765"  # Thay đổi địa chỉ IP và cổng nếu cần
    async with websockets.serve(handle_message, "localhost", 8765):
        print("WebSocket server đang chạy tại ws://localhost:8765")
        await asyncio.Future()  # Chạy server mãi mãi

async def handle_message(websocket, path):
    async for message in websocket:
        # In dữ liệu nhận được
        print(f"Nhận dữ liệu: {message}")
        # Nếu dữ liệu là nhị phân (bytes), bạn có thể xử lý nó theo cách bạn muốn
        if isinstance(message, bytes):
            print(f"Dữ liệu nhị phân nhận được: {len(message)} bytes")

# Chạy server WebSocket
asyncio.run(receive_data())
