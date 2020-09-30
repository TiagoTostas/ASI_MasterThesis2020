def bSQI(detector_1, detector_2, fs=1000., mode='simple', search_window=150):
    """ Comparison of the output of two detectors.

    Parameters
    ----------
    detector_1 : array
        Output of the first detector.
    detector_2 : array
        Output of the second detector.
    fs: int, optional
        Sampling rate, in Hz.
    mode : str, optional
        If 'simple', return only the percentage of beats detected by both. If 'matching', return the peak matching degree. If 'n_double' returns the number of matches divided by the sum of all minus the matches.
    search_window : int, optional
        Search window around each peak, in ms.

    Returns
    -------
    bSQI : float
        Performance of both detectors.

   """

    if(detector_1 is None or detector_2 is None):
        raise TypeError("Input Error, check detectors outputs")
    search_window = int(search_window/1000 * fs)
    both = 0
    for i in detector_1:
        for j in range(max([0, i-search_window]), i+search_window):
            if(j in detector_2):
                both+=1
                break

    if(mode == 'simple'):
        return (both/len(detector_1))*100
    elif(mode == 'matching'):
        return (2*both)/(len(detector_1)+len(detector_2))
    elif(mode == 'n_double'):
        return (both/(len(detector_1)+len(detector_2)-both))
        

def sSQI(signal):
    """ Return the skewness of the signal

    Parameters
    ----------
    signal : array
        ECG signal.

    Returns
    -------
    skewness : float
        Skewness value.

    """
    if(signal is None):
        raise TypeError("Please specify an input signal")
    
    import scipy

    return scipy.stats.skew(signal)


def kSQI(signal, fisher=True):
    """ Return the kurtosis of the signal

    Parameters
    ----------
    signal : array
        ECG signal.
    fisher : bool, optional
        If True,Fisher’s definition is used (normal ==> 0.0). If False, Pearson’s definition is used (normal ==> 3.0).

    Returns
    -------
    kurtosis : float
        Kurtosis value.
    """

    if(signal is None):
        raise TypeError("Please specify an input signal")
    
    import scipy

    return scipy.stats.kurtosis(signal, fisher=fisher)


def pSQI(signal, f_thr=0.01):
    """ Return the flatline percentage of the signal

    Parameters
    ----------
    signal : array
        ECG signal.
    f_thr : float, optional
        Flatline threshold, in mV / sample

    Returns
    -------
    flatline_percentage : float
        Percentage of signal where the absolute value of the derivative is lower then the threshold.

    """

    if(signal is None):
        raise TypeError("Please specify an input signal")
    
    import numpy
    
    diff = np.diff(signal)
    lenght = len(diff)
    
    flatline = np.where(abs(diff) < f_thr)[0]

    return (len(flatline)/lenght) * 100


def fSQI(ecg_signal, fs=1000.0, nseg=1024, num_spectrum=[5, 20], dem_spectrum=None, mode='simple'):
    """ Returns the ration between two frequency power bands.

    Parameters
    ----------
    ecg_signal : array
        ECG signal.
    fs : float, optional
        ECG sampling frequency, in Hz.
    nseg : int, optional
        Frequency axis resolution.
    num_spectrum : array, optional
        Frequency bandwidth for the ratio's numerator, in Hz.
    dem_spectrum : array, optional
        Frequency bandwidth for the ratio's denominator, in Hz. If None, then the whole spectrum is used.
    mode : str, optional
        If 'simple' just do the ration, if is 'bas', then do 1 - num_power.

    Returns
    -------
    Ratio : float
        Ratio between two powerbands.  
    """


    def power_in_range(f_range, f, Pxx_den):
        _indexes = np.where((f>=f_range[0]) & (f<=f_range[1]))[0]
        _power = integrate.trapz(Pxx_den[_indexes], f[_indexes])
        return _power


    if(ecg_signal is None):
        raise TypeError("Please specify an input signal")
    
    from scipy import signal, integrate
    import numpy as np

    f, Pxx_den = signal.welch(ecg_signal, fs, nperseg=nseg)
    num_power = power_in_range(num_spectrum, f, Pxx_den)
    
    if(dem_spectrum is None):
        dem_power = power_in_range([0, float(fs/2.0)], f, Pxx_den)
    else:
        dem_power = power_in_range(dem_spectrum, f, Pxx_den)
    
    if(mode=='simple'):
        return num_power/dem_power
    elif(mode=='bas'):
        return 1 - num_power/dem_power


## ZZ2018
def cSQI(detector):
    """ Variability in the HR.

    Parameters
    ----------
    detector : array
        Output of the R peak detector.
    
    Returns
    -------
    cSQI: float
        Variability in the HR
    """

    if(detector is None):
        raise TypeError("Please specify an input signal")

    import numpy as np

    RR = np.diff(detector)
    
    return np.std(RR)/np.mean(RR)

###### PL2011
def FB(signal, fs=1000.0, duration=1.0, fl_thr=0.01):
    """ Returns the presence of flatline segments of at least a pre-determined duration.

    Parameters
    ----------
    ecg_signal : array
        ECG signal, in mV.
    fs : float, optional
        ECG sampling frequency, in Hz.
    duration : float, optional
        Duration of flatline threshold, in s.
    fl_thr : float, optional
        Flatline threshold, in mV/sample.

    Returns
    -------
    Flatline : bool
        Presence of a flatline of a pre-determined duration.
        True equals a clean signal, False indicates a presence of a flatline.
    """

    if(signal is None):
        raise TypeError("Please specify an input signal")

    import numpy as np
    
    signal_diff = np.diff(signal)
    time_threshold = int(fs*duration)
    
    count = 0
    for i in signal_diff:
        if(i < fl_thr):
            count+=1
            if(count >= time_threshold):
                return False
        else:
            count=0
    
    return True


def SA(signal, fs=1000.0, duration=0.2, sa_thr=2.0):
    """ Returns the presence of a saturation segments of at least a pre-determined duration.

    Parameters
    ----------
    ecg_signal : array
        ECG signal.
    fs : float, optional
        ECG sampling frequency, in Hz.
    duration : float, optional
        Duration of the saturation threshold, in s.
    sa_thr : float, optional
        Saturation threshold, in mV/sample.

    Returns
    -------
    Saturation : bool
        Presence of saturation for a pre-determined duration.
        True equals a clean signal, False indicates a presence of saturation.
    """

    if(signal is None):
        raise TypeError("Please specify an input signal")

    import numpy as np
    
    time_threshold = int(fs*duration)
    
    count = 0
    for i in signal:
        if(i > sa_thr):
            count+=1
            if(count >= time_threshold):
                return False
        else:
            count=0
    
    return True


def BD(baseline, bs_thr=2.5):
    """ Returns the presence of baseline drift.

    Parameters
    ----------
    baseline : array
        Baseline signal (excluding the first two seconds).
    bs_thr : float, optional
        Maximum amplitude threshold, in mV/sample.

    Returns
    -------
    BaselineDrift : bool
        Presence of baseline drift.
        True equals a clean signal, False indicates a baseline drift.
    """

    if(baseline is None):
        raise TypeError("Please specify an input signal")
    if(max(baseline) > bs_thr):
        return False
    else:
        return True


def LA(filtered_signal, la_thr=0.125):
    """ Returns the presence of low amplitude signals.

    Parameters
    ----------
    filtered_signal : array
        ECG signal with the baseline removed.
    la_thr : float, optional
        Maximum amplitude threshold, in mV/sample.

    Returns
    -------
    LowAmplitude : bool
        Presence of low amplitude signals.
        True equals a clean signal, False indicates a low amplitude.
    """

    if(filtered_signal is None):
        raise TypeError("Please specify an input signal")
    if(max(filtered_signal) < la_thr):
        return False
    else:
        return True
    

def HA(filtered_signal, ha_thr=3.75):
    """ Returns the presence of high amplitude signals.

    Parameters
    ----------
    filtered_signal : array
        ECG signal with the baseline removed.
    ha_thr : float, optional
        Maximum amplitude threshold, in mV/sample.

    Returns
    -------
    HighAmplitude : bool
        Presence of high amplitude signals.
        True equals a clean signal, False indicates a high amplitude.
    """

    if(filtered_signal is None):
        raise TypeError("Please specify an input signal")
    
    if(max(filtered_signal) > ha_thr):
        return False
    else:
        return True


def SteepSlope(signal, fs=1000.0, tpm_thr=0.250, pm_window=[80, 100], hf_noise=1):

    """ Mitigates against the presence of pacemakers.

    Parameters
    ----------
    signal : array
        ECG signal.
    fs : float, optional
        Sampling rate, in Hz.
    tpm_thr : float, optional
        Pacemaker threshold, in micro volts/sample.
    pm_window : float, optional
        Pacemaker window trimmer, in ms.
    hf_noise: int, optional
        High frequency noise threshold, in mV/sample.

    Returns
    -------
    Pacemaker : bool
        Presence of pacemaker noise.
        True equals a clean signal, False indicates contamination.
    """

    if(signal is None):
        raise TypeError("Please specify an input signal")
    
    import numpy as np
    
    sig_diff = np.diff(signal)
    
    pm_window = [int(pm_window[0]/1000.0*fs), int(pm_window[1]/1000.0*fs)]

    for i in range(0, len(sig_diff)):
        if(i > tpm_thr):
            signal[max([0, i-pm_window[0]]):min([len(signal)-1, i+pm_window[1]])] = signal[max([0, i-pm_window[1]])]

    sig_diff = np.diff(signal)

    if(max(sig_diff) > hf_noise):
        return False
    else:
        return True

## ES2014

def HardSat(signal, ADC=12):
    """ Hard Threshold 

    Parameters
    ----------
    signal : array
        ECG signal.
    ADC : int, optional
        Resolution of the ADC, in bits.
    
    Returns
    -------
    Percentage : float
        Percentage of signal either saturated of flatlined
    """

    if(signal is None):
        raise TypeError("Please specify an input signal")

    import numpy as np

    high_thr = np.power(2, ADC)

    F1 = len(np.where(signal == high_thr)[0]) + len(np.where(signal == 0)[0])

    F1 = F1/len(signal)

    return F1


def meanECGAmplitude(signal, fs=1000.0, big_window=1, window_size=2, mean_thr=0.2):
    ''' Get mean amplitude from non-overlapping ECG windows of 2 seconds each

    Parameters
    ----------
    signal : array
        ECG signal.
    fs : int, float, optional
        Sampling rate, in Hz.
    big_size : int, float, optional
        Size of the non-overlapping windows, in minutes.
    window_size : int, float, optional
        Size of the non-overlapping windows, in seconds.
    thr : float, optional
        Decision threshold.

    Returns
    -------
    F2 : float
        Percentage of signal with a mean value higher than a threshold

   '''
    if(signal is None):
        raise TypeError("Please specify an input signal")
    
    big_index = int(fs*(big_window*60))
    index = int(fs*window_size)
    F2 = []
    for j in range(0, len(signal), big_index):
        segment = signal[i:np.min([len(signal), j+big_index])]
        scalling_para = []
        
        for i in range(0, len(segment), index):
            crt_segment = segment[i, np.min([i+index, len(segment)])]
            scalling_para.append(max(crt_segment))
        
        signal_mean = np.mean(segment)
        scalling_para = np.median(scalling_para)
        F2.append((0, 1)[signal_mean/scalling_para > mean_thr])
        
    return np.sum(F2)/len(F2)


def sigPeaks(signal, fs=1000.0, big_window=1, peaks_thr=2000):
    ''' Get the number of significant peaks in the signal

    Parameters
    ----------
    signal : array
        ECG signal.
    fs : int, float, optional
        Sampling rate, in Hz.
    big_window : int, float, optional
        Size of the non-overlapping windows, in minutes.
    thr : float, optional
        Decision threshold.

    Returns
    -------
    F3 : float
        Percentage of signal with a mean value higher than a threshold

   '''
    if(signal is None):
        raise TypeError("Please specify an input signal")
    
    big_index = int(fs*(big_window*60))
    F3 = []
    for j in range(0, len(signal), big_index):
        segment = signal[i:np.min([len(signal), j+big_index])]
        s_peaks = 0
        for i in range(3, len(segment)-3):
            if(i == np.max(segment[i-3:i+3])):
                s_peaks += 1

        F3.append((0,1)[s_peaks>peaks_thr])

    return np.sum(F3)/len(F3)


## CL2011

def sample_entropy(signal, sample_length=None, tolerance=None):
    '''
    Calculation of the sample entropy of a m lenght time series, using
    the chebychev norm.
    Based on the implementation of [1].

    Parameters
    ----------
    signal: array
        Time series to be analysed.
    sample_length: int, optional
        Length of the longest template vector.
    tolerance: float, optional
        Tolerance

    Returns
    -------
    sampen: array
        Sample entropy at different template size.

    Reference
    ---------
    [1] https://github.com/nikdon/pyEntropy/blob/master/pyentrp/entropy.py
    '''
    import numpy as np
    if sample_length is None:
        sample_length = 2

    M = sample_length -1
    time_series = np.array(signal)
    if tolerance is None:
        tolerance = 0.1*np.std(time_series)

    n = len(time_series)

    #Ntemp is a vector that holds the number of matches. N[k] holds matches templates of length k
    Ntemp = np.zeros(M + 2)
    #Templates of length 0 matches by definition:
    Ntemp[0] = n*(n - 1) / 2

    for i in range(n - M - 1):
        template = time_series[i:(i+M+1)];#We have 'M+1' elements in the template
        rem_time_series = time_series[i+1:]

        searchlist = np.nonzero(np.abs(rem_time_series - template[0]) < tolerance)[0]

        go = len(searchlist) > 0;

        length = 1;

        Ntemp[length] += len(searchlist)

        while go:
            length += 1
            nextindxlist = searchlist + 1;
            nextindxlist = nextindxlist[nextindxlist < n - 1 - i]#Remove candidates too close to the end
            nextcandidates = rem_time_series[nextindxlist]
            hitlist = np.abs(nextcandidates - template[length-1]) < tolerance
            searchlist = nextindxlist[hitlist]

            Ntemp[length] += np.sum(hitlist)

            go = any(hitlist) and length < M + 1

    sampen =  - np.log(Ntemp[1:] / Ntemp[:-1])
    return sampen


def impulseRejectionFilter(RR):
    '''
    Impulse rejection filter

    Parameters
    ----------
    RR: array
        Array containing the RR intervals.

    Return
    ------
    D: array
        Output of the impulse rejection filter.

    '''

    import numpy as np

    med = np.median(RR)
    den = abs(RR-med)
    med2 = np.median(den)
    
    D = den/(1.483*med2)

    return D
