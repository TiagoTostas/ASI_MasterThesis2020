import numpy as np
from .. import utils

def CL2011(signal, detector_1, fs=1000.0, N_seg1=5, r_line=1, Nline_thr=2, N_seg2=10, r_impulse=1000, Nimpulse_thr=1, nseg=512, num_spectrum=[0.05, 40], SFNF_thr=1.5, sampem_thr=0.7, NNoise_thr=3, IRF_thr=2, Nirf_thr=1):

    
    # check inputs
    if signal is None:
        raise TypeError("Please specify an input signal.")
    
    seg_indexes = int(len(signal)/N_seg1)
    Nline = 0
    for i in range(0, len(signal), seg_indexes):
        crt_seg = signal[i:min([len(signal),i+seg_indexes])]
        d_crt_seg = np.diff(crt_seg)
        sd_crt_seg = np.std(d_crt_seg)
        Nline += (sd_crt_seg<=r_line)
    
    flag1 = (Nline >= Nline_thr)
    
    seg_indexes = int(len(signal)/N_seg2)
    Nimpulse = 0
    Nnoise = 0
    for i in range(0, len(signal), seg_indexes):
        crt_seg = signal[i:min([len(signal),i+seg_indexes])]
        if(max(crt_seg) > r_impulse):
            Nimpulse += 1
            signal[i:min([len(signal),i+seg_indexes])] = np.mean(signal) 
        
        SF_NF = utils.fSQI(signal[i:min([len(signal),i+seg_indexes])], fs=fs, nseg=nseg, num_spectrum=num_spectrum, dem_spectrum=[num_spectrum[1], int(fs/2)], mode='simple')
        sampem = utils.sample_entropy(signal)
        if(sampem[0] < sampem_thr and SF_NF < SFNF_thr):
            Nnoise += 1

    flag2 = (Nimpulse >= Nimpulse_thr)
    flag3 = (Nnoise >= 3)
    
    D = utils.impulseRejectionFilter(detector_1)
    Nirf = len(np.where(D>=IRF_thr)[0])
    flag4 = (Nirf >= Nirf_thr)
    
    SSQI = 1-flag1-0.2*(flag2+2*flag3+flag4)-0.05*(Nimpulse+Nnoise+Nirf)
    return SSQI

