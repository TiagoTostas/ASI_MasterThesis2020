from .. import utils
def ZZ2018(signal, detector_1, detector_2, fs=1000.0, search_window=100, nseg=1024, mode='simple'):
    """ Signal quality estimator. Designed for signal with a lenght of 10 seconds.
        Follows the approach by Zhao *et la.* [Zhao18]_.
            
    Parameters
    ----------
    signal : array
        Input ECG signal in mV.
    detector_1 : array
        Input of the first R peak detector.
    detector_2 : array
        Input of the second R peak detector.
    fs : int, float, optional
        Sampling frequency (Hz).
    search_window : int, optional
        Search window around each peak, in ms.
    nseg : int, optional
        Frequency axis resolution.
    mode : str, optional
        If 'simple', simple heurisitc. If 'fuzzy', employ a fuzzy classifier.
        
    Returns
    -------
    noise : str
        Quality classification.
       
    References
    ----------
    .. [Zhao18] Zhao, Z., & Zhang, Y. (2018). 
    SQI quality evaluation mechanism of single-lead ECG signal based on simple heuristic fusion and fuzzy comprehensive evaluation. 
    Frontiers in Physiology, 9, 727.
    """
    
    
    if(len(detector_1) == 0 or len(detector_2) == 0):
        return 'Unacceptable'
    ## Feature extraction
    qSQI = utils.bSQI(detector_1, detector_2, fs=fs, mode='matching', search_window=search_window)
    pSQI = utils.fSQI(signal, fs=fs, nseg=nseg, num_spectrum=[5, 15], dem_spectrum=[5, 40])
    cSQI = utils.cSQI(detector_1)
    sSQI = utils.sSQI(signal)
    kSQI = utils.kSQI(signal)
    basSQI = utils.fSQI(signal, fs=fs, nseg=nseg, num_spectrum=[0, 1], dem_spectrum=[0, 40], mode='bas')
    if(mode=='simple'):
        ## First stage rules (0 = unqualified, 1 = suspicious, 2 = optimal)
        ## qSQI rules  
        if(qSQI > 0.90):
            qSQI_class = 2
        elif(qSQI < 0.60):
            qSQI_class = 0
        else:
            qSQI_class = 1
    
        ## pSQI rules  
        import numpy as np
    
        ## Get the maximum bpm
        if(len(detector_1) > 1):
            RR_max = 60000.0/(1000.0/fs * np.min(np.diff(detector_1)))
        else:
            RR_max = 1

        if(RR_max < 130):
            l1, l2, l3 = 0.5, 0.8, 0.4
        else:
            l1, l2, l3 = 0.4, 0.7, 0.3

        if(pSQI > l1 and pSQI < l2):
            pSQI_class = 2
        elif(pSQI > l3 and pSQI < l1):
            pSQI_class = 1
        else:
            pSQI_class = 0

        ## kSQI rules  
        if(kSQI > 5):
            kSQI_class = 2
        else:
            kSQI_class = 0
        
        ## basSQI rules  
        if(basSQI >= 0.95):
            basSQI_class = 2
        elif(basSQI < 0.9):
           basSQI_class = 0
        else:
            basSQI_class = 1


        class_matrix = np.array([qSQI_class, pSQI_class, kSQI_class, basSQI_class])
        n_optimal = len(np.where(class_matrix == 2)[0])
        n_suspics = len(np.where(class_matrix == 1)[0])
        n_unqualy = len(np.where(class_matrix == 0)[0])
        if(n_unqualy >= 3 or (n_unqualy == 2 and n_suspics >= 1) or (n_unqualy == 1 and n_suspics == 3)):
            return 'Unacceptable'
        elif(n_optimal >= 3 and n_unqualy == 0):
            return 'Excellent'
        else:
            return 'Barely acceptable'

    elif(mode=='fuzzy'):
        import numpy as np
        ## Membership functions
        ### qSQI
        ### Transform qSQI range from [0, 1] to [0, 100]
        qSQI = qSQI * 100.0
        #### UqH (Excellent)
        if(qSQI <= 80):
            UqH = 0
        elif(qSQI >= 90):
            UqH = qSQI/100.0
        else:
            UqH = 1.0 / (1+(1/np.power(0.3*(qSQI-80),2)))

        #### UqI (Barely acceptable)
        UqI = 1.0 / (1+np.power((qSQI-75)/7.5, 2))

        #### UqJ (unacceptable)
        if(qSQI <= 55):
            UqJ = 1
        else:
            UqJ = 1.0 / (1+np.power((qSQI-55)/5.0, 2))

        #### Get R1
        R1 = np.array([UqH, UqI, UqJ])

        ### pSQI
        #### UpH
        if(pSQI <= 0.25):
            UpH = 0
        elif(pSQI >= 0.35):
            UpH = 1
        else:
            UpH = 0.1 * (pSQI-0.25)
        
        #### UpI
        if(pSQI < 0.18):
            UpI = 0
        elif(pSQI >= 0.32):
            UpI = 0
        elif(pSQI >= 0.18 and pSQI < 0.22):
            UpI = 25 * (pSQI-0.18)
        elif(pSQI >= 0.22 and pSQI < 0.28):
            UpI = 1
        else:
            UpI = 25 * (0.32-pSQI)
        
        #### UpJ
        if(pSQI < 0.15):
            UpJ = 1
        elif(pSQI > 0.25):
            UpJ = 0
        else:
            UpJ = 0.1 * (0.25-pSQI)

        #### Get R2
        R2 = np.array([UpH, UpI, UpJ])
        
        ### kSQI
        #### Get R3

        if(kSQI > 5):
            R3 = np.array([1, 0, 0])
        else:
            R3 = np.array([0, 0, 1])

        ### basSQI  
        #### UbH 
        if(basSQI <= 90):
            UbH = 0
        elif(basSQI >= 95):
            UbH = basSQI/100.0
        else:
            UbH = 1.0 / (1+(1/np.power(0.8718*(basSQI-90),2)))

        #### UbI
        if(basSQI <= 85):
            UbI = 1
        else:
            UbI = 1.0 / (1+np.power((basSQI-85)/5.0, 2))
        
        #### UbJ 
        UbJ = 1.0 / (1+np.power((basSQI-95)/2.5, 2))

        #### R4

        R4 = np.array([UbH, UbI, UbJ])

        ### Make R
        R = np.vstack([R1, R2, R3, R4])

        ### Weight Vector

        W = np.array([0.4, 0.4, 0.1, 0.1])

        ### Get S vector
        
        S = np.array([np.sum((R[:, 0]*W)), np.sum((R[:, 1]*W)), np.sum((R[:, 2]*W))])

        ### Classify

        V = np.sum(np.power(S, 2) * [1, 2, 3]) / np.sum(np.power(S, 2))

        if(V < 1.5):
            return 'Excellent'
        elif(V >= 2.40):
            return 'Unnacceptable'
        else:
            return 'Barely acceptable'
