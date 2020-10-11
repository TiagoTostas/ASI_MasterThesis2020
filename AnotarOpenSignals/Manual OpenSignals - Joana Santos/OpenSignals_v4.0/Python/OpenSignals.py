import shutil
import numpy
import h5py
import h5db
import json
import inspect
import time
import socket
import os
import os.path
import fileinput
# import BITalino
import bitalino
import multiprocessing
import traceback
import datetime
import copy
import pandas
import math
from txws import WebSocketFactory
from twisted.internet import protocol, reactor
import ujson
global id
global CPTH
global INSDIR
global dataset

CPTH=None
id=0


class VS(protocol.Protocol):
	def connectionMade(self):
		self.transport.write('ConnectionMade()')

	def send(self,data,prot):
		prot.transport.write(data)
		
	def dataReceived(self, data):
		print "Server received: %s"%data
		try:
			if "StartAcquisition()" in data:
				StartAcquisition(self)
				res = 'printMessage("BeginAcquisition")'
			else: res = eval(data)
			
			self.transport.write(res)
			print "Server sent: %s"%"Ok"
		except Exception as e:
			pass
			print "in exception dataReceived"
			print traceback.format_exc()
	
	def connectionLost(self, reason):
		global CPTH
		if CPTH:
			if CPTH.acquire == True:
				StopAcquisition()

		connector.stopListening()
		reactor.stop()
		os.system("exit")
		print "Connection LOST!"
		# CPTH.exit()
		os.system('Taskkill /IM GoogleChromePortable.exe /F')
		CPTH._Thread__stop()
		return
		
##############################
##### REALTIME FUNCTIONS #####
##############################
def getSettings() :
	f=open(os.path.join(INSDIR,'Settings.json'))
	settings = json.load(f)
	f.close()
	f=open(os.path.join(INSDIR,'Devices.json'))
	devices = json.load(f)
	f.close()
	return 'SetConfigurations('+ujson.dumps(settings)+','+ujson.dumps(devices)+')'

def saveConfig(device,macAddress,analogInp,digitalOut,labels,units,annotationKeys):
	check = True
	SetToSave = {"Device":device,"MacAddress":macAddress,"Analog":analogInp,"Digital":digitalOut,"Labels": labels, "Units":units, "AnotKeys":annotationKeys};
	f=open(os.path.join(INSDIR,'Settings.json'),'w')
	json.dump(SetToSave,f)
	f.close()
	if macAddress != "":
		f=open(os.path.join(INSDIR,'Devices.json'),'r')
		Dev = json.load(f)
		f.close()
		f=open(os.path.join(INSDIR,'Devices.json'),'w')
		for x,devs in enumerate(Dev):
			if Dev[x][0] == macAddress:
				if Dev[x][1] != device:
					Dev[x] = tuple([macAddress,device])
				check = False
				break
		if check: 
			temp = tuple([macAddress,device])
			Dev.append(temp)
		json.dump(Dev,f)
		f.close()
	else:
		f=open(os.path.join(INSDIR,'Devices.json'),'r')
		Dev = json.load(f)
		f.close()
	return 'SetConfigurations('+ujson.dumps(SetToSave)+','+ujson.dumps(Dev)+')'

def getRTDatatoFlot(datasets):
	global dataset
	dataset = copy.deepcopy(datasets) 
	data = [];
	for i in numpy.arange(60):
		data.append([i,0])
	for x in datasets:
		datasets[x]['data'] = data
	return 'BuildPage('+json.dumps(datasets,sort_keys=False)+',"")'


def getFile(path,back):
	if back == False:
		if os.path.isfile(path) == True:
			path = os.path.dirname(path)
		os.chdir(path);
		dirL = os.listdir(os.getcwd());
		dirFinal = [];
		filesFinal = [];
		list=[]
		for i,item in enumerate(dirL):
		 try:
			 json.dumps(item)
			 list.append(item)
		 except:
			 list.append(item.decode("utf-8","ignore"))
		for el in list:
			try:
				if os.path.isdir(os.path.join(os.getcwd(),el)) == True :
					os.listdir(os.path.join(os.getcwd(),el))
					dirFinal.append(el)
				elif os.path.isfile(os.path.join(os.getcwd(),el)) == True and el.split('.')[-1] == 'hdf5' or el.split('.')[-1] == 'txt' :
					filesFinal.append(el)
			except WindowsError:
				pass 
		dir = {"path":os.getcwd(),"dir":dirL,"files":filesFinal};
		dir = {"path":path,"dir":dirFinal,"files":filesFinal};
	else:
		currentDir = path;
		os.chdir(currentDir);
		currentD = os.path.dirname(os.getcwd())
		dirL = os.listdir(currentD);
		dirFinal = [];
		filesFinal = [];
		list=[]
		for i,item in enumerate(dirL):
		 try:
			 json.dumps(item)
			 list.append(item)
		 except:
			 list.append(item.decode("utf-8","ignore"))
		for el in list:
			try:
				if os.path.isdir(os.path.join(currentD,el)) == True :
					os.listdir(os.path.join(currentD,el))
					dirFinal.append(el)
				elif os.path.isfile(os.path.join(currentD,el)) == True and el.split('.')[-1] == 'hdf5' or el.split('.')[-1] == 'txt' :
					filesFinal.append(el)
			except WindowsError:
				pass 
		dir = {"path":currentD,"dir":dirFinal,"files":filesFinal};
	return 'DisplayFiles('+ujson.dumps(dir)+')'

def SetupAcquisition(MACAddress,channelsList,samplingRate,units):
	import ArduinoToBrowser1 as ArduinoToBrowser
	global CPTH
	try:
		if CPTH:
			# CPTH.exit()
			CPTH.restartVariables()
		else:
			CPTH = ArduinoToBrowser.ThreadArduino()
			CPTH.start()
		CPTH.macAddress = MACAddress 
		CPTH.AnalogChannels = channelsList
		CPTH.SamplingRate = samplingRate
		CPTH.units = units
		CPTH.inoconnect()
		answer = "Connect(true)"
		
	except Exception as e: 
		
		answer = "Connect(false)"
		pass
		print "exception Setup -> ",e
	return answer

def StartAcquisition(protocolReactor):
	global CPTH
	global id
	global StartTime
	global dataset
	StartTime = datetime.datetime.now()
	filename = os.path.join(INSDIR+'/Python/temp', StartTime.strftime("%Y%m%d-%H%M%S")+'-record%s'%id+'.hdf5')
	header = {'date': datetime.datetime.utcnow().isoformat(),'SamplingRate':CPTH.SamplingRate}
	
	# Creates HDF5 file to save signals in real time
	fid = h5db.hdf(filename, 'w')
	fid.addInfo(header)
	signalsRT = {}
	blockShape = (CPTH.nSamples,)
	keysSorted = dataset.keys()
	keysSorted.sort()
	for i,j in enumerate(dataset):
		mdata = {'type': '/AnalogInputs/Analog%s'%i,  'name': dataset[keysSorted[i]]['label'].split(' [')[0],'labels': [dataset[keysSorted[i]]['label'].split(' [')[0]]}
		dataName = dataset[keysSorted[i]]['label'].split(' [')[0]
		signalsRT['Analog%s'%i] = fid.addSignalRT(mdata['type'], mdata, dataName, blockShape)#, compress=True)
	for i in range(4) :
		mdata = {'type': '/DigitalInputs/Digital%s'%i,  'name': 'Digital%s'%i,'labels': ['Digital%s'%i]}
		dataName = 'Digital%s'%i
		signalsRT['Digital%s'%i] = fid.addSignalRT(mdata['type'], mdata, dataName, blockShape,compress=True)
		
	mdata = {'type': '/others', 'name': 'SeqN', 'labels':['SeqN']}
	signalsRT['SeqN'] = fid.addSignalRT(mdata['type'], mdata, 'SeqN', blockShape)#,compress=True)
	CPTH.file=fid
	CPTH.RT = signalsRT
	CPTH.filename = filename
	CPTH.Newfilename = None
	
	# Sends command to start acquisition
	CPTH.acquire = True
	CPTH.reactorr = protocolReactor
	id=id+1
	print "Acquisition set to start"

	
def StopAcquisition():
	global EndTime;
	import datetime
	EndTime = datetime.datetime.now()
	CPTH.child.send('END')
	# CPTH.RT={}
	return "printMessage('Stop acquisition')"

def saveDigitalOutput(data):
	f=open(os.path.join(INSDIR,'Settings.json'))
	settings = json.load(f)
	f.close()
	settings['Digital'] = data
	f=open(os.path.join(INSDIR,'Settings.json'),'w')
	json.dump(settings,f)
	f.close()
	StopAcquisition()
	return 'printMessage("Settings of Digital Output saved!")'

def saveEvent(sample, description):
	global CPTH
	if description in CPTH.events.keys():
		CPTH.events[description].append([sample,sample])
	else:
		CPTH.events[description] = [[sample,sample]]

	return 'printMessage("Event saved on sample '+str(sample)+'")'

	
def CLOSE():
	global CPTH
	if CPTH:
		if CPTH.acquire == True:
			StopAcquisition()
	reactor.stop()
	return "printMessage('closed')"
	

def listHDF5Signals(file):	
	signals=[]
	#Function to select signals from the hdf5 tree file
	def func(name, obj): 
		if isinstance(obj, h5py._hl.dataset.Dataset): 
			n=name.split('/')
			if n[0] == 'signals' :
				signals.append(name) 
		
	file.visititems(func)
	signals.sort()
	return signals
	
def checkFile(path,file,type):
	check = os.path.exists(path+'/'+file+'.'+type)
	return "FileExists("+str(check).lower()+")"

def saveFile(path,file,type):
	try:
		global CPTH
		file.decode("utf-8","ignore")
		## TXT File
		if type=="txt":
			if file[-4:] == '.txt': file = file[:-4]
			f=h5py.File(CPTH.filename);
			
			mdata = f.attrs['json']
			head = eval(mdata)
			
			sig = listHDF5Signals(f)
			FinalArray = numpy.zeros((len(f[sig[0]].value),len(sig)))
			
			h = [None] * len(sig)
			for s in sig:
				if 'SeqN' in s:
					FinalArray[:,0] = f[s].value
					h[0] = s
				elif 'Digital' in s:
					d = s.split('/')[-1][-1]
					FinalArray[:,int(d)+1] = f[s].value
					h[int(d)+1] = s
				elif 'Analog' in s:
					a = s.split('/')[-2][-1]
					FinalArray[:,int(a)+5] = f[s].value
					h[int(a)+5] = s
			head['ChannelsOrder'] = h
			
			numpy.savetxt(path+'/'+file+'.txt',FinalArray,fmt='%0d',delimiter='\t',header=json.dumps(head))
			
			#save Events
			events = []
			def func(name, obj): 	
				if isinstance(obj, h5py._hl.dataset.Dataset): 
					n=name.split('/')
					if n[0] == 'events' and n[-1] != 'values':
						events.append(name) 

			f.visititems(func)
			FinalArrayEvents = [None] *len(events)
			if len(events) > 0:
				for i,e in enumerate(events):
					ev = e.split('/')
					evFinal = "/".join(ev[0:-1])
					J = json.loads(f[evFinal].attrs['json'])
					J['data'] = f[e].value.tolist();
					J['label'] = J['name'] if J.has_key('name') else J['label']
					FinalArrayEvents[i] = J
				
				fEvent = open(path+'/'+file+'.ev','w')
				json.dump(FinalArrayEvents,fEvent)
				fEvent.close()
			
			f.close()
			CPTH.Newfilename = os.path.join(path,file+'.txt')
			
		## HDF5 file
		else:
			if file[-5:] == '.hdf5': file = file[:-5]
			shutil.copy(CPTH.filename,os.path.join(path,file+'.hdf5'))
			f = h5db.hdf(os.path.join(path,file+'.hdf5'))
			mdata = f.getInfo()['header']
			mdata['name'] = file
			f.addInfo(mdata)
			f.close()
			CPTH.Newfilename = os.path.join(path,file+'.hdf5')
			
	except Exception:
		print traceback.format_exc()
	return 'FileSaved()'

def changeXScale(UpOrDown):
	global CPTH
	if UpOrDown == 'up':
		if CPTH.t != (len(CPTH.xScale)-1):
			CPTH.t += 1
	else:
		if CPTH.t != 0:
			if CPTH.t == 1 and CPTH.SamplingRate == 1:
				return ""
			else:
				CPTH.t -= 1
	return 'NewXScale('+str(CPTH.xScale[CPTH.t])+')'

# def digitalOutputs(DOarray):
	# global CPTH
	# data = 3
	# for i,j in enumerate(DOarray):
		# data = data | j<<(2+i)
	# CPTH.device.write(data)
	# return 'printMessage("DigitalOut done")'

# def battery(data):
	# global CPTH
	# CPTH.device.write(data)
	# return 'printMessage("battery threshold set")'
	
def digitalOutputs(DOarray):
	global CPTH
	data = 3
	for i,j in enumerate(DOarray):
		data = data | j<<(2+i)
	CPTH.parent.send("self.write("+str(data)+")")
	return 'printMessage("DigitalOut done")'

def battery(data):
	global CPTH
	CPTH.parent.send("self.write("+str(data)+")")
	return 'printMessage("battery threshold set")'


def search():
	f=open(os.path.join(INSDIR,'Devices.json'))
	old_devices = json.load(f)
	f.close()
	for i in range(len(old_devices)):
		old_devices[i] = tuple(old_devices[i])
	nearby_devices = bitalino.BITalino().find()
	if nearby_devices == -1:
		return "SearchDevices(-1)"
	bitDevices = []
	for addr,name in nearby_devices:
		if 'bit' in name:
			bitDevices.append((addr,name))
	new = []
	if old_devices != [] and bitDevices != []: 
		new_devices = list(set(zip(*bitDevices)[0])-set(zip(*old_devices)[0]))
		
		for x,i in enumerate(list(zip(*bitDevices)[0])):
			for j in new_devices:
				if i ==j:
					new.append(bitDevices[x])
	else:
		new = bitDevices
	Dev = {}
	Dev['old'] = old_devices
	Dev['new'] = new
	return "SearchDevices("+json.dumps(Dev)+")"

###############################
###### OFFLINE FUNCTIONS ######
###############################

def getDatatoFlot(signals = None, Npixels = 1000,FilePath = None): 
	global pathFile
	global Npix;
	global samplingRate
	Npix = Npixels;
	
	if FilePath == None:
		global CPTH
		if CPTH.Newfilename == None:
			FilePath = CPTH.filename
		else:
			FilePath = CPTH.Newfilename
	else:
		FilePath = os.path.abspath(pathFile)
		FilePath = os.path.abspath(FilePath)
		# pathFile = FilePath
	FilePath = os.path.abspath(FilePath)
	FilePath = FilePath.replace('\\','/')
	pathFile = os.path.abspath(FilePath)
	print "pathFile: ", pathFile
	global signal_data;
	try:
		if signal_data[0]['file'] != None:
			signal_data[0]['file'].close()
	except NameError:
		pass
		
	events=[]
	
	if '.hdf5' in FilePath:
		file=h5py.File(FilePath);
		# print "FilePath: ",FilePath
		#get events
		def func(name, obj): 	
			if isinstance(obj, h5py._hl.dataset.Dataset): 
				n=name.split('/')
				if n[0] == 'events' and n[-1] != 'values':
					events.append(name) 
		
		file.visititems(func)
		print events
		#get signals if not set as input
		if signals == None:
			sig = listHDF5Signals(file)
			signals = []
			for s in sig:
				if 'Analog' in s:
					signals.append(s)
		file.close()

		signal_data=[None for k in xrange(len(signals))]
		
		# get signals dataset
		file = h5db.hdf(FilePath)
		header = file.getInfo()['header']
		samplingRate = int(header['SamplingRate']) if 'SamplingRate' in header else 1000
		# samplingRate = 1000
		#join signals and metadata in one JSON object -> signal_data
		for i in range(0,len(signals)):
			type = '/'.join(signals[i].split('/')[1:-1])
			name = signals[i].split('/')[-1]
			j = file.getSignalSet('/'+type,name)
			signal_data[i] = j['mdata']
			signal_data[i]['data'] = j['signal']
		# file.close()
		
		
	elif '.txt' in FilePath:
		#read file
		f=open(FilePath,'r')
		header = f.readline();
		data = pandas.read_table(f, header=0)
		DataTable = data.values
		f.close()
		header = header[2:-1]
		header = json.loads(header)
		signalsOrder = header['ChannelsOrder']
		samplingRate = int(header['SamplingRate'])
		
		j = {}
		if signals == None:
			signals = []
			for i in signalsOrder:
				if 'AnalogInputs' in i:
					signals.append(i)
		signal_data=[None] * len(signals);
		
		for k in range(0,len(signals)):
			s = signalsOrder.index(signals[k])
			j['labels'] = [signalsOrder[s].split('/')[-1]]
			j['data'] = DataTable[:,s]
			j['type'] = '/'.join(signalsOrder[s].split('/')[1:-1])
			signal_data[k] = j.copy()
	
	# time variable
	global timeElapsed
	timeElapsed = numpy.arange(len(signal_data[0]['data']))
	timeElapsed*=(1000/samplingRate)
	
	#calculate downsampling factor
	factor=int(len(signal_data[0]['data'])/Npixels)
	if factor < 1:
		factor = 1
		
	#construct dataset dictionary
	d = '{';
	for i in range(0,len(signal_data)):
		if 'labels' in signal_data[i]:
			lb = signal_data[i]["labels"][0]
		else:
			lb = signal_data[i]["name"]
		if i != len(signal_data)-1 :
			d += '"'+str(i)+'":{"label":"'+lb+'","data":[],"anot":[],"path":"'+signal_data[i]["type"]+'","id":'+str(i)+',"factor":"'+str(factor)+'"},'
		else:
			d += '"'+str(i)+'":{"label":"'+lb+'","data":[],"anot":[],"path":"'+signal_data[i]["type"]+'","id":'+str(i)+',"factor":"'+str(factor)+'"}'

	d += '}';
	global datasets;
	datasets = {};
	datasets = json.loads(d)
	
	#Convert data to flot format
	for dt in range(0,len(signal_data)):
		signalTemp = signal_data[dt]['data'][::factor]
		temp = numpy.zeros((len(signalTemp),2))
		temp[:,0] = timeElapsed[::factor] #x axis
		temp[:,1] = signalTemp 			  #y axis
		datasets[str(dt)]["data"] = temp.tolist()
		datasets[str(dt)]["incNumber"] = 0
		try:
			datasets[str(dt)]['units'] = signal_data[dt]['units']['signal']
		except:
			datasets[str(dt)]['units'] = {}
			pass
	
	#Add annotations to dataset
	if '.hdf5' in FilePath:
		for i in range(len(events)):
			ev = events[i].split('/');
			evType = "/".join(ev[1:-2]);
			evName =ev[-2];
			out = file.getEvent('/'+evType, evName)
			JSON=out['mdata']
			JSON['data'] = out['timeStamps']*(1000/samplingRate)
			JSON['data'] = JSON['data'].tolist();
			JSON['label'] = JSON['name'] if JSON.has_key('name') else JSON['label']
			for key in datasets:
				if datasets[key]["path"][1:] == evType:
					datasets[key]["anot"].append(JSON)
					datasets[key]["incNumber"]=len(datasets[key]["anot"])
		signal_data[0]['file'] = file
			
	elif '.txt' in FilePath:
		file_path = FilePath.replace('txt','ev')
		if os.path.exists(file_path):
			f=open(file_path,'r')
			txt_events = json.load(f)
			f.close()
			for i in txt_events:
				for key in datasets:
					if datasets[key]['path'] in i['type']:
						datasets[key]["anot"].append(i)
						datasets[key]["incNumber"]=len(datasets[key]["anot"])
		signal_data[0]['file'] = None
	
	# else:
		# file.close();
	
	return 'BuildPage('+ujson.dumps(datasets)+','+ujson.dumps(FilePath)+')'

def getPreviousData(fileName):
	global pathFile
	path = os.path.dirname(pathFile)
	if '.hdf5' in fileName:
		listFiles = [f for f in os.listdir(path) if '.hdf5' in f]
		pos = listFiles.index(fileName)
		if pos == 0:
			res = "printMessage('No more next data')"
			#do nothing
		else:
			file = listFiles[pos-1]
			# print "previous file: ",file
			f = h5py.File(os.path.join(path,file))
			sig = listHDF5Signals(f)
			f.close()
			pathFile = os.path.join(path,file)
			res = getDatatoFlot(sig,FilePath = pathFile)
		# print res
		return res
	else:
		return "printMessage('txt data not possible yet')"

def getNextData(fileName):
	global pathFile
	path = os.path.dirname(pathFile)
	if '.hdf5' in fileName:
	# print "path: ",path
		listFiles = [f for f in os.listdir(path) if '.hdf5' in f]
		pos = listFiles.index(fileName)
		if pos == len(listFiles)-1:
			res = "printMessage('No more next data')"
			#do nothing
		else:
			file = listFiles[pos+1]
			# print "next file: ",file
			f = h5py.File(os.path.join(path,file))
			sig = listHDF5Signals(f)
			f.close()
			pathFile = os.path.join(path,file)
			res = getDatatoFlot(sig,FilePath = pathFile)
		# print res
		return res
	else:
		return "printMessage('txt data not possible yet')"
	


def ZoomData(minLimit,maxLimit, channels = None):
	
	global Npix
	global signal_data;
	global samplingRate;
	global timeElapsed
	global datasets
	minLimit = minLimit/(1000/samplingRate)
	maxLimit = maxLimit/(1000/samplingRate)
	if channels == None: channels = range(len(signal_data))
	for i in range(0,len(signal_data)):
		newFactor = int((maxLimit - minLimit)/Npix)
		if newFactor < 2:
			newFactor = 1
	
	window = maxLimit - minLimit
	windowMin = int((minLimit-3*window))
	windowMax = int((maxLimit+3*window))
	
	if windowMin < 0:
		windowMin =0
	if windowMax > len(signal_data[0]['data'])-1:
		windowMax = len(signal_data[0]['data'])
	print "window min %s and max %s"%(windowMin,windowMax)
	temp = numpy.zeros((int(math.ceil((windowMax-windowMin)/float(newFactor))),2))
	temp[:,0] = timeElapsed[windowMin:windowMax:newFactor]
	for dt in range(0,len(signal_data)):
		label = str(dt)
		# print "length temp: ",len(temp)
		if dt in channels:
			# t0 = time.time()
			sTemp = signal_data[dt]['data'][windowMin:windowMax]
			temp[:,1] = sTemp[::newFactor]
			# t1 = time.time()
			
			signal_data[dt]['min'] = windowMin
			signal_data[dt]['max'] = windowMax
			signal_data[dt]['factor'] = newFactor
			datasets[label]["data"] = temp.tolist()
			datasets[label]["min"] = int(minLimit)*(1000/samplingRate)
			datasets[label]["max"] = int(maxLimit)*(1000/samplingRate)
			datasets[label]["factor"] = newFactor
			# t2 = time.time()
		else:
			signal_data[dt]['min'] = minLimit
			signal_data[dt]['max'] = maxLimit
			signal_data[dt]['factor'] = newFactor
			datasets[label]["data"] = []
			datasets[label]["min"] = int(minLimit)*(1000/samplingRate)
			datasets[label]["max"] = int(maxLimit)*(1000/samplingRate)
			datasets[label]["factor"] = newFactor
		# print "time getting data: ",t1-t0
		# print "time data to list: ",t2-t1
		

	return 'changeSelection('+ujson.dumps(datasets)+')'
	
def newWindow(window,direction, channels = None):
	global timeElapsed
	global signal_data
	global datasets
	global samplingRate
	
	if channels == None: channels = range(len(signal_data))
	window = numpy.array(window)/(1000/samplingRate)
	for dt in range(0,len(signal_data)):
		label = str(dt)
		factor = signal_data[dt]['factor']

		if dt in channels:
			if direction == "right":
				windowMin = signal_data[dt]["max"]
				windowMax = windowMin+(3*window[dt])
				if windowMax > len(signal_data[dt]['data'])-1:
					print len(signal_data[dt]['data'])-1
					windowMax = len(signal_data[dt]['data'])
				print "window min %s and max %s"%(windowMin,windowMax)
				if windowMin == windowMax:
					return 'printMessage("")'
				
				# signal_data[dt]['min'] = windowMin
				signal_data[dt]['max'] = windowMax
				temp = numpy.zeros((int(math.ceil((windowMax-windowMin)/float(factor))),2))
				temp[:,0] = timeElapsed[windowMin:windowMax:factor]
				sTemp = signal_data[dt]['data'][windowMin:windowMax]
				temp[:,1] = sTemp[::factor]
				datasets[label]["data"] = temp.tolist()
				
			else:
				windowMax = signal_data[dt]["min"]
				windowMin = windowMax-(3*window[dt])
				if windowMin < 0:
					windowMin =0
				print "window min %s and max %s"%(windowMin,windowMax)
				if windowMin == windowMax:
					return 'printMessage("")'
				
				signal_data[dt]['min'] = windowMin
				# signal_data[dt]['max'] = windowMax
				temp = numpy.zeros((int(math.ceil((windowMax-windowMin)/float(factor))),2))
				temp[:,0] = timeElapsed[windowMin:windowMax:factor]
				sTemp = signal_data[dt]['data'][windowMin:windowMax]
				temp[:,1] = sTemp[::factor]
				datasets[label]["data"] = temp.tolist()
				
		else:
			datasets[label]["data"] = []

	return 'concatData('+ujson.dumps(datasets)+',"'+direction+'")'
	
def FileTree(FilePath):
	global pathFile;
	FilePath = os.path.abspath(FilePath)
	pathFile = FilePath
	if '.hdf5' in FilePath:
		#open file
		file=h5py.File(FilePath);
		signals=[]
		#Function to select signals from the hdf5 tree file
		def func(name, obj): 
			
			if isinstance(obj, h5py._hl.dataset.Dataset): 
				n=name.split('/')
				if n[0] == 'signals' or n[0] == 'data':
					signals.append(name) 
		file.visititems(func)
		signals.sort()
		file.close()
		return 'TreeView('+json.dumps(signals)+','+json.dumps(FilePath)+')'
	else:
		f=open(FilePath,'r')
		header = f.readline();
		f.close()
		header = header[2:-1]
		header = json.loads(header)
		signals = header['ChannelsOrder']
		
		return 'TreeView('+json.dumps(signals)+','+json.dumps(FilePath)+')'

def saveAnnotations(FilePath,type,anot,signalInfo,color,name,user): 
	#type: region or line
	#anot: array with annotations
	#signalInfo: signal to attach annotations
	#metaData : JSON with color information
	#name : name of the annotation
	global samplingRate
	if FilePath == "":
		global CPTH
		if CPTH.Newfilename == None:
			FilePath = CPTH.filename
		else:
			FilePath = CPTH.Newfilename
	else:
		FilePath = os.path.abspath(FilePath)
	print "File Path", FilePath
	eventType = signalInfo;
	timeStamps = numpy.array(json.loads(anot))/(1000/samplingRate);
	timeStamps = timeStamps.tolist();
	eventName = name;
	mdata = {'color':color,'annotationType':type,'label':eventName,'type':eventType,'user':user};
	if '.hdf5' in FilePath:
		file = h5db.hdf(FilePath);
		file.addEvent(eventType,timeStamps,mdata = mdata,eventName = eventName)
		file.close();
	elif '.txt' in FilePath:
		mdata['data'] = timeStamps
		file_path = FilePath.replace('txt','ev')
		if os.path.exists(file_path):
			fEvent = open(file_path,'r')
			ANOT = json.load(fEvent)
			fEvent.close()
			ANOT.append(mdata)
		else:
			ANOT = [mdata]
		
		fEvent = open(FilePath.replace('txt','ev'),'w')
		json.dump(ANOT,fEvent)
		fEvent.close()
		
	return 'printMessage("Events Saved")'

def deleteAnnotations(FilePath,eventType,eventName):
	if FilePath == "":
		global CPTH
		if CPTH.Newfilename == None:
			FilePath = CPTH.filename
		else:
			FilePath = CPTH.Newfilename
	# FilePath = os.path.abspath(FilePath)
	if '.hdf5' in FilePath:
		file = h5db.hdf(FilePath);
		file.delEvent(eventType, eventName)
		file.close()
	elif '.txt' in FilePath:
		fEvent = open(FilePath.replace('txt','ev'),'r')
		ANOT = json.load(fEvent)
		fEvent.close()
		indexToEliminate = None
		for i,a in enumerate(ANOT):
			if eventType in a['type'] and a['label'] == eventName:
				indexToEliminate = i
				print indexToEliminate
				break
		del ANOT[indexToEliminate]
		fEvent = open(FilePath.replace('txt','ev'),'w')
		json.dump(ANOT,fEvent)
		fEvent.close()
	return 'printMessage("Events Deleted")'
	
def editAnnotations(FilePath,type,anot,signalInfo,color,name,previousName,user):
	global samplingRate
	if FilePath == "":
		global CPTH
		if CPTH.Newfilename == None:
			FilePath = CPTH.filename
		else:
			FilePath = CPTH.Newfilename
	eventType = signalInfo;
	# eventType = "/".join(eventType[1:-1])
	timeStamps = numpy.array(json.loads(anot))/(1000/samplingRate);
	timeStamps = timeStamps.tolist();
	eventName = name;
	mdata = {'color':color,'annotationType':type,'label':eventName,'type':eventType,'user':user};
	# FilePath = os.path.abspath(FilePath)
	try:
		if '.hdf5' in FilePath:
			file = h5db.hdf(FilePath);
			file.delEvent(eventType, previousName)
			file.close()
			file = h5db.hdf(FilePath);
			file.addEvent(eventType,timeStamps,mdata = mdata,eventName = eventName)
			file.close()
		elif '.txt' in FilePath:
			mdata['data'] = timeStamps
			fEvent = open(FilePath.replace('txt','ev'),'r')
			ANOT = json.load(fEvent)
			fEvent.close()
			for a in ANOT:
				if a['type'] == eventType and a['label'] == previousName:
					a['label'] = eventName
					a['data'] = timeStamps
			fEvent = open(FilePath.replace('txt','ev'),'w')
			json.dump(ANOT,fEvent)
			fEvent.close()
	except Exception as e:
		print traceback.format_exc()

	return 'printMessage("Events Edited")'

def getComment(FilePath = None):
	
	if FilePath == None:
		global pathFile
		FilePath = pathFile
	print "path : ", FilePath
	if '.hdf5' in FilePath:
		file = h5db.hdf(FilePath)
		header = file.getInfo()['header']
		comment = header['Comments'] if 'Comments' in header else ""
		file.close()
		
	elif '.txt' in FilePath:
		#read file
		f=open(FilePath,'r')
		header = f.readline();
		header = header[2:-1]
		header = json.loads(header)
		comment = header['Comments'] if 'Comments' in header else ""
		f.close()
	print "comment: ",comment
	return 'getComment('+json.dumps(comment)+')'
	

def saveComment(FilePath, comments):
	if FilePath == "":
		global CPTH
		if CPTH.Newfilename == None:
			FilePath = CPTH.filename
		else:
			FilePath = CPTH.Newfilename
	else:
		global pathFile
		FilePath = os.path.abspath(pathFile)
	print "FilePath: ", FilePath
	if '.hdf5' in FilePath:
		file = h5db.hdf(FilePath);
		header = file.getInfo()['header']
		header['Comments'] = comments
		file.addInfo(header)
		file.close()
	elif '.txt' in FilePath:
		f=open(FilePath,'r')
		header = f.readline();
		header = header[2:-1]
		header = json.loads(header)
		header['Comments'] = comments
		remainder = f.read()
		f.close()
		header = json.dumps(header)
		t = open(FilePath,"w")
		t.write("# "+header + "\n")
		t.write(remainder)
		t.close()
	return 'printMessage("Comments saved!")'


class VSFactory(protocol.Factory):
	def buildProtocol(self, addr):
		return VS()

if __name__=='__main__':
	global INSDIR
	INSDIR = os.getcwd()
	#delete temp files from previous session
	frame = inspect.currentframe()
	filename = inspect.getframeinfo(frame).filename
	pathStd = os.path.dirname(os.path.abspath(filename))
	del frame
	if len(os.listdir(pathStd+'/temp')) != 0:
		for i in os.listdir(pathStd+'/temp'):
			os.remove(pathStd+'/temp'+'/'+i)
	try:
		# Launch WebServer
		ip_addr, port = "127.0.0.1", 9001 # socket.gethostbyname(socket.getfqdn()) #
		print "Listening at port %s of %s\n"%(port, ip_addr)
 
		connector = reactor.listenTCP(port, WebSocketFactory(VSFactory())) # console to html communication
		# os.system('start C:\OpenSignals\chrome\GoogleChromePortable.exe --allow-file-access-from-files file:///C:/Users/Priscila%20Alves/Dropbox/WORK/PROJECTS/BIT/SignalBIT/SignalBIT%20OFFLINE_REALTIME/v2/OpenSignals.html')
		os.system('start chrome\GoogleChromePortable.exe --allow-file-access-from-files -kiosk file:///C:\\OpenSignals_v4.0' + os.path.sep + 'OpenSignals.html')
		
		reactor.run()

	except Exception as e:
		print traceback.format_exc()
		print "Resetting .."
