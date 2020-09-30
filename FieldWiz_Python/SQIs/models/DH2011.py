def DH2011(signal, sampling_rate=1000.0, skipped_segment=800, threshold_1 = 2.0, threshold_2 = 0.2, threshold_3 = 0.01):
    """Signal quality estimator. Designed for signal with a lenght of 10 seconds
    Follows the approach by Hayn *et la.* [Hayn11]_.
    
    Parameters
    ----------
    signal : array
        Input ECG signal in mV.
    sampling_rate : int, float, optional
        Sampling frequency (Hz).
    skipped_segment : int, optional
        Skip delay (ms).
    threshold_1 : int, float, optional
        Saturation threshold (mV).
    threshold_2 : int, float, optional
        Derivative threshold (mV / sample).
    threshold_3 : int, float, optional
        Flatline threshold (mV / sample).
    
    Returns
    -------
    noise : boolean
        Quality classification.
    
    References
    ----------
    .. [Hayn11] Hayn, Dieter, Bernhard Jammerbund, and Günter Schreier. 
    "ECG quality assessment for patient empowerment in mHealth applications." 
    Computing in Cardiology, 2011. IEEE, 2011.
    """
    
    # check inputs
    if signal is None:
        raise TypeError("Please specify an input signal.")
    
    # skip initial ms to discard any transient components
    starting_index = int(skipped_segment/sampling_rate)
    signal = signal[starting_index:]
    length = len(signal)

    # Criterion thresholds and flag_counters
    CA1 = int(length * 0.4)
    CA2 = int(length * 0.4)
    CA3 = int(length * 0.8)
    CA4 = int(length * 0.685)

    counter_A1 = 0
    counter_A2 = 0
    counter_A3 = 0
    counter_A4 = 0
    
    # Crtiriums A1-A4

    for i in range(1, length):
        crt_sample = signal[i]
        delta = crt_sample - signal[i-1]
        
        flag_A4 = False # If any conditions is triggered then increase counter_A4
        
        # Criteriums A1 - A3
        if(abs(crt_sample) > threshold_1):
            counter_A1 += 1
            if(counter_A1 >= CA1):
                return True
            flag_A4 = True

        if(abs(delta) > threshold_2):
            counter_A2 += 1
            if(counter_A2 >= CA2):
                return True
            flag_A4 = True

        if(abs(delta) < threshold_3):
            counter_A3 += 1
            if(counter_A3 >= CA3):
                return True
            flag_A4 = True
        
        # Critirium A4
        if(flag_A4):
            counter_A4 += 1
            if(counter_A4 >= CA4):
                return True
    
    return False
