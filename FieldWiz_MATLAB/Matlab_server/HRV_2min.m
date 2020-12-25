function [LF,HF,LFHF,hrmean,sdnn,rmssd,lnrmssd,rr_intervals,rr_time] = HRV_2min(rpeaks_positions,fs)
%% Description
%{
HRV Metrics
Time-Domain: hrmean (bpm),SDNN (ms), RMSSD (ms), LnRMSSD
Frequency Domain: LF, HF and LF/HF, power of the frequency bands
%}
   
%% Inputs
%{
rpeaks_positions: vector containing R-peak positions from the recorded session
fs: sampling frequency (e.g. 250 Hz)
%}

%% Outputs
%{
rr_intervals (ms) and its timestamps (seconds)

Time-Domain:
SDNN, standard deviation of RR intervals (ms)
RMSSD, root mean square of successive RR interval differences (ms)
LnRMSSD 

Frequency Domain: 
LF, bandpower [0.04 0.15]Hz (ms^2)
HF, bandpower [0.15 0.4]Hz (ms^2)
LF/HF (estimation for the session)
%}

%% Pre-processing data
% compute sequence of RR intervals (in ms)
rr_sequence = 1000 * (diff(rpeaks_positions)./fs); 

% rr-intervals artefact correction
% remove rr-intervals that meet |rr-medrr|/medrr > 20%
rrmedian = movmedian(rr_sequence,11);
rr_corrected = rr_sequence;
rr_corrected((abs(rr_sequence-rrmedian)./rrmedian) > 0.2) = nan;

% interpolate missing data with spline 
rr_intervals = fillmissing(rr_corrected,'spline');

% rr-intervals sucessive differences for hrv
rr_intervalsdiff =  diff(rr_intervals);

% rr-intervals time vector
rr_time = rpeaks_positions./fs;
rr_time = rr_time(1:end-1) - rr_time(1); %start timestamps from 0s

% resampling rr-Intervals at 7Hz for frequency domain features
targetSampleRate = 7;
[rr_intervalsr, rr_timer] = resample(rr_intervals,rr_time,targetSampleRate,'spline');


%% Time-domain
% discard first n seconds of ecg data (transient):
t_discard = 30;
td_start = find(rr_time > t_discard, 1);

% moving window to compute the time-domain features over a window of "time domain_window" number of beats
timedomain_window = 60;

% mean heart rate
hrmean = 60/(mean(rr_intervals(td_start:end)/1000));

sdnn_vector = zeros(1, length(rr_intervals)-1);
rmssd_vector = zeros(1, length(rr_intervals)-1);

for i = td_start + timedomain_window  : length(rr_intervalsdiff)
    window = rr_intervalsdiff(i - timedomain_window +1 : i);
   
    sdnn_vector(i) = std(window);  
    dist_square = sum(diff(window).^2);
    rmssd_vector(i) = sqrt(dist_square/length(window));
end

% mean of the session (over the computed time windows)
sdnn = mean(sdnn_vector(sdnn_vector~=0));
rmssd = mean(rmssd_vector(rmssd_vector~=0));
lnrmssd = log(rmssd);

%% Frequency-domain
% discard first 30 sec of ecg data (ecg transient):
tf_start = find(rr_timer > 30, 1);
rr_intervalsr = rr_intervalsr(tf_start:end);

% extract LF (low frequency) and HF (high frequency) power
LF = bandpower(rr_intervalsr,targetSampleRate,[0.04 0.15]);
HF = bandpower(rr_intervalsr,targetSampleRate,[0.15 0.4]);  

LFHF = LF/HF;

end
