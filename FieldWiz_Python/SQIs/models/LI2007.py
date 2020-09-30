import numpy as np
from .. import utils

def LI2007(signal, detector_1, detector_2, fs=1000.0, window_size=10, search_window=150, nseg=1024, num_spectrum=[5, 14], dem_spectrum=[5, 50], bmode='n_double', fmode='simple', n=0.7):
    '''
    Implements a signal quality metric by Li, et al [LI07]

    Parameters
    ----------
    '''

    window_index = int(fs*search_window)
    
    quality = []
    bSQI = []
    kSQI = []
    sSQI = []

    for i in detector_1:
        start = max([0, i-int(window_index/2)])
        end = min([len(signal), i+int(window_index/2)])
        
        crt_segment = signal[start:end]
        beats_1 = np.where((detector_1 > start) & (detector_1 < end))[0]
        beats_2 = np.where((detector_2 > start) & (detector_2 < end))[0]
        
        _bSQI=utils.bSQI(beats_1, beats_2, fs=fs, mode=bmode, search_window=search_window)
        
        _kSQI=(0, 1)[utils.kSQI(crt_segment)>5]
        
        _SDR=utils.fSQI(crt_segment, fs=fs, nseg=nseg, num_spectrum=num_spectrum, dem_spectrum=dem_spectrum, mode=fmode)
        
        if(_SDR >= 0.5 and _SDR <= 0.8):
            _sSQI = 1
        else:
            _sSQI = 0
        
        bSQI.append(_bSQI)
        kSQI.append(_kSQI)
        sSQI.append(_sSQI)

        if(_kSQI == 1):
            quality.append(_bSQI)
        else:
            quality.append(_bSQI*n)

    return quality, bSQI, kSQI, sSQI
