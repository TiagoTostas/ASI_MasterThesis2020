%% Test detrending effect on frequency hrv
%% run
% rest
%fid = fopen('Users/tiagorodrigues/Universidade de Lisboa/Ana Luisa Nobre Fred - TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/HRV_5min/20200423-TR-Belt.txt') ;

% sharp drop
%fid = fopen('Users/tiagorodrigues/Universidade de Lisboa/Ana Luisa Nobre Fred - TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/Activities/20200502-JT-FWv2.txt') ;

% run
fid = fopen('Users/tiagorodrigues/Universidade de Lisboa/Ana Luisa Nobre Fred - TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/Activities/20200510-TR-Belt.txt') ;

data = textscan(fid,'%f','HeaderLines',10);
ecg = cell2mat(data);
fclose(fid);

fs = 250;
% R-peak position

run = 30000;
rest = 6000;
runrest = 1100000;
test = run;
ecg = ecg(test : test + 5.1 * 60*250); %import 5min of data running
[rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(ecg,250,1,6);

rr_sequence = 1000 * (diff(rpeaks_positions)./fs); 

% RR-intervals artefact correction
% Remove rr-intervals that follow |rr-medrr|/medrr > 20%
rrmedian = movmedian(rr_sequence,10);
rr_corrected = rr_sequence;
rr_corrected((abs(rr_sequence-rrmedian)./rrmedian) > 0.2) = nan;

% Interpolate missing data with spline
rr_intervals = fillmissing(rr_corrected,'spline');
rr_intervalsdiff =  diff(rr_intervals);

% RR-intervals time vector
rr_time = rpeaks_positions./fs;
rr_time = rr_time(1:end-1)-rr_time(1); %start timestamps from 0s

% Resampling RR-Intervals at 7Hz for frequency domain features
targetSampleRate = 4;
[rr_intervalsr , rr_timer] = resample(rr_intervals,rr_time,targetSampleRate,'spline');

% Detrending the rr_intervals for Frequency domain (stationary + trend)
z = rr_intervalsr;
T = length(z);
lambda = 500; 
I = speye(T);
D2 = spdiags(ones(T-2,1)*[1 -2 1],[0:2],T-2,T);
rr_intervalsstatr = (I - inv(I + lambda^2*D2'*D2))*z';
rr_trend = rr_intervalsr' - rr_intervalsstatr; %apagar isto


%% Histogram rr-intervals
histogram(rr_intervals)
xlabel('RR-intervals (ms)')
ylabel('Number of intervals')
grid on
set(gcf,'color','w');

%% Detrending 

plot(rr_time, rr_sequence,'Color',[0 0 0]+0.05*15,'LineWidth',2)
hold on
plot(rr_time, rr_intervals,'Color',[0 0 0]+0.05*5,'LineWidth',2)
plot(rr_timer, rr_trend,'--r','LineWidth',1.5)
plot(rr_timer, rr_intervalsstatr,'Color',[0 0 0],'LineWidth',2)

ylim([-200 1000])
xlim([0 300])
xlabel('Time (s)','FontSize',20)
ylabel('RR-intervals (ms)','FontSize',20)
grid on

legend('Original RR-intervals', 'Corrected RR-intervals','RR-intervals trend','Detrended RR-intervals','Fontsize', 20)
set(gcf,'color','w');
%%

fs = 250;
[LFnorm,HFnorm,sdnn,rmssd,lnrmssd,rr_intervals,rr_time] = HRV(rr_intervalsstatr',fs);

