"""
.. module:: h5db
   :platform: Unix, Windows
   :synopsis: This module provides a wrapper to the HDF5 file format, adapting it to store biosignals according to the BioMESH specification at http://camoes.lx.it.pt/MediaWiki/index.php/Database_Specification#Data_Model

.. moduleauthor:: Carlos Carreiras
"""


import h5py
import json
from Queue import Empty
from multiprocessing import Process, Queue, Event


class hdf:
    """
    
    Wrapper class to operate on HDF5 records according to the BioMESH specification.
    
    Kwargs:
        
    
    Kwrvals:
        
    
    See Also:
        
    
    Notes:
        
    
    Example:
        
    
    References:
        .. [1]
        
    """
    
    
    def __init__(self, filePath=None, mode='a'):
        """
        
        Open the HDF5 record.
        
        Kwargs:
            filePath (str): Path to HDF5 file.
            
            mode (str): File access mode. Available modes:
                'r+': Read/write, file must exist
                'r': Read only, file must exist
                'w': Create file, truncate if exists
                'w-': Create file, fail if exists
                'a': Read/write if exists, create otherwise
                Default: 'a'.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid = hdf('record.hdf5', 'a')
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if filePath is None:
            raise TypeError, "A path to the HDF5 file is needed."
        
        # open the file
        self.file = h5py.File(filePath, mode)
        # check the basic structures
        try:
            self.signals = self.file['signals']
        except KeyError:
            if mode == 'r':
                raise IOError("File is in read only mode and doesn't have the required Group 'signals'; change to another mode.")
            self.signals = self.file.create_group('signals')
        try:
            self.events = self.file['events']
        except KeyError:
            if mode == 'r':
                raise IOError("File is in read only mode and doesn't have the required Group 'events'; change to another mode.")
            self.events = self.file.create_group('events')
        try:
            self.file.attrs['repack']
        except KeyError:
            if mode == 'r':
                raise IOError("File is in read only mode and doesn't have the required flag 'repack'; change to another mode.")
            self.file.attrs['repack'] = False
        try:
            self.file.attrs['delete']
        except KeyError:
            if mode == 'r':
                raise IOError("File is in read only mode and doesn't have the required 'delete' attribute; change to another mode.")
            self.file.attrs['delete'] = json.dumps({'list': []})
    
    
    def __enter__(self):
        """
        
        __enter__ Method for 'with' statement.
        
        Kwargs:
            None
        
        Kwrvals:
            None
        
        See Also:
            
        
        Notes:
            
        
        Example:
            
        
        References:
            .. [1]
            
        """
        
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        
        __exit__ Method for 'with' statement.
        
        Kwargs:
            None
        
        Kwrvals:
            None
        
        See Also:
            
        
        Notes:
            
        
        Example:
            
        
        References:
            .. [1]
            
        """
        
        self.close()
        
        return None
    
    
    def addInfo(self, header={}):
        """
        
        Method to add or overwrite the basic information (header) of the HDF5 record.
        
        Kwargs:
            header (dict): Dictionary (JSON) object with the information. Default: {}.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.addInfo({'name': 'record'})
        
        References:
            .. [1]
            
        """
        
        # add the information
        self.file.attrs['json'] = json.dumps(header)
        
        
    def getInfo(self):
        """
        
        Method to retrieve the basic information (header) of the HDF5 record.
        
        Kwargs:
            
        
        Kwrvals:
            header (dict): Dictionary object with the header information.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            header = fid.get()['header']
        
        References:
            .. [1]
            
        """
        
        # kwrvals
        kwrvals = {'header': {}}
        
        try:
            kwrvals['header'] = json.loads(self.file.attrs['json'])
        except KeyError:
            pass
        
        return kwrvals
    
    def addSignal(self, signalType='', signal=None, mdata=None, dataName=None, compress=False):
        """
        
        Method to add a signal (synchronous data) to the HDF5 record.
        
        Kwargs:
            signalType (str): Type of the signal to add. Default: ''.
            
            signal (array): Array with the signal to add.
            
            mdata (dict): Dictionary object with metadata about the data. Default: {}.
            
            dataName (str): Name of the dataset to be created.
            
            compress (bool): Flag to compress the data (GZIP). Default: False.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.addSignal('/test', [0, 1, 2], {'comments': '/test signal'}, 'signal0')
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if dataName is None:
            raise TypeError, "A name for the dataset must be specified."
        if mdata is None:
            mdata = {}
        
        # navigate to group
        weg = self.signals.name + signalType
        
        try:
            group = self.file[weg]
        except KeyError:
            # create group
            group = self.file.create_group(weg)
        
        # create new dataset in group
        if signal is None:
            dset = group.create_dataset(dataName, shape=(0, ), maxshape=(None, ), chunks=(1, ))
        else:
            if compress:
                dset = group.create_dataset(dataName, data=signal, compression='gzip')
            else:
                dset = group.create_dataset(dataName, data=signal)
        
        # set the attributes
        dset.attrs['json'] = json.dumps(mdata)
        
        return dset.name
    
    def addSignalRT(self, signalType='', mdata=None, dataName=None, blockShape=None, axis=0, dtype='f8', compress=False):
        """
        
        Method to add a signal (synchronous data) to the HDF5 record in real time.
        
        Kwargs:
            signalType (str): Type of the signal to add. Default: ''.
            
            mdata (dict): Dictionary object with metadata about the data. Default: {}.
            
            dataName (str): Name of the dataset to be created.
            
            blockShape (tuple): Shape of the signal blocks.
            
            axis (int): Direction on which the expansion of the dataset is made. Default: 0.
            
            dtype (str): Data type of the signal to add (supports numpy data types).
            
            compress (bool): Flag to compress the data (GZIP). Default: False.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if dataName is None:
            raise TypeError, "A name for the dataset must be specified."
        if mdata is None:
            mdata = {}
        if blockShape is None:
            raise TypeError, "A please specify the shape of the signal blocks."
        
        # navigate to group
        weg = self.signals.name + signalType
        
        try:
            group = self.file[weg]
        except KeyError:
            # create group
            group = self.file.create_group(weg)
        
        return realTime(group, mdata, dataName, blockShape, axis, dtype, compress)
        
    def getSignal(self, signalType='', dataName=None):
        """
        
        Method to retrieve a signal (synchronous data) from the HDF5 record.
        
        Kwargs:
            signalType (str): Type of the desired signal. Default: ''.
            
            dataName (str): Name of the dataset to retrieve.
        
        Kwrvals:
            signal (array): Array with the signals.
            
            mdata (dict): Dictionary object with metadata about the signals.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            out = fid.getSignal('/test', 'signal0')
            signal = out['signal']
            metadata = out['mdata']
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if dataName is None:
            raise TypeError, "A data name must be specified."
        
        if signalType == '':
            group = self.signals
        else:
            # navigate to group
            weg = self.signals.name + signalType
            group = self.file[weg]
        
        # get the data and mdata
        dset = group[dataName]
        try:
            data = dset[...]
        except ValueError:
            data = []
        mdata = json.loads(dset.attrs['json'])
        
        # kwrvals
        kwrvals = {}
        kwrvals['signal'] = data
        kwrvals['mdata'] = mdata
        
        return kwrvals
    
    def getSignalSet(self, signalType='', dataName=None):
        """
        
        Method to retrieve a signal (synchronous data) from the HDF5 record.
        
        Kwargs:
            signalType (str): Type of the desired signal. Default: ''.
            
            dataName (str): Name of the dataset to retrieve.
        
        Kwrvals:
            signal (array): Array with the signals.
            
            mdata (dict): Dictionary object with metadata about the signals.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            out = fid.getSignal('/test', 'signal0')
            signal = out['signal']
            metadata = out['mdata']
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if dataName is None:
            raise TypeError, "A data name must be specified."
        
        if signalType == '':
            group = self.signals
        else:
            # navigate to group
            weg = self.signals.name + signalType
            group = self.file[weg]
        
        # get the data and mdata
        dset = group[dataName]
        mdata = json.loads(dset.attrs['json'])
        
        # kwrvals
        kwrvals = {}
        kwrvals['signal'] = dset
        kwrvals['mdata'] = mdata
        
        return kwrvals
    
    
    def listSignals(self, signalType=''):
        """
        
        Method to list the signals (synchronous data) belonging to a given type.
        
        Kwargs:
            signalType (str): Type of the desired signal. Default: ''.
        
        Kwrvals:
            signalsList (lit): List of the signals of the given type.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.listSignals('/test')
        
        References:
            .. [1]
            
        """
        
        # kwrvals
        kwrvals = {'signalsList': []}
        
        if signalType == '':
            group = self.signals
        else:
            # navigate to group
            weg = self.signals.name + signalType
            try:
                group = self.file[weg]
            except KeyError:
                return kwrvals
        
        # loop the items
        for item in group.iteritems():
            if isinstance(item[1], h5py.Dataset):
                kwrvals['signalsList'].append(item[0])
        
        return kwrvals
    
    
    def delSignal(self, signalType='', dataName=None):
        """
        
        Method to delete a signal (synchronous data) from the HDF5 record. The record is marked for repackaging.
        
        Kwargs:
            signalType (str): Type of the desired signal. Default: ''.
            
            dataName (str): Name of the dataset to retrieve.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.delSignal('/test', 'data0')
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if dataName is None:
            raise TypeError, "A data name must be specified."
        
        if signalType == '':
            group = self.signals
        else:
            # navigate to group
            weg = self.signals.name + signalType
            group = self.file[weg]
        
        # delete if exists
        try:
            path = group[dataName].name
        except (ValueError, KeyError), e:
            pass
        else:
            del group[dataName]
            delete = json.loads(self.file.attrs['delete'])
            delete['list'].append(path)
            self.file.attrs['delete'] = json.dumps(delete)
        
        # set to repack
        self.setRepack()
    
    
    def delSignalType(self, signalType=''):
        """
        
        Method to delete a type of signals from the HDF5 record. The record is marked for repackaging.
        
        Kwargs:
            signalType (str): Signal type to delete. Default: ''.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.delSignalType('/test')
        
        References:
            .. [1]
            
        """
        
        # delete if exists
        try:
            path = self.signals['./' + signalType].name
        except (KeyError, ValueError), e:
            pass
        else:
            del self.signals['./' + signalType]
            delete = json.loads(self.file.attrs['delete'])
            delete['list'].append(path)
            self.file.attrs['delete'] = json.dumps(delete)
        
        # set to repack
        self.setRepack()
    
    
    def getSignalInfo(self, dataWeg=None):
        """
        
        Method to retrieve the metadata of a signal.
        
        Kwargs:
            dataWeg (str): Path to the dataset.
        
        Kwrvals:
            mdata (dict): Dictionary with the desired information.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            out = fid.getSignalInfo('/test/data0')
            metadata = out['mdata']
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if dataWeg is None:
            raise TypeError, "A signal path must be specified."
        
        # get the metadata
        dset = self.signals[dataWeg]
        mdata = json.loads(dset.attrs['json'])
        
        # kwrvals
        kwrvals = {}
        kwrvals['mdata'] = mdata
        
        return kwrvals
        
        
    def addEvent(self, eventType='', timeStamps=None, values=None, mdata=None, eventName=None, compress=False):
        """
        
        Method to add asynchronous data (events) to the HDF5 record.
        
        Kwargs:
            eventType (str): Type of the events to add. Default: ''.
            
            timeStamps (array): Array of time stamps. Default: [].
            
            values (array): Array with data for each time stamp. Default: [].
            
            mdata (dict): Dictionary object with metadata about the events. Default: {}.
            
            eventName (str): Name of the group to be created.
            
            compress (bool): Flag to compress the data (GZIP). Default: False.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.addEvent('/test', [0, 1, 2], [[1, 2], [3, 4], [5, 6]], {'comments': 'test event'}, 'event0')
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if eventName is None:
            raise TypeError, "A name for the event must be specified."
        if mdata is None:
            mdata = {}
        
        # navigate to group
        weg = self.events.name + eventType
        
        try:
            parentGr = self.file[weg]
        except KeyError:
            # create group
            parentGr = self.file.create_group(weg)
        
        # create new group in parentGr
        group = parentGr.create_group(eventName)
        
        # add the timeStamps and values
        if timeStamps is None:
            ts = group.create_dataset('timeStamps', shape=(0, ), maxshape=(None, ), chunks=(1, ))
        else:
            if compress:
                ts = group.create_dataset('timeStamps', data=timeStamps, compression='gzip')
            else:
                ts = group.create_dataset('timeStamps', data=timeStamps)
        if values is None:
            val = group.create_dataset('values', shape=(0, ), maxshape=(None, ), chunks=(1, ))
        else:
            if compress:
                val = group.create_dataset('values', data=values, compression='gzip')
            else:
                val = group.create_dataset('values', data=values)
        
        # set the attributes
        group.attrs['json'] = json.dumps(mdata)
        
        return group.name
    
    
    def getEvent(self, eventType='', eventName=None):
        """
        
        Method to retrieve asynchronous data(events) from the HDF5 record.
        
        Kwargs:
            eventType (str): Type of the desired event. Default: ''.
            
            eventName (str): Name of the dataset to retrieve.
        
        Kwrvals:
            timeStamps (array): Array of time stamps.
            
            values (array): Array with data for each time stamp.
            
            mdata (dict): Dictionary object with metadata about the events.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            out = fid.getEvent('/test', 'event0')
            timeStamps = out['timeStamps']
            values = out['values']
            metadata = out['mdata']
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if eventName is None:
            raise TypeError, "An event name must be specified."
        
        if eventType == '':
            parentGr = self.events
        else:
            # navigate to group
            weg = self.events.name + eventType
            parentGr = self.file[weg]
        
        # get the things
        group = parentGr[eventName]
        mdata = json.loads(group.attrs['json'])
        
        timeStamps = group['timeStamps']
        try:
            timeStamps = timeStamps[...]
        except ValueError:
            timeStamps = []
        
        values = group['values']
        try:
            values = values[...]
        except ValueError:
            values = []
        
        # kwrvals
        kwrvals = {}
        kwrvals['timeStamps'] = timeStamps
        kwrvals['values'] = values
        kwrvals['mdata'] = mdata
        
        return kwrvals
    
    
    def listEvents(self, eventType=''):
        """
        
        Method to list the events (asynchronous data) belonging to a given type.
        
        Kwargs:
            eventType (str): Type of the desired signal. Default: ''.
        
        Kwrvals:
            eventsList (lit): List of the events of the given type.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.listEvents('/test')
        
        References:
            .. [1]
            
        """
        
        # kwrvals
        kwrvals = {'eventsList': []}
        
        if eventType == '':
            group = self.signals
        else:
            # navigate to group
            weg = self.events.name + eventType
            try:
                group = self.file[weg]
            except KeyError:
                return kwrvals
        
        # loop the items
        for item in group.items():
            if isinstance(item[1], h5py.Group):
                try:
                    item[1].attrs['json']
                except KeyError:
                    pass
                else:
                    kwrvals['eventsList'].append(item[0])
        
        return kwrvals
    
    
    def delEvent(self, eventType='', eventName=None):
        """
        
        Method to delete asynchronous data (events) from the HDF5 record. The record is marked for repackaging.
        
        Kwargs:
            eventType (str): Type of the desired event. Default: ''.
            
            eventName (str): Name of the dataset to retrieve.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.delEvent('/test', 'event0')
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if eventName is None:
            raise TypeError, "An event name must be specified."
        
        if eventType == '':
            parentGr = self.events
        else:
            # navigate to group
            weg = self.events.name + eventType
            parentGr = self.file[weg]
        
        # delete if exists
        try:
            path = parentGr[eventName].name
        except (ValueError, KeyError), e:
            pass
        else:
            del parentGr[eventName]
            delete = json.loads(self.file.attrs['delete'])
            delete['list'].append(path)
            self.file.attrs['delete'] = json.dumps(delete)
        
        # set to repack
        self.setRepack()
    
    
    def delEventType(self, eventType=''):
        """
        
        Method to delete a type of asynchronous data from the HDF5 record. The record is marked for repackaging.
        
        Kwargs:
            eventType (str): Type of the desired event. Default: ''.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.delEventType('/test')
        
        References:
            .. [1]
            
        """
        
        # delete if exists
        try:
            path = self.events['./' + eventType].name
        except (KeyError, ValueError), e:
            pass
        else:
            del self.events['./' + eventType]
            delete = json.loads(self.file.attrs['delete'])
            delete['list'].append(path)
            self.file.attrs['delete'] = json.dumps(delete)
        
        # set to repack
        self.setRepack()
    
    
    def getEventInfo(self, eventWeg=None):
        """
        
        Method to retrieve the metadata of asynchronous.
        
        Kwargs:
            eventWeg (str): Path to the group.
        
        Kwrvals:
            mdata (dict): Dictionary with the desired information.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            out = fid.getEventInfo('/test/event0')
            metadata = out['mdata']
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if eventWeg is None:
            raise TypeError, "An event path must be specified."
        
        group = self.events[eventWeg]
        mdata = json.loads(group.attrs['json'])
        
        # kwrvals
        kwrvals = {}
        kwrvals['mdata'] = mdata
        
        return kwrvals
    
    
    def setRepack(self):
        """
        
        Set flag to repack.
        
        Kwargs:
            
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.setRepack()
        
        References:
            .. [1]
            
        """
        
        # set the flag
        self.file.attrs['repack'] = True
    
    
    def unsetRepack(self):
        """
        
        Unset flag to repack.
        
        Kwargs:
            
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.unsetRepack()
        
        References:
            .. [1]
            
        """
        
        # set the flag
        self.file.attrs['repack'] = False
    
    
    def getRepack(self):
        """
        
        Get the repack flag.
        
        Kwargs:
            
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            repack = fid.getRepack()
        
        References:
            .. [1]
            
        """
        
        return self.file.attrs['repack']
    
    
    def close(self):
        """
        
        Method to close the HDF5 record.
        
        Kwargs:
            
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.close()
        
        References:
            .. [1]
            
        """
        
        # flush buffers
        self.file.flush()
        
        # close the file
        self.file.close()
    
    
class meta:
    """
    
    Wrapper class to store experiments and subjects on HDF5.
    
    Kwargs:
        
    
    Kwrvals:
        
    
    See Also:
        
    
    Notes:
        
    
    Example:
        
    
    References:
        .. [1]
        
    """
    
    
    def __init__(self, filePath=None, mode='a'):
        """
        
        Open the HDF5 file.
        
        Kwargs:
            filePath (str): Path to HDF5 file.
            
            mode (str): File access mode. Available modes:
                'r+': Read/write, file must exist
                'r': Read only, file must exist
                'w': Create file, truncate if exists
                'w-': Create file, fail if exists
                'a': Read/write if exists, create otherwise
                Default: 'a'.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid = meta('expsub.hdf5', 'a')
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if filePath is None:
            raise TypeError, "A path to the HDF5 file is needed."
            
        # open the file
        self.file = h5py.File(filePath, mode)
        
        # check the basic structures
        try:
            self.experiments = self.file['experiments']
        except KeyError:
            if mode == 'r':
                raise IOError, "File is in read only mode and doesn't have the required Group 'experiments'; change to another mode."
            self.experiments = self.file.create_group('experiments')
        
        try:
            self.subjects = self.file['subjects']
        except KeyError:
            if mode == 'r':
                raise IOError("File is in read only mode and doesn't have the required Group 'subjects'; change to another mode.")
            self.subjects = self.file.create_group('subjects')
        try:
            self.file.attrs['repack']
        except KeyError:
            if mode == 'r':
                raise IOError("File is in read only mode and doesn't have the required flag 'repack'; change to another mode.")
            self.file.attrs['repack'] = False
    
    
    def __enter__(self):
        """
        
        __enter__ Method for 'with' statement.
        
        Kwargs:
            None
        
        Kwrvals:
            None
        
        See Also:
            
        
        Notes:
            
        
        Example:
            
        
        References:
            .. [1]
            
        """
        
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        
        __exit__ Method for 'with' statement.
        
        Kwargs:
            None
        
        Kwrvals:
            None
        
        See Also:
            
        
        Notes:
            
        
        Example:
            
        
        References:
            .. [1]
            
        """
        
        self.close()
        
        return None
    
    
    def setDB(self, dbName=None):
        """
        
        Method to set the DB the file belongs to.
        
        Kwargs:
            dbName (str): Name of the database.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.setDB('database')
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if dbName is None:
            raise TypeError, "A DB name must be provided."
        
        # set
        self.file.attrs['dbName'] = dbName
    
    
    def addSubject(self, subject={}):
        """
        
        Method to add a subject to the file.
        
        Kwargs:
            subject (dict): Dictionary with the subject information. Default: {}.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            The subject must have a '_id' key.
        
        Example:
            fid.addSubject({'_id': 0, 'name': 'subject'})
        
        References:
            .. [1]
            
        """
        
        # get the ID
        subjectId = subject['_id']
        
        # avoid latin1 characters in name
        try:
            name = subject['name']
        except KeyError:
            pass
        else:
            name = latin1ToAscii(name)
            subject.update({'name': name})
        
        # add the information
        dset = self.subjects.create_dataset(str(subjectId), data=json.dumps(subject))
    
    
    def getSubject(self, subjectId=None):
        """
        
        Method to get the information about a subject.
        
        Kwargs:
            subjectId (int): The ID of the subject.
        
        Kwrvals:
            subject (dict): Dictionary with the subject information.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            subject = fid.getSubject(0)['subject']
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if subjectId is None:
            raise TypeError, "A subject ID must be provided."
        
        try:
            aux = json.loads(str(self.subjects[str(subjectId)][...]))
        except KeyError:
            aux = {}
        
        # kwrvals
        kwrvals = {}
        kwrvals['subject'] = aux
        
        return kwrvals
    
    
    def updateSubject(self, subjectId=None, info={}):
        """
        
        Method to update a subject's information.
        
        Kwargs:
            sunjectId (int): The ID of the subject.
            
            info (dict): Dictionary with the information to update.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.updateSubject(0, {'new': 'field'})
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if subjectId is None:
            raise TypeError, "A subject ID must be provided."
        
        # get old info
        sub = self.getSubject(subjectId)['subject']
        del self.subjects[str(subjectId)]
        
        # update with new info
        sub.update(info)
        
        # store
        self.addSubject(sub)
    
    
    def listSubjects(self):
        """
        
        Method to list all the subjects in the file.
        
        Kwargs:
            
        
        Kwrvals:
            subList (list): List with the subjects.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            subList = fid.listSubjects()['subList']
        
        References:
            .. [1]
            
        """
        
        subList = []
        for item in self.subjects.iteritems():
            subList.append(self.getSubject(item[0])['subject'])
        
        return {'subList': subList}
    
    
    def addExperiment(self, experiment={}):
        """
        
        Method to add an experiment to the file.
        
        Kwargs:
            experiment (dict): Dictionary with the experiment information. Default: {}.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            The experiment must have a 'name' key.
        
        Example:
            fid.addExperiment({'name': 'experiment', 'comments': 'Hello world.'})
        
        References:
            .. [1]
            
        """
        
        # get the ID
        experimentName = experiment['name']
        
        # avoid latin1 characters in name
        try:
            experimentName = experiment['name']
        except KeyError:
            pass
        else:
            experimentName = latin1ToAscii(experimentName)
            experiment.update({'name': experimentName})
        
        # add the information
        dset = self.experiments.create_dataset(str(experimentName), data=json.dumps(experiment))
    
    
    def getExperiment(self, experimentName=None):
        """
        
        Method to get the information about an experiment.
        
        Kwargs:
            experimentName (str): The name of the experiment.
        
        Kwrvals:
            experiment (dict): Dictionary with the experiment information.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            experiment = fid.getExperiment('experiment')['experiment']
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if experimentName is None:
            raise TypeError, "An experiment name must be provided."
        
        try:
            aux = json.loads(str(self.experiments[str(experimentName)][...]))
        except KeyError:
            aux = {}
        
        # kwrvals
        kwrvals = {}
        kwrvals['experiment'] = aux
        
        return kwrvals
    
    
    def updateExperiment(self, experimentName=None, info={}):
        """
        
        Method to update an experiment's information.
        
        Kwargs:
            experimentName (str): Name of the experiment.
            
            info (dict): Dictionary with the information to update.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.updateExperiment('experiment', {'new': 'field'})
        
        References:
            .. [1]
            
        """
        
        # check inputs
        if experimentName is None:
            raise TypeError, "An experiment name must be provided."
        
        # get old info
        exp = self.getExperiment(experimentName)['experiment']
        del self.experiments[str(experimentName)]
        
        # update with new info
        exp.update(info)
        
        # store
        self.addExperiment(exp)
    
    
    def listExperiments(self):
        """
        
        Method to list all the experiments in the file.
        
        Kwargs:
            
        
        Kwrvals:
            expList (list): List with the experiments.
        
        See Also:
            
        
        Notes:
            
        
        Example:
            expList = fid.listExperiments()['expList']
        
        References:
            .. [1]
            
        """
        
        expList = []
        for item in self.experiments.iteritems():
            expList.append(self.getExperiment(item[0])['experiment'])
        
        return {'expList': expList}
    
    
    def close(self):
        """
        
        Method to close the HDF5 file.
        
        Kwargs:
            
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            fid.close()
        
        References:
            .. [1]
            
        """
        
        # close the file
        self.file.close()


class realTime():
    """
    
    Class to add signals in real time to an HDF5 file.
    
    Kwargs:
        
    
    Kwrvals:
        
    
    See Also:
        
    
    Notes:
        
    
    Example:
        
    
    References:
        .. [1]
        
    """
    
    def __init__(self, group, mdata, dataName, blockShape, axis, dtype, compress=False):
        """
        
        Initialize the new dataset.
        
        Kwargs:
            group (h5py.Group, h5py.File): File or group instance.
            
            mdata (dict): Dictionary object with metadata about the data.
            
            dataName (str): Name of the dataset to be created.
            
            blockShape (tuple): Shape of the signal blocks.
            
            axis (int): Direction on which the expansion of the dataset is made.
            
            dtype (str): Data type of the signal to add (supports numpy data types).
            
            compress (bool): Flag to compress the data (GZIP). Default: False.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            
        
        References:
            .. [1]
            
        """
        
        # set max shape
        mxs = list(blockShape)
        mxs[axis] = None
        mxs = tuple(mxs)
        
        # create dataset
        dset = group.create_dataset(dataName, blockShape, dtype, maxshape=mxs, compression='gzip')
        
        # set the attributes
        dset.attrs['json'] = json.dumps(mdata)
        
        # self things
        self.dset = dset
        self.shape = blockShape
        self.axis = axis
        self.first = True
    
    def put(self, data):
        """
        
        Add data.
        
        Kwargs:
            data (array): Data to add.
        
        Kwrvals:
            
        
        See Also:
            
        
        Notes:
            
        
        Example:
            
        
        References:
            .. [1]
            
        """
        
        # chech data's shape and type
        if data.shape != self.shape:
            raise ValueError, "Data is not of the expected shape."
        
        if data.dtype != self.dset.dtype:
            raise ValueError, "Data is not of the expected type."
        
        if self.first:
            # add data
            self.dset[:] = data
            self.first = False
        else:
            # resize
            size = list(self.dset.shape)
            ind = size[self.axis]
            size[self.axis] += self.shape[self.axis]
            size = tuple(size)
            self.dset.resize(size)
            
            # add data
            sel = [slice(None) for item in size]
            sel[self.axis] = slice(ind, None, None)
            sel = tuple(sel)
            self.dset[sel] = data



def IOProcess(fileConfig, acquisition, queue):
    # create new file (obtain parameters from fileConfig)
    fid = hdf('D:\\work\\Tests\\tmp.hdf5', 'w')
    try:
        fid.addInfo({'name': 'Test'})
        rt = fid.addSignalRT(signalType='/test', mdata={'name': 'test'}, dataName='signal0', blockShape=(100,))
        
        # wait for acquisition flag
        acquisition.wait(timeout=30.)
        
        while acquisition.is_set():
            while True:
                try:
                    data = queue.get(timeout=1.5)
                except Empty:
                    break
                # add data  to file
                else:
                    rt.put(data)
    except:
        raise
    finally:
        fid.close()


class IOController():
    
    def __init__(self, fileConfig):
        # instantiate multiprocessing objects
        self.acquisition = Event()
        self.queue = Queue()
        self.process = Process(target=IOProcess, args=(fileConfig, self.acquisition, self.queue))
        
        # start process
        self.process.start()
    
    def start(self):
        # start acquisition mode
        self.acquisition.set()
    
    def stop(self):
        # stop the acquisition
        self.acquisition.clear()
        # wait for process to terminate
        self.process.join()
    
    def put(self, data):
        # put data to file
        self.queue.put(data)



def latin1ToAscii (text):
    """
    This replaces UNICODE Latin-1 characters with something equivalent in 7-bit ASCII.
    Kwargs:
        text (str): Text to convert.
    
    Kwrvals:
        
    
    See Also:
        
    
    Notes:
        
    
    Example:
        text = 'Jo\xe3o'
        print text
        ntext = latin1ToAscii(text)
        print ntext
    
    References:
        .. [1] http://stackoverflow.com/questions/930303/python-string-cleanup-manipulation-accented-characters
    """
    xlate = {
             0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
             0xc6:'Ae', 0xc7:'C',
             0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
             0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
             0xd0:'Th', 0xd1:'N',
             0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
             0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
             0xdd:'Y', 0xde:'th', 0xdf:'ss',
             0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
             0xe6:'ae', 0xe7:'c',
             0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
             0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
             0xf0:'th', 0xf1:'n',
             0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
             0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
             0xfd:'y', 0xfe:'th', 0xff:'y',
             0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
             0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
             0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
             0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
             0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
             0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
             0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>',
             0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
             0xd7:'*', 0xf7:'/',
             }
    
    r = ''
    for i in text:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += i
    return r



if __name__ == '__main__':
    # Example
    import numpy as np
    import pylab as pl
    import datetime
    import time
    import os
    
    # create directory for tests
    path = os.path.abspath(os.path.expanduser('~/tmp/h5db'))
    if not os.path.exists(path):
        os.makedirs(path)
    
    # open the test record
    fid = hdf(os.path.join(path, 'rec.hdf5'), 'w')
    
    # addInfo
    header = {'name': 'rec', 'date': datetime.datetime.utcnow().isoformat(), 'experiment': 'experiment', 'subject': 'subject'}
    fid.addInfo(header)
    
    # getInfo
    header_ = fid.getInfo()['header']
    
    print "Header OK?", header == header_
    
    # addSignal
    signal = np.zeros((100, 5), dtype='float64')
    mdata = {'type': '/test', 'comments': 'zeros', 'name': 'signal'}
    signalName = 'signal'
    fid.addSignal('/test', signal, mdata, signalName)
    
    # getSignal
    res = fid.getSignal('/test', 'signal')
    signal_ = res['signal']
    mdata_ = res['mdata']
    
    print "Signal OK?"
    aux = signal == signal_
    print "  Signal: ", bool(np.prod(aux.flatten()))
    print "  Metadata: ", mdata == mdata_
    
    # delSignal
    mdata = {'type': '/test/delete', 'comments': 'zeros', 'name': 'signalD'}
    signalName = 'signalD'
    fid.addSignal('/test/delete', signal, mdata, signalName)
    fid.delSignal('/test/delete', signalName)
    
    try:
        res = fid.getSignal('/test/delete', 'signalD')
        print "Delete data OK?", False
    except Exception, e:
        print "Delete data OK?", e
    
    # delSignalType
    fid.delSignalType('/test/delete')
    
    # addEvent
    nts = 100
    timeStamps = []
    now = datetime.datetime.utcnow()
    for i in range(nts):
        instant = now + datetime.timedelta(seconds=i)
        timeStamps.append(time.mktime(instant.timetuple()))
    timeStamps = np.array(timeStamps, dtype='float')
    values = np.zeros((nts, 1), dtype='float64')
    mdata = {'type': '/test', 'comments': 'zeros', 'name': 'event'}
    eventName = 'event'
    fid.addEvent('/test', timeStamps, values, mdata, eventName)
    
    # getEvent
    res = fid.getEvent('/test', 'event')
    timeStamps_ = res['timeStamps']
    values_ = res['values']
    mdata_ = res['mdata']
    
    print "Events OK?"
    aux = timeStamps == timeStamps_
    print "  Timestamps: ", bool(np.prod(aux.flatten()))
    aux = values == values_
    print "  Values: ", bool(np.prod(aux.flatten()))
    print "  Metadata: ", mdata == mdata_
    
    # delEvent
    mdata = {'type': '/test/delete', 'comments': 'zeros', 'name': 'eventD'}
    eventName = 'eventD'
    fid.addEvent('/test/delete', timeStamps, values, mdata, eventName)
    fid.delEvent('/test/delete', eventName)
    
    try:
        res = fid.getEvent('/test', 'eventD')
        print "Delete event OK?", False
    except Exception, e:
        print "Delete event OK?", e
    
    # delEventType
    fid.delEventType('/test/delete')
    
    # close
    fid.close()
    
    
    # open the test metafile
    fid = meta(os.path.join(path, 'ExpSub.hdf5'), 'w')
    
    # addSubject
    subject = {'name': 'subject', '_id': 0}
    fid.addSubject(subject)
    
    # getSubject
    subject_ = fid.getSubject(0)['subject']
    
    print "Subject OK?", subject == subject_
    
    # updateSubject
    fid.updateSubject(0, {'new': 'field'})
    subject_ = fid.getSubject(0)['subject']
    
    print "Updade subject OK?", subject_['new'] == 'field'
    
    # listSubjects
    res = fid.listSubjects()
    
    print "List subjects OK?", res['subList']
    
    # addExperiment
    experiment = {'name': 'experiment', '_id': 0}
    fid.addExperiment(experiment)
    
    # getExperiment
    experiment_ = fid.getExperiment('experiment')['experiment']
    
    print "Experiment OK?", experiment == experiment_
    
    # updateSubject
    fid.updateExperiment('experiment', {'new': 'field'})
    experiment_ = fid.getExperiment('experiment')['experiment']
    
    print "Updade experiment OK?", experiment_['new'] == 'field'
    
    # listSubjects
    res = fid.listExperiments()
    
    print "List experiments OK?", res['expList']
    
    # close
    fid.close()
    
    
    ##############################
    # Example for IOController
    fileConfig = {}
    
    # start controller
    print "Starting Controller"
    fileIO = IOController(fileConfig)
    
    # start acquisition
    print "Starting acquisition"
    fileIO.start()
    
    # add data
    for i in xrange(10):
        print "Adding data", i
        fileIO.put(i * np.ones(100, dtype='f'))
        time.sleep(3.)
    
    # stop acquisition and controller
    print "Stopping acquisition"
    fileIO.stop()
    print "Acquisition stopped"
    
    # read from file
    fid = hdf('D:\\work\\Tests\\tmp.hdf5')
    out = fid.getSignal('/test', 'signal0')
    pl.plot(out['signal'])
    pl.show()
    fid.close()
    
    print "Remove file"    
    os.remove('D:\\work\\Tests\\tmp.hdf5')
    
