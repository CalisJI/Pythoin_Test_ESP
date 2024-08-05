import asyncio
import websockets
import struct

async def send_binary_data(uri):
    async with websockets.connect(uri) as websocket:
        width, height = 64, 64
        
        # Function to create binary data
        def create_binary_data():
            binary_data = bytearray()
            for y in range(height):
                for x in range(width):
                    r, g, b = (255, 0, 0)  # Example: Red color for all pixels
                    binary_data.extend(struct.pack('BBBBB', x, y, r, g, b))
            return binary_data
        
        # Function to send binary data
        async def send_data(data):
            await websocket.send(data)
            print("Binary data sent to the server")
            # response = await websocket.recv()
            # print(f"Received from server: {response}")

        # Initial sending of data
        binary_data = create_binary_data()
        await send_data(binary_data)
        
        # Loop to allow dynamic sending of additional data
        while True:
            user_input = input("Send more data? (yes/no): ").strip().lower()
            if user_input == "yes":
                binary_data = create_binary_data()
                await send_data(binary_data)
            elif user_input == "no":
                print("Exiting...")
                break
            else:
                print("Invalid input. Please type 'yes' or 'no'.")

# Replace <ESP8266_IP> with the actual IP address of your ESP8266
uri = "ws://192.168.1.189:80/ws"

# Run the client
asyncio.get_event_loop().run_until_complete(send_binary_data(uri))
