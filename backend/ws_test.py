import asyncio
import websockets

async def test_ws():
    try:
        print("Connecting to ws://localhost:8000/ws/audio...")
        async with websockets.connect('ws://localhost:8000/ws/audio') as websocket:
            print("Connected successfully!")
            await websocket.send("test")
            print("Message sent.")
            res = await websocket.recv()
            print(f"Received: {res}")
    except Exception as e:
        print(f"Failed: {e}")

asyncio.run(test_ws())
