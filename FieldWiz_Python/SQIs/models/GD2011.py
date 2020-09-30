from .. import utils
def GD2011(signal, r_peaks, sampling_rate=1000.0, high_pass_fc=1, flatline_threshold = 0.01):
    """Signal quality estimator. Designed for signal with a lenght of 10 seconds
    Follows the approach by Hayn *et la.* [Clifford11]_.

    Parameters
    ----------
    signal : array
        Input ECG signal in mV.
    r_peaks : array
        Output of 2 QRS detectors.
    sampling_rate : int, float, optional
        Sampling frequency (Hz).
    high_pass_fs : int, optional
        Cut-off frequency for the high-pass filter, in Hz.
    flatline_threshold : float, optional
        Threshold for the flatline condition, in mV / samples.

    Returns
    -------
    SQI_features : array
        Returns an array of featues to be feed into a classifier.

    References
    ----------
    .. [Clifford11] Clifford, G. D., Lopez, D., Li, Q., & Rezek, I. (2011, September). 
       Signal quality indices and data fusion for determining acceptability of electrocardiograms collected in noisy ambulatory environments. 
       In Computing in Cardiology, 2011 (pp. 285-288). IEEE.
    """

    if(signal is None):
        raise TypeError("Please specify an input signal")
    
    #High pass filter
    from scipy import signal
    b, a = signal.butter(6, high_pass_fc, 'high', analog=True)
    filtered_signal = signal.filtfilt(b, a, signal)
    
    bSQI = utils.bSQI(r_peaks[0], r_peaks[1])
    fSQI = utils.fSQI(signal)
    sSQI = utils.sSQI(signal)
    kSQI = utils.kSQI(signal)
    pSQI = utils.pSQI(signal, f_thr=flatline_threshold)

    return [bSQI, fSQI, sSQI, kSQI, pSQI]


