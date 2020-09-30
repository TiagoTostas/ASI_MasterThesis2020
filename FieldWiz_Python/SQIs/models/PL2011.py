from .. import utils
def PL2011(signal, fs=1000.0, fl_duration=1.0, fl_thr=0.01, sa_duration=0.2, sa_thr=2.0, bs_thr=2.5, la_thr=0.125, ha_thr=3.75, tpm_thr=0.250, pm_window=[80, 100], hf_noise=1):
    """Signal quality estimator. Designed for signal with a lenght of 10 seconds
    Follows the approach by Langley *et la.* [Langley11]_.

    Parameters
    ----------
    signal : array
        Input ECG signal in mV.
    fs : int, float, optional
        Sampling frequency (Hz).
    fl_duration : float, optional
        Duration of flatline threshold, in s.
    fl_thr : float, optional
        Flatline threshold, in mV/sample.
    sa_duration : float, optional
        Duration of the saturation threshold, in s.
    sa_thr : float, optional
        Saturation threshold, in mV/sample.
    bs_thr : float, optional
        Maximum amplitude threshold, in mV/sample.
    la_thr : float, optional
        Maximum amplitude threshold, in mV/sample.
    ha_thr : float, optional
        Maximum amplitude threshold, in mV/sample.
    tpm_thr : float, optional
        Pacemaker threshold, in micro volts/sample.
    pm_window : float, optional
        Pacemaker window trimmer, in ms.
    hf_noise: int, optional
        High frequency noise threshold, in mV/sample.


    Returns
    -------
    noise : boolean
        Quality classification.

    References
    ----------
    .. [Langley11] Langley, P., Di Marco, L. Y., King, S., Duncan, D., Di Maria, C., Duan, W., ... & Murray, A. (2011, September). 
    "An algorithm for assessment of quality of ECGs acquired via mobile telephones."
    In Computing in Cardiology, 2011 (pp. 281-284). IEEE.
    """

    if(signal is None):
        raise TypeError("Please specify an input signal")

    if(utils.FB(signal, fs=fs, duration=fl_duration, fl_thr=fl_thr)):
        if(utils.SA(signal, fs=fs, duration=sa_duration, sa_thr=sa_thr)):
            from scipy.signal import butter, lfilter
            b, a = butter(6, 1.0/(int(fs/2)), 'low', analog=False)
            baseline = lfilter(b, a, signal)
            if(utils.BD(baseline, bs_thr=bs_thr)):
                filtered = signal-baseline
                if(utils.LA(filtered, la_thr=la_thr)):
                    if(utils.HA(filtered, ha_thr=ha_thr)):
                        if(utils.SteepSlope(signal, fs=fs, tpm_thr=tpm_thr, pm_window=pm_window, hf_noise=hf_noise)):
                            return False
    return True
