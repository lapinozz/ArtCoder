import sys
import time
import asyncio
import threading
import traceback

from appUtils import killThread

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

class Flag:
	def __init__(self, val = True):
		self.value = val

	def set(self, val):
		self.value = val

	def get(self):
		return self.value

WAITING  = 0
RUNNING  = 1
DONE 	 = 2
CRASHED  = 3
CANCELED = 4

class Training:
	def __init__(self, trainer, session):
		self.lock = threading.Lock()
		self.trainer = trainer
		self.session = session
		self.state = WAITING
		self.position = 0

	def finish(self, newState = DONE):
		if self.state == RUNNING:
			killThread(self.trainer.thread)
		
		self.state = newState

	def isWaiting(self):
		return self.state == WAITING

	def isRunning(self):
		return self.state == RUNNING

	def isDone(self):
		return self.state == DONE

	def isCrashed(self):
		return self.state == CRASHED

	def isCanceled(self):
		return self.state == CANCELED

	def isFinished(self):
		return self.isDone() or self.isCrashed() or self.isCanceled()

	async def train(self):
		self.state = RUNNING
		try:
			await self.session.train()
			self.state = DONE
		except:
			self.state = CRASHED
			traceback.print_exc()
			raise

class Trainer:
	def __init__(self):
		self.queue = []
		self.lock = threading.Lock()

	def enqueue(self, training):
		with self.lock:
			self.queue.append(training)

	def updateQueue(self):
		while True:
			time.sleep(0.25)
			with self.lock:
				i = 0
				while i < len(self.queue):
					if self.queue[i].isFinished():
						del self.queue[i]
					else:
						self.queue[i].position = i
						i += 1

	def start(self):
		def _run():
			self.loop = asyncio.new_event_loop()
			self.loop.run_until_complete(self.run())

		self.thread = threading.Thread(target=_run, args=())
		self.thread.daemon = True
		self.thread.start()

		self.thread2 = threading.Thread(target=self.updateQueue, args=())
		self.thread2.daemon = True
		self.thread2.start()

	async def run(self):
		while True:
			try:
				while True:
					with self.lock:
						if len(self.queue) > 0:
							break

					time.sleep(0.25)

				training = None
				with self.lock:
					training = self.queue.pop(0)

				if not training or not training.isWaiting():
					continue

				await training.train()
			except:
				traceback.print_exc()

	async def queueTraining(self, session):

		training = Training(self, session)
		self.enqueue(training)	

		try:	
			while not training.isFinished():

				data = {'position': training.position, 'length': len(self.queue)}
				if training.isWaiting():
					data['status'] = 'waiting'
				elif training.isRunning():
					data['status'] = 'running'

				await session.sendMessage('queue', {'queue': data})
			
				time.sleep(1)
		except:
			training.finish(CANCELED)
			raise
		finally:
			data = {}

			if training.isDone():
				data['status'] = 'done'
			elif training.isCrashed():
				data['status'] = 'crashed'
			elif training.isCanceled():
				data['status'] = 'canceled'

			await session.sendMessage('queue', {'queue': data})




