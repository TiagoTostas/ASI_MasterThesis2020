function [HR, rr_intervals, rr_time] = HR_session(rpeaks_positions,fs)
%% Description
%{
Computation of the in session features:
%}

%% Inputs
%{
rpeaks_positions: vector containing R-peak positions from the recorded session
fs: sampling frequency
%}

%% Outputs
%{
HR: heart rate 
rr_intervals and rr_time: RR intervals (ms) and its timestamps (seconds)
%}

%% Pre-processing data
% Compute sequence of RR intervals (in ms)
rr_sequence = 1000 * (diff(rpeaks_positions)./fs); 

% RR-intervals median 21 samples
rr_median = movmedian(rr_sequence,21);

%%
% SQI - based on the local variance of 10 samples of the RR-intervals
% Index normalization [0,1]
%{
SQI = movvar(rr_sequence,5);
SQI = normalize(SQI,'range');
SQI = (SQI - ones(1,length(SQI))) * -100; 
%}

%%
% RR-intervals artefact correction
% 1) |rr - medrr| / medrr > 20%
% 2) higher than 1500ms or lower than 300ms (heart rate between 45bpm and 200bpm)
rr_corrected = rr_sequence;
rr_corrected(1:20) = nan; % discard first 10 samples (transient)
rr_corrected((abs(rr_sequence - rr_median)./rr_median) > 0.2) = nan;
rr_corrected(or(rr_corrected > 2000,rr_corrected < 300)) = nan;

% Interpolate missing data with spline
rr_intervals = fillmissing(rr_corrected,'movmedian',15);

% Heart Rate
HR = (60*1000) ./ rr_intervals;
HR = movmedian(HR,21);

% RR-intervals time vector
rr_time = rpeaks_positions./fs;
rr_time = rr_time(1:end-1)-rr_time(1); %start timestamps from 0s

end
