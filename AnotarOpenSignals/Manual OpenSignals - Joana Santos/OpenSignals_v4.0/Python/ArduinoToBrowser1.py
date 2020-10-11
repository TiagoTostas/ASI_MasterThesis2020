# Imports
import time
import numpy
# import BITalino
import bitalino
import traceback
import threading
import multiprocessing
from multiprocessing import Process, Pipe
import OpenSignals as OpenSignals
from twisted.internet import protocol, reactor
import ujson

class ThreadArduino(threading.Thread):
	""" Threaded Arduino """
	def __init__(self):
		threading.Thread.__init__(self)
		self.macAddress = None
		self.SamplingRate = None
		self.AnalogChannels = []
		self.units = []
		self.nSamples = 300
		self.SCREEN_SIZE = 1000
		self.flot_xy = numpy.zeros((self.SCREEN_SIZE,2))  
		self.flot_xy[:,0] = numpy.arange(self.SCREEN_SIZE)
		self.xScale = (1,3,6,10,20,30)
		self.acquire = False
		self.reactorr = None
		self.file = None
		self.RT = {}
		self.filename = None
		self.t = 3
		self.flot_xyO = numpy.zeros((self.SCREEN_SIZE,2))*(60./self.SCREEN_SIZE) 
		self.flot_xyO[:,0] = numpy.arange(self.SCREEN_SIZE)*(60./self.SCREEN_SIZE)
		self.unitsLabels = {"V":"self.toV(%s)","mV":"self.tomV(%s)","uS":"self.touS(%s)","lx":"self.toLux(%s)","G":"self.toG(%s)","None":"%s"}
		self.device = bitalino.BITalino()
		self.events = {}
		
	
	# Arduino connection
	def inoconnect(self):
		if self.device.socket: 
			self.device.close()
			time.sleep(2)
		self.btConnection = self.device.open(self.macAddress, self.SamplingRate)
		if  not self.btConnection: raise TypeError, "Could not connect to bluetooth device."
		else:
			# Create acquisition event
			self.acquisitionFlag = multiprocessing.Event()
			# Create pipe for parent-child communication
			self.parent, self.child = multiprocessing.Pipe()
			self.acquisitionProcess = None
			
			if self.SamplingRate == 1000:
				self.device.write(195)
				self.nSamples = 300
				self.SCREEN_SIZE = 1000
			elif self.SamplingRate == 100:
				self.device.write(131)
				self.nSamples = 12
				if self.xScale[self.t] >= 10:
					self.SCREEN_SIZE = 1000
				else:
					self.SCREEN_SIZE = self.xScale[self.t] * self.SamplingRate
			elif self.SamplingRate == 10:
				self.device.write(67)
				self.nSamples = 1
				self.SCREEN_SIZE = self.xScale[self.t] * self.SamplingRate
				self.flot_xyO = numpy.zeros((600,2))*(60./600.)
				self.flot_xyO[:,0] = numpy.arange(600)*(60./600.)
			elif self.SamplingRate == 1:
				self.device.write(3)
				self.nSamples = 1
				self.SCREEN_SIZE = self.xScale[self.t] * self.SamplingRate
				self.flot_xyO = numpy.zeros((60,2))*(60./60.)
				self.flot_xyO[:,0] = numpy.arange(60)*(60./60.)
			self.flot_xy = numpy.zeros((self.SCREEN_SIZE,2))  
			self.flot_xy[:,0] = numpy.arange(self.SCREEN_SIZE)

	def restartVariables(self):
		self.macAddress = None
		self.SamplingRate = None
		self.AnalogChannels = []
		self.units=[]
		self.nSamples = 300
		self.SCREEN_SIZE = 1000
		self.flot_xy = numpy.zeros((self.SCREEN_SIZE,2))  
		self.flot_xy[:,0] = numpy.arange(self.SCREEN_SIZE)
		self.xScale = (1,3,6,10,20,30)
		self.acquire = False
		self.reactorr = None
		self.file = None
		self.RT = {}
		self.filename = None
		self.flot_xyO = numpy.zeros((self.SCREEN_SIZE,2))*(60./self.SCREEN_SIZE) 
		self.flot_xyO[:,0] = numpy.arange(self.SCREEN_SIZE)*(60./self.SCREEN_SIZE)
		self.unitsLabels = {"V":"self.toV(%s)","mV":"self.tomV(%s)","uS":"self.touS(%s)","lx":"self.toLux(%s)","G":"self.toG(%s)","None":"%s"}
		self.events = {}

	def run(self):
		from OpenSignals import VS
		while 1:
			try:
				# Init variables
				if self.acquire:
					
					SizeCoef = self.SCREEN_SIZE
					y_net = numpy.zeros((len(self.AnalogChannels),self.SCREEN_SIZE))
					
					resBegin = numpy.zeros(((len(self.AnalogChannels)+5),self.nSamples))
					
					Result = {'overview':{}}
					IntResult = numpy.zeros((len(self.AnalogChannels),60*self.SamplingRate))
					sampleNumber = numpy.array(range((-60*self.SamplingRate)+1,1))
					self.events = {}
					Overview = numpy.zeros((len(self.AnalogChannels),60*self.SamplingRate))
					for x in range(len(self.AnalogChannels)):
						Result['Analog%s'%x] = []
						Result['overview']['Analog%s'%x] = []
					Fp = 0
					
					# Start acquisition
					# Create acquisition process. Associate it with the acquisition event and the communication pipe
					if self.acquisitionProcess == None:
						self.acquisitionProcess = Acquisition(self)  
						self.acquisitionProcess.start()
					# Enable acquisition event
					self.acquisitionFlag.set()
					TempScale = self.t
					while self.acquire:
						try :
							# Acquire data
							if TempScale != self.t:
								TempScale = self.t
								if self.SamplingRate == 100 and TempScale <=3 or self.SamplingRate == 10 or self.SamplingRate == 1:
									self.flot_xy = numpy.zeros((self.SamplingRate*self.xScale[TempScale],2))
									# self.flot_xy[:,0] = numpy.arange(self.SamplingRate*self.xScale[TempScale])
									SizeCoef = self.SamplingRate*self.xScale[TempScale]
								else: SizeCoef = self.SCREEN_SIZE
									
							TempScale = self.t
							decodedData = self.parent.recv()
							if decodedData == 'END':
								self.acquire = False
								break
							if Fp == 60*self.SamplingRate:
								Fp = 0
							IntResult[:,Fp:Fp+self.nSamples] = decodedData[5:,:]
							sampleNumber += self.nSamples
							Fp = Fp+self.nSamples
							Overview[:,-Fp:] = IntResult[:,:Fp]
							Overview[:,:-Fp] = IntResult[:,Fp:]
							y_net = Overview[:,-(self.xScale[TempScale]*self.SamplingRate):][:,::((self.xScale[TempScale]*self.SamplingRate)/SizeCoef)]
							self.flot_xy[:,0] = sampleNumber[-(self.xScale[TempScale]*self.SamplingRate):][::((self.xScale[TempScale]*self.SamplingRate)/SizeCoef)]
							# Prepare string with x and y axis to flot
							for item in range(len(self.AnalogChannels)):
								self.flot_xy[:,1] = eval(self.unitsLabels[self.units[self.AnalogChannels[item]]]%y_net[item,:].tolist())
								Result['Analog%s'%item] = self.flot_xy.tolist()
								self.RT['Analog%s'%item].put(decodedData[item+5,:])
								if 60*self.SamplingRate >= 1000:
									downSampling = 60*self.SamplingRate/1000
								else:
									downSampling = 1
								self.flot_xyO[:,0] = sampleNumber[::downSampling]
								self.flot_xyO[:,1] = Overview[item,:][::downSampling]
								Result['overview']['Analog%s'%item] = self.flot_xyO.tolist()
							for item in range(4):
								Result['Digital%s'%item] = decodedData[item+1,-1]
								self.RT['Digital%s'%item].put(decodedData[item+1,:])
								
								
							self.RT['SeqN'].put(decodedData[0,:])####
							# self.RT['time'].put(sampleNumber[-self.nSamples:])
							# send samples to browser
							FLOT_DATA = ujson.dumps(Result)
							reactor.callFromThread(VS.send,VS(),"ws.data("+FLOT_DATA+")",self.reactorr)

						except Exception as e:
							print "exceptionArduinoToBrowser"
							print e
							print traceback.format_exc()
							pass
					if len(self.events.keys()) > 0 :
						self.saveEvents()
					self.acquisitionFlag.clear()
					self.file.close()
					self.RT = {}
					self.exit()
					
					
				
			except Exception as e:
				print "exception %s"%e
				self.acquisitionFlag.clear()
				self.acquire = False
				self.device.stop()
			
	def toV(self,value):
		return numpy.array(value)*(3.3/1024.)
		
	def tomV(self,value):
		return numpy.array(value)*(3300/1024.)
		
	def toG(self,value):
		minC = 195.
		maxC = 287.
		return 2*((numpy.array(value)-minC)/(maxC-minC))-1.
		
	def touS(self,value):
		return numpy.array(value) * 1031.25
		
	def toLux(self,value):
		return 20* self.tomV(value)
	
	def saveEvents(self):
		# header_ = self.file.getInfo()['header']
		# header_['events'] = self.events
		# self.file.addInfo(header_)
		for i in range(len(self.AnalogChannels)):
			for ev in self.events:
				##adicionar eventos com o mesmo path que os canais analogicos
				mdata = {"color": "black", "annotationType": "line", "type": '/AnalogInputs/Analog%s'%i, "user": "undefined", "label": ev}
				self.file.addEvent('/AnalogInputs/Analog%s'%i, self.events[ev], [], mdata, ev)
	
		
	def exit(self):
		if self.btConnection:
			self.device.stop()
			self.device.close()
		if self.acquisitionProcess != None:
			self.acquisitionProcess.terminate()
		
		
		
#######################
# ACQUISITION PROCESS #
#######################
class Acquisition(Process):
	""" Acquisition Process """
	def __init__(self, slfBITAcq):
		Process.__init__(self)
		self.device = slfBITAcq.device
		self.conn = slfBITAcq.child
		self.acquisition = slfBITAcq.acquisitionFlag
		self.nSamples = slfBITAcq.nSamples
		self.AnalogChannels  = slfBITAcq.AnalogChannels

	def run(self):
		while True:
			self.data = ''
			self.acquisition.wait()
			print "START"
			#START ACQUISITION
			self.device.start(self.AnalogChannels)
			while self.acquisition.is_set():
				self.data = self.device.read(self.nSamples)
				self.conn.send(self.data)
				self.data = ''