function [LFln,HFln,LFHF,hrmean,sdnn,rmssd,lnrmssd,rr_intervals,rr_time] = HRV_realtimesession(rpeaksposition,fs)
%% Description
%{
Real Time HRV metrics
Time-Domain: hrmean (bpm),SDNN (ms), RMSSD (ms), LnRMSSD
Frequency Domain: LF, HF and LF/HF, power of the frequency bands
%}


%% Inputs
%{
rpeaksposition: last R-peak position
fs: sampling frequency (e.g 250 Hz)
%}

    persistent lastrpeakpositions
    
    if 


outputArg1 = inputArg1;
outputArg2 = inputArg2;
end

