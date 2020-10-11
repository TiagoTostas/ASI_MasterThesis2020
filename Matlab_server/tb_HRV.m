%% Load ECG Data
% 1) football player 
% 2) run johan
% 3) rest

test = 1;
fs = 250;

if test == 1
    ecg = load('20200706-zYBko.txt');
elseif test == 2
    ecg = load('20200422-JT-FWv2.txt');
elseif test == 3
    ecg = load('20200422-TR-Belt.txt');
else
    disp('Input ECG signal')
end
%% (Simulating rpeaks_positions from embedded)
% Sampling frequency
fs = 250;
% R-peak detection (Rpeaks output of fieldwiz)
[rpeaks_positions, ~] = ASI_segmenter(ecg,fs,1,5);

%%
% HRV metrics for the 2 min session
[LF,HF,LFHF,hrmean,sdnn,rmssd,lnrmssd,rr_intervals1,rr_time1] = HRV_2min(rpeaks_positions,fs);

%%
% HR, RR-intervals, RR_time and during the entire session
[HR, rr_intervals2,rr_time2] = HR_session(rpeaks_positions,fs);

plot(HR,'Linewidth',1)
xlabel('Time(s)')
ylabel('Heart Rate (bpm)')

%%
% Real time HRV (rmssd)
for i = 1 : length(rpeaks_positions)
    [hrmean(i), rmssd(i), rr_interval(i), rr_time(i)] = HRV_realtimesession(rpeaks_positions(i),fs);
end

subplot(311)
plot(rr_time,rr_interval)
title('RR-intervals')
ylabel ('ms')

subplot(312)
plot(rr_time,hrmean)
title('Heart Rate ')
ylabel('bpm')

subplot(313)
plot(rr_time,rmssd)
title('RMSSD')
xlabel('Time (s)')
