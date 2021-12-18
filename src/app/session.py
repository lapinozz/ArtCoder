import sys
import json
import base64
import ctypes
import asyncio
import threading
import traceback

from os import walk
from io import BytesIO
from pathlib import Path
from collections import OrderedDict

from PIL import Image, ImageEnhance, ImageFilter

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from appUtils import killThread

import utils
from segmentation import segmentData
from prepareContent import prepareContent
from qrcode import decodeQr, encodeQr
from combine import combine
from Artcoder import artcoder

firstConnection = True

def imageToBase64(img, format='JPEG'):
	buffered = BytesIO()
	img.save(buffered, format=format)
	return base64.b64encode(buffered.getvalue()).decode()

def sanitizeFolder(folder):
	folder = folder.replace(".","")
	folder = folder.replace("\\","")
	folder = folder.replace("/","")
	return folder

class Session:
	def __init__(self, ws, trainer):
		self.ws = ws
		self.trainer = trainer

	async def start(self):
		self.settings = {}

		global firstConnection
		if firstConnection:
			firstConnection = False
			await self.sendMessage('reload')

		self.updates = [
			["data", ['data', 'level', 'minVersion', 'versionPadding']],
			["content", ['moduleSize', 'brightness', 'contrast', 'selectedContents']],
			["basic", []],
			["style", ['selectedStyles']],
			["styled", ['training', 'learningRate', 'contentWeight', 'styleWeight', 'codeWeight', 'epochs', 'discriminant', 'correct']],
		]

		self.updateDirty = {}
		for id, settings in self.updates:
			self.updateDirty[id] = False

		self.updateThread = None
		self.currentUpdate = None

		task1 = asyncio.ensure_future(self.updateReceive())
		task2 = asyncio.ensure_future(self.run())
		done, pending = await asyncio.wait(
			[task1, task2],
			return_when=asyncio.ALL_COMPLETED,
		)
		for task in pending:
			task.cancel()

	async def updateReceive(self):
		async for msg in self.ws:
			try:
				data = json.loads(msg)
				await self.onMessage(data['event'], data)
			except Exception as e:
				pass

	async def onMessage(self, event, data):
		if event == 'sessionId':
			self.sessionId = data['id']

			self.sessionPath = './sessions/' + sanitizeFolder(self.sessionId)
			self.outputPath = self.sessionPath + '/output'
			Path(self.sessionPath).mkdir(parents=True, exist_ok=True)
			Path(self.outputPath).mkdir(parents=True, exist_ok=True)

			await self.sendStyles()
			await self.sendContents()
		elif event == 'deleteSessionImage':
			path = os.path.abspath(data['path']) 
			sessionPath = os.path.abspath(self.sessionPath);

			if path.startswith(sessionPath):
				os.remove(path)

		elif event == 'uploadSessionImage':
			path = self.sessionPath + "/" + sanitizeFolder(data['folder']) + "/" + data['name'].replace('/', '').replace('\\', '')
			with open(path, "wb+") as f:
				f.write(base64.b64decode(data['data']))

			await self.sendImageList(data["folder"])
		else:
			self.settings[event] = data[event]

			for id, settings in self.updates:
				if event in settings:
					await self.onUpdate(id)
					return

	def getUpdateIndex(self, id):
		return [u[0] for u in self.updates].index(id)

	async def onUpdate(self, id):
		index = self.getUpdateIndex(id)

		print('update', self.updateDirty)

		if self.updateThread != None:

			currentIndex = self.getUpdateIndex(self.currentUpdate)
			if currentIndex < index:
				return

			if not killThread(self.updateThread):
				return

			self.updateThread = None		

		found = False
		for i, settings in self.updates:
			if not found and id == i:
				found = True

			if found and not self.updateDirty[i]:
				self.updateDirty[i] = True
				await self.sendMessage(i + 'Dirty')

		def run():
			self.loop = asyncio.new_event_loop()
			
			try:
				for i in self.updates[index::]:
					self.currentUpdate = i[0]
					func = getattr(self, 'on' + self.currentUpdate.capitalize() + 'Updated')
					self.updateDirty[self.currentUpdate] = False
					if func:
						self.loop.run_until_complete(func())

				self.loop.close()

				self.currentUpdate = None
				self.updateThread = None
			except Exception as e:
				if type(e).__name__ != 'SystemExit':
					traceback.print_exc()
					error = {'message': str(e), 'state': self.currentUpdate}
					print('error', error)
					self.loop.run_until_complete(self.sendMessage('error', {'error': error}))
					
			finally:
				self.loop.close()

		self.updateThread = threading.Thread(target=run, args=())
		self.updateThread.daemon = True
		self.updateThread.start()

	async def sendMessage(self, event, data = {}):
		data['event'] = event
		await self.ws.send(json.dumps(data))

	async def run(self):
		await asyncio.sleep(1000000)

	async def sendImageList(self, id):
		files = []

		def forEachFile(path, f, fromSession):
			path = path + "/" + f
			data = base64.b64encode((open(path, 'rb')).read()).decode()
			return {"path": path, "fromSession": fromSession, "data": data}

		def gatherFiles(path, fromSession):
			for (dirpath, dirnames, filenames) in walk(path):
				files.extend(list(map(lambda f: forEachFile(path, f, fromSession), filenames)))
				break

		gatherFiles("./data/" + id, False)
		gatherFiles(self.sessionPath + '/' + id, True)

		await self.sendMessage(id, {id: files})

	async def sendStyles(self):
		await self.sendImageList('styles')

	async def sendContents(self):
		await self.sendImageList('contents')

	async def onDataUpdated(self):
		settings = self.settings
		version, segments = segmentData(settings['data'], settings['level'], 1, 40)
		self.segments = segments

		await self.sendMessage('dataMinVersion', {'dataMinVersion': version})
		await self.sendMessage('segments', {'segments': json.dumps(segments)})

		version += int(settings['versionPadding'])
		self.version = max(version, int(settings['minVersion']))

		self.moduleNum = self.version * 4 + 17

		await self.sendMessage('version', {'version': self.version})

	async def onContentUpdated(self):
		settings = self.settings

		self.moduleSize = int(settings['moduleSize'])

		contentImg = Image.open(settings['selectedContents']).convert('RGB')
		contentImg, contentModules, contentWeights, edgesImg, saliencyImg, weightsImg = prepareContent(contentImg, self.moduleNum, self.moduleSize, self.outputPath)

		contentImg = ImageEnhance.Brightness(contentImg).enhance(float(settings['brightness']))
		contentImg = ImageEnhance.Contrast(contentImg).enhance(float(settings['contrast']))

		self.contentImg = contentImg
		self.contentModules = contentModules
		self.contentWeights = contentWeights

		self.edgesImg = edgesImg
		self.saliencyImg = saliencyImg
		self.weightsImg = weightsImg
		await self.sendMessage('contentsPreview', {'contentsPreview': imageToBase64(contentImg)})

	async def onBasicUpdated(self):
		settings = self.settings

		await self.sendMessage('modulesImg', {'modulesImg': imageToBase64(Image.fromarray(self.contentModules))})
		await self.sendMessage('edgesImg', {'edgesImg': imageToBase64(self.edgesImg)})
		await self.sendMessage('saliencyImg', {'saliencyImg': imageToBase64(self.saliencyImg)})
		await self.sendMessage('weightsImg', {'weightsImg': imageToBase64(self.weightsImg)})

		self.codeImg = encodeQr(self.segments, int(settings['level']), self.version, self.contentModules, self.contentWeights, self.moduleSize, self.outputPath)
		await self.sendMessage('codeImg', {'codeImg': imageToBase64(self.codeImg)})

		self.combined = combine(self.codeImg, self.contentImg, True, self.moduleSize).convert("RGB")
		self.combined = utils.add_pattern(self.combined, self.codeImg, self.version, module_number=self.moduleNum, module_size=self.moduleSize)
		await self.sendMessage('combined', {'combined': imageToBase64(self.combined)})

	async def onStyleUpdated(self):
		settings = self.settings

		styleImg = Image.open(settings['selectedStyles']).convert('RGB')

		w, h = styleImg.size
		minSize = min(w, h)
		marginW = (w - minSize) / 2
		marginH = (h - minSize) / 2
		contentBox = (marginW, marginH, w - marginW, h - marginH)
		moduleSize = self.moduleSize
		moduleNum = self.moduleNum
		targetSize = (moduleNum * moduleSize, moduleNum * moduleSize)
		styleImg = styleImg.resize(targetSize,  Image.BICUBIC, contentBox, 2.0)

		self.styleImg = styleImg

		await self.sendMessage('stylesPreview', {'stylesPreview': imageToBase64(styleImg)})

	async def onStyledUpdated(self):
		settings = self.settings

		if not bool(settings['training']):
			await self.sendMessage('queue', {'queue': {'status': 'paused'}})
			return

		await self.trainer.queueTraining(self)

	async def train(self):
		settings = self.settings

		self.epochs = int(settings['epochs'])
		self.learningRate = float(settings['learningRate'])
		self.contentWeight = 10 ** float(settings['contentWeight'])
		self.styleWeight = 10 ** float(settings['styleWeight'])
		self.codeWeight = 10 ** float(settings['codeWeight'])
		self.discriminant = float(settings['discriminant'])
		self.correct = float(settings['correct'])

		from timeit import default_timer as timer
		for output in artcoder(self.styleImg, self.contentImg, self.codeImg, self.sessionPath, self.version, 
							moduleSize=self.moduleSize, moduleNum=self.moduleNum, EPOCHS=self.epochs, LEARNING_RATE=self.learningRate,
							CONTENT_WEIGHT=self.contentWeight, STYLE_WEIGHT=self.styleWeight, CODE_WEIGHT=self.codeWeight,
							discrim=self.discriminant, correct=self.correct):
			if 'image' in output:
				output['image'] = imageToBase64(output['image'])

			if 'gifPath' in output:
				output['gif'] = imageToBase64(Image.open(output['gifPath']), 'gif')

			await self.sendMessage('styledUpdate', {'styledUpdate': output})

