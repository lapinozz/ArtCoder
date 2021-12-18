import json
import asyncio
import http.server
import socketserver
from threading import Thread

import sass
import websockets

from session import Session 
from trainer import Trainer 

PORT = 8056
DIRECTORY = "./src/app/frontend"

sass.compile(dirname=(DIRECTORY + '/scss', DIRECTORY + '/css'), output_style='compressed')

socketserver.TCPServer.allow_reuse_address = True

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

trainer = Trainer()
trainer.start()

async def onConnection(websocket, path):

	session = Session(websocket, trainer)
	await session.start()

start_server = websockets.serve(onConnection, 'localhost', PORT + 1)

asyncio.get_event_loop().run_until_complete(start_server)

print("Websockets server has started. Continuing..")

try:
	asyncio.get_event_loop().run_forever()
except KeyboardInterrupt as e:
	quit()