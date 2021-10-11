import asyncio
import http.server
import socketserver
from threading import Thread

import websockets

PORT = 8056
DIRECTORY = "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, directory=DIRECTORY, **kwargs)

def create_server():
	with socketserver.TCPServer(("", PORT), Handler) as httpd:
		print("serving at port", PORT)
		httpd.serve_forever()

thread = Thread(target = create_server, args = ())
thread.daemon = True
thread.start()

print("Server has started. Continuing..")

async def onMessage(message):
	print(message)

firstConnection = True
async def onConnection(websocket, path):
	global firstConnection
	if firstConnection:
		firstConnection = False
		await websocket.send("reload")
	
	await websocket.send("rwar")

	async for message in websocket:
		onMessage(message)

start_server = websockets.serve(onConnection, 'localhost', PORT + 1)

asyncio.get_event_loop().run_until_complete(start_server)

print("Websockets server has started. Continuing..")

try:
	asyncio.get_event_loop().run_forever()
except KeyboardInterrupt as e:
	quit()

#while True:
	#print("running")

#thread.exit()
#thread.join()