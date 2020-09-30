% Moving Average
load('/Users/tiagorodrigues/OneDrive - Universidade de Lisboa/FieldWiz/FieldWiz_Data/120220/ECG120220.mat')
fs = 250;

[b,a] = butter(4,[8 20]/125,'bandpass');
ECG = resample(ECG,4,1);

ecg_filter = filtfilt(b,a,ECG); % filter [8 20]Hz
ecg_diff = diff(ecg_filter);    % derivative filter
ecg_rect = ecg_diff.^2;         % squaring 

input = ecg_rect;
average1 = movmean(input, 0.1*fs);
average2 = movmean(input, 0.4*fs);

movingAverage1 = conv(input, ones(0.1*fs,1)/(0.1*fs), 'same');
movingAverage2 = conv(input, ones(0.6*fs,1)/(0.6*fs), 'same');

