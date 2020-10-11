# # -*- coding: utf-8 -*-

""" 
.. module:: bitalino
   :platform: Windows
   :synopsis: BITalino API

.. moduleauthor:: Priscila Alves <@plux.info>
.. moduleauthor:: José Guerreiro <@plux.info>
.. moduleauthor:: Carlos Carreiras <@plux.info>
.. moduleauthor:: Hugo Silva <@plux.info>

*Created on Tue Jun 25 13:44:28 2013*
"""


try:
    import bluetooth
    from bluetooth import discover_devices
except ImportError:
    pass
import serial
from serial.tools import list_ports
import time
import math
import numpy


class BITalino(object):
    """**BITalino Class**: Interface to the **BITalino** Hardware."""
    
    def __init__(self):
        self.socket = None
        self.analogChannels = []
        self.number_bytes = None
        self.macAddress = None
        self.serial = False
    
    def find(self, serial=False):
        """
        :param serial: Serial port (True) or MAC address (False)
        :type serial: bool.
        :returns: MAC address or serial of each device found

        Searches for bluetooth devices nearby.
        
        Possible return formats:
        
        =========  ===================================================== =====================
        *serial*   Returns                                                Examples              
        =========  ===================================================== =====================
        True       List of port names containing ``bitalino`` or ``COM`` ``['COM1','COM3']``
        False      List of (tuples) with MAC address and name            ``[('00:0a:95:9d:68:16','bitalino_name')]``
        =========  ===================================================== =====================
        """
        
        try:
            if serial:
                nearby_devices = list(port[0] for port in list_ports.comports() if 'bitalino' or 'COM' in port[0])
            else:
                nearby_devices = discover_devices(lookup_names=True)
            return nearby_devices
        except:
            return -1
    
    def open(self, macAddress=None, SamplingRate=1000):
        """
        :param macAddress: MAC address or serial port of the bluetooth device
        :type macAddress: str.
        :param SamplingRate: Sampling frequency (Hz)
        :type SamplingRate: int.
        :returns: True (Ok) or False (Error)
        :raises TypeError: When MAC address or serial port are not defined
        :raises TypeError: When sampling rate type is not supported
        :raises ValueError: When sampling rate value is not valid
             
        Connects to the bluetooth device with the MAC address or serial port provided and configures the sampling rate. Setting the sampling
        rate on the device implies the use of the method :meth:`write`
        
        Possible values for parameter *macAddress*:
        
        * MAC address: e.g. ``00:0a:95:9d:68:16``
        * Serial port - number: number of the device, numbering starts at zero
        * Serial port - device name: depending on the operating system. e.g. ``COM3`` on Windows; ``/dev/tty.bitalino-DevB`` on Mac OS X; ``/dev/ttyUSB0`` on GNU/Linux.
        
        Possible values for parameter *SamplingRate*:
        
        * 1
        * 10
        * 100
        * 1000
        """
        
        # check inputs
        if macAddress is None:
            raise TypeError, "A MAC address or serial port is needed to connect."
        
        try:
            SamplingRate = int(SamplingRate)
        except Exception, e:
            raise TypeError, "Unsupported sampling rate type (%s)." % e
        
        if SamplingRate not in [1, 10, 100, 1000]:
            raise ValueError,  "The specified sampling rate %s is not valid; choose 1, 10, 100, or 1000." % SamplingRate
        
        # connect socket
        try:
            if ':' in macAddress and len(macAddress) == 17:
                # bluetooth
                self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.socket.connect((macAddress, 1))
            else:
                # serial
                self.socket = serial.Serial(macAddress, 115200)
                self.serial = True
            
            # set sampling rate
            time.sleep(2)
            if SamplingRate == 1000:
                variableToSend = 0x03
            elif SamplingRate == 100:
                variableToSend = 0x02
            elif SamplingRate == 10:
                variableToSend = 0x01
            elif SamplingRate == 1:
                variableToSend = 0x00
            
            variableToSend = int((variableToSend<<6)|0x03)
            self.write(variableToSend)
        except Exception, e:
            print "BITalino.open:", e
            return False
        else:
            self.macAddress = macAddress
            return True
    
    def start(self, analogChannels=[0, 1, 2, 3, 4, 5]):
        """
        :param analogChannels: Channels to be acquired
        :type analogChannels: array, tuple or list of int.
        :returns: True (Ok)
        :raises TypeError: When list of analog channels is not supported
        :raises TypeError: When set of analog channels is not valid
        :raises TypeError: When a connection to the device is not open
             
        Starts acquisition in the analog channels set. Starting the acquisition in the 
        defined analog channels implies the use of the method :meth:`write`
        
        Possible values, types, configurations and examples for parameter *analogChannels*:
        
        ===============  ====================================
        Values           0, 1, 2, 3, 4, 5
        Types            list ``[]``, tuple ``()``, array ``[[]]``
        Configurations   Any number of channels, identified by their value
        Examples         ``[0, 3, 4]``, ``(1, 2, 3, 5)``
        ===============  ====================================
        
        .. note:: To obtain the samples, use method :meth:`read`
        """
        
        # check type of list of analog channels
        if isinstance(analogChannels, list):
            self.analogChannels = analogChannels
        elif isinstance(analogChannels, tuple):
            self.analogChannels = list(analogChannels)
        elif isinstance(analogChannels, numpy.ndarray):
            self.analogChannels = analogChannels.astype('int').tolist()
        else:
            raise TypeError, "Unsupported analog channels list type."
        
        # remove repeats
        self.analogChannels = list(set(self.analogChannels))
        
        # check items
        nb = len(self.analogChannels)
        pValues = range(6)
        if nb == 0 or nb > 6 or any([item not in pValues for item in self.analogChannels]):
            raise TypeError, "Analog channels set not valid."
        
        if self.socket is None:
            raise TypeError, "An input connection is needed."
        bit = 1
        #setting channels mask
        for i in analogChannels:
            bit = bit | 1<<(2+i)
        #start acquisition
        self.write(bit)
        return True
    
    def stop(self):
        """
        :returns: True (Ok)
        :raises TypeError: When a connection to the device is not open
        
        Stops acquisition. Stoping the acquisition implies the use of the method :meth:`write`
        """
        
        if self.socket is None:
            raise TypeError, "An input connection is needed."
        
        # Send stop mode
        self.write(0)
        
        return True
    
    def close(self):
        """
        :returns: True (Ok)
        :raises TypeError: When a connection to the device is not open
        
        Closes the bluetooth socket
        """
        
        # Check
        if self.socket is None:
            raise TypeError, "An input connection is needed."
        
        self.socket.close()
        
        return True
    
    def write(self, data=0):
        """
        :returns: True (Ok)
        :raises TypeError: When a connection to the device is not open
        
        Sends a command to the BITalino device 
        """
        if self.socket is None:
            raise TypeError, "An input connection is needed."

        # Send Mode
        if self.serial:
            self.socket.write(chr(data))
        else:
            self.socket.send(chr(data))
        return True
    
    def battery(self, value=0):
        """
        :param value: Threshold value [0 - 63]
        :type value: int.
        :returns: True (Ok)
        :raises TypeError: When a connection to the device is not open
        :raises TypeError: When the threshold value is invalid
        
        Sets the battery threshold for the BITalino device. Setting the battery threshold implies the use of the method :meth:`write`
        
        Possible values for parameter *value*:
        
        ===============  =======  =====================
        Range            *value*  Corresponding threshold (Volts)               
        ===============  =======  =====================
        Minimum *value*  0        3.4 Volts
        Maximum *value*  63       3.8 Volts
        ===============  =======  =====================
        
        .. warning:: Only works in IDLE mode       
        """
        
        if self.socket is None:
            raise TypeError, "An input connection is needed."
        
        # Send Mode
        if 0 <= value <= 63:
            Mode = value << 2
            self.write(Mode)
        else:
            raise TypeError, "The threshold value must be between 0 and 63."
        
        return True
    
    def trigger(self, digitalArray=[0, 0, 0, 0]):
        """
        :param digitalArray: Array which acts on digital outputs according to the value: 0 or 1
        :type digitalArray: array, tuple or list of int.
        :returns: True (Ok)
        :raises TypeError: When list of digital channels output is not supported
        :raises TypeError: When set of digital channels output is not valid
        :raises TypeError: When a connection to the device is not open
             
        Acts on digital output channels of the BITalino device. Triggering these digital outputs implies the use of the method :meth:`write`
       
        Each position of the array *digitalArray* corresponds to a digital output, in ascending order. Possible values, types, configurations and examples for parameter *digitalArray*:

        ===============  ====================================
        Values           0 or 1
        Types            list ``[]``, tuple ``()``, array ``[[]]``
        Configurations   4 values, one for each digital channel output
        Examples         ``[1, 0, 1, 0]``: Digital 0 and 2 will be set to 1 while Digital 1 and 3 will be set to 0
        ===============  ====================================    
       
        .. warning:: Only works during acquisition mode          
        """
        
        if self.socket is None:
            raise TypeError, "An input connection is needed."
        
        # check type of digital array
        if isinstance(digitalArray, list):
            pass
        elif isinstance(digitalArray, tuple):
            digitalArray = list(digitalArray)
        elif isinstance(digitalArray, numpy.ndarray):
            digitalArray = digitalArray.astype('int').tolist()
        else:
            raise TypeError, "Unsupported digital channels list type."
        
        # check items
        pValues = [0, 1]
        if len(digitalArray) != 4 or any([item not in pValues for item in digitalArray]):
            raise TypeError, "Digital channels set not valid."
        
        data = 3
        for i,j in enumerate(digitalArray):
            data = data | j<<(2+i)
        
        self.write(data)
        return True
    
    def version(self):
        """
        :returns: (str.) Version of BITalino 
        :raises TypeError: When a connection to the device is not open
        
        Retrieves the BITalino version. Retrieving the version implies the use of the method :meth:`write`

        .. warning:: Only works in IDLE mode
        """
        
        if self.socket is None:
            raise TypeError, "An input connection is needed."
        
        self.write(7)
        version = ' '
        
        # choose serial or socket
        if self.serial:
            reader = self.socket.read
        else:
            reader = self.socket.recv
        
        while version[-1] != '\n':
            version += reader(1)
        else:
            return version[:-1]
    
    def read(self, nSamples=100):
        """
        :param nSamples: Number of samples to acquire
        :type nSamples: int.
        :returns: (array) Data acquired
        :raises TypeError: When a connection to the device is not open
        
        Acquires a defined number of samples (`nSamples`) from BITalino. Reading samples from BITalino implies the use of the method :meth:`decode`
        
        Requiring a low number of samples (e.g. ``nSamples = 1``) may be computationally expensive; it is recommended to acquire batches of samples (e.g. ``nSamples = 100``)

        The data acquired is organized in a matrix whose lines correspond to samples and the columns are as follows:
        
        * Sequence Number
        * 4 Digital Channels (always present)
        * 1-6 Analog Channels (as defined in the :meth:`start` method)
        
        Example matrix for ``analogChannels = [0, 1, 3]`` used in :meth:`start` method
        
        ==================  ========= ========= ========= ========= ======== ======== ========
        Sequence Number*    Digital 0 Digital 1 Digital 2 Digital 3 Analog 0 Analog 1 Analog 3              
        ==================  ========= ========= ========= ========= ======== ======== ========
        0                   
        1 
        (...)
        15
        0
        1
        (...)
        ==================  ========= ========= ========= ========= ======== ======== ========
        
        .. note:: *The sequence number overflows at 15 
        """
        
        if self.socket is None:
            raise TypeError, "An input connection is needed."
        
        nChannels = len(self.analogChannels)
        
        if nChannels <=4 :
            self.number_bytes = int(math.ceil((12.+10.*nChannels)/8.))
        else:
            self.number_bytes = int(math.ceil((52.+6.*(nChannels-4))/8.))
        
        # choose serial or socket
        if self.serial:
            reader = self.socket.read
        else:
            reader = self.socket.recv
        
        # get data according to the value nSamples set
        dataAcquired = numpy.zeros((5 + nChannels, nSamples))
        Data = ''
        sampleIndex = 0
        while sampleIndex < nSamples:
            while len(Data) < self.number_bytes:
                Data += reader(1)
            else:
                decoded = self.decode(Data)
                if len(decoded) != 0: 
                    dataAcquired[:, sampleIndex] = decoded.T
                    Data = ''
                    sampleIndex += 1    
                else:
                    Data += reader(1)
                    Data = Data[1:] 
                    print "ERROR DECODING"
        else:
            return dataAcquired
    
    def decode(self, data, nAnalog=None):
        """
        :param data: Data to be decoded
        :type data: array
        :param nAnalog: Number of analog channels contained in the data
        :type nAnalog: int    
        :returns: (array) Data decoded
        
        Unpacks data samples acquired from BITalino (bytes) to hexadecimal. 
        """
        
        if nAnalog == None: nAnalog = len(self.analogChannels)
        if nAnalog <= 4:
            number_bytes = int(math.ceil((12. + 10. * nAnalog) / 8.))
        else:
            number_bytes = int(math.ceil((52. + 6. * (nAnalog - 4)) / 8.))
        
        nSamples = len(data) / number_bytes
        res = numpy.zeros(((nAnalog + 5), nSamples))
        
        j, x0, x1, x2, x3, out, inp, col, line = 0, 0, 0, 0, 0, 0, 0, 0, 0
        encode0F = int('\x0F'.encode("hex"), 16)
        encode01 = int('\x01'.encode("hex"), 16)
        encode03 = int('\x03'.encode("hex"), 16)
        encodeFC = int('\xFC'.encode("hex"), 16)
        encodeFF = int('\xFF'.encode("hex"), 16)
        encodeC0 = int('\xC0'.encode("hex"), 16)
        encode3F = int('\x3F'.encode("hex"), 16)
        encodeF0 = int('\xF0'.encode("hex"), 16)
        
        #CRC check
        CRC = int(data[j + number_bytes - 1].encode("hex"), 16) & encode0F
        for byte in range(number_bytes):
            for bit in range(7, -1, -1):
                inp = int(data[byte].encode("hex"), 16)>>bit & encode01
                if byte == (number_bytes - 1) and bit < 4:
                    inp = 0
                out = x3
                x3 = x2
                x2 = x1
                x1 = out^x0
                x0 = inp^out
        
        if CRC == int((x3<<3)|(x2<<2)|(x1<<1)|x0):
            try:
                # Seq Number
                SeqN = int(data[j + number_bytes - 1].encode("hex"), 16) >> 4 & encode0F
                res[line, col] = SeqN
                line += 1
                
                # Digital 0
                Digital0 = int(data[j + number_bytes - 2].encode("hex"), 16) >> 7 & encode01
                res[line, col] = Digital0
                line += 1
                
                # Digital 1
                Digital1 = int(data[j + number_bytes - 2].encode("hex"), 16) >> 6 & encode01
                res[line, col] = Digital1
                line += 1
                
                # Digital 2
                Digital2 = int(data[j + number_bytes - 2].encode("hex"), 16) >> 5 & encode01
                res[line, col] = Digital2
                line += 1
                
                # Digital 3
                Digital3 = int(data[j + number_bytes - 2].encode("hex"), 16) >> 4 & encode01
                res[line, col] = Digital3
                line += 1
                
                if number_bytes >= 3:
                    # Analog 0
                    Analog0 = (int(data[j + number_bytes - 2].encode("hex"), 16) & encode0F) << 6 | (int(data[j + number_bytes - 3].encode("hex"), 16) & encodeFC) >> 2
                    res[line, col] = Analog0
                    line += 1
                    
                if number_bytes >= 4:
                    # Analog 1
                    Analog1 = (int(data[j + number_bytes - 3].encode("hex"), 16) & encode03) << 8 | (int(data[j + number_bytes - 4].encode("hex"), 16) & encodeFF)
                    res[line, col] = Analog1
                    line += 1
                    
                if number_bytes >= 6:
                    # Analog 2
                    Analog2 = (int(data[j + number_bytes - 5].encode("hex"), 16) & encodeFF) << 2 | (int(data[j + number_bytes - 6].encode("hex"), 16) & encodeC0) >> 6
                    res[line, col] = Analog2
                    line += 1
                    
                if number_bytes >= 7:
                    # Analog 3
                    Analog3 = (int(data[j + number_bytes - 6].encode("hex"), 16) & encode3F) << 4 | (int(data[j + number_bytes - 7].encode("hex"), 16) & encodeF0) >> 4
                    res[line, col] = Analog3
                    line += 1
                    
                if number_bytes >= 8:
                    # Analog 4
                    Analog4 = (int(data[j + number_bytes - 7].encode("hex"), 16) & encode0F) << 2 | (int(data[j + number_bytes - 8].encode("hex"), 16) & encodeC0) >> 6
                    res[line, col] = Analog4
                    line += 1
                    
                    # Analog 5
                    if numpy.shape(res)[0] == 11:
                        Analog5 = int(data[j + number_bytes - 8].encode("hex"), 16) & encode3F
                        res[line, col] = Analog5
                
            except Exception:
                print "exception decode"
            return res
        else:
            return []

if __name__ == '__main__':
    
    #Example
    device = BITalino()
    
    # macAddress = "00:13:01:04:02:16"
    macAddress = "COM7"
    SamplingRate = 1000
    nSamples = 10
    
    # Connect to bluetooth device and set Sampling Rate
    device.open(macAddress, SamplingRate)
    
    #set battery threshold
    th = device.battery(20)
    
    #get BITalino version
    BITversion = device.version()
    print "version: ", BITversion
    
    #Start Acquisition in Analog Channels 0 and 3
    device.start([0, 3])
    
    #Read 1000 samples
    dataAcquired = device.read(nSamples)
    
    # turn BITalino led on
    device.trigger([0, 0, 1, 0])
    
    #stop acquisition
    device.stop()
    device.close()
    
    SeqN = dataAcquired[0, :]
    D0 = dataAcquired[1, :]
    D1 = dataAcquired[2, :]
    D2 = dataAcquired[3, :]
    D3 = dataAcquired[4, :]
    A0 = dataAcquired[5, :]
    A3 = dataAcquired[6, :]  
    print SeqN
    
