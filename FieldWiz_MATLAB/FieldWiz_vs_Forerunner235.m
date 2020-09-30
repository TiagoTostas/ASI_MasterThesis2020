%% Comparison FieldWiz vs Garmin Forerrunner 235

load('/Users/tiagorodrigues/OneDrive - Universidade de Lisboa/FieldWiz/FieldWiz_Data/100220/ECG100220.mat');
load('/Users/tiagorodrigues/OneDrive - Universidade de Lisboa/FieldWiz/FieldWiz_Data/100220/HR100220.mat')

time_fieldwiz = 1/250 : 1/250 : length(ECG)/250;    % time(s), Fs=250 Hz
hr_fieldwiz = HR(1:10:end);                     % sampled at 10Hz -> 10equal values each

[NUM,TXT,RAW] = xlsread('/Users/tiagorodrigues/OneDrive - Universidade de Lisboa/FieldWiz/FieldWiz_Data/100220/100220.xls');
time_garmin = NUM(:,1);
hr_garmin = NUM(:,3);
 
% Detect R-peaks from the FieldWiz ECG
fs = 250;
remove_timestamps = 1000; %remove first n samples, due to initial transient
ecg = - ECG;
[qrs_amp_raw,qrs_i_raw,delay] = pan_tompkin(ecg(remove_timestamps:end),fs,1); 
rr_time = (1/fs) * qrs_i_raw;   
rr_intervals = [diff(rr_time) 0];

a = 0.03;   
rr_intervals = filtfilt(a,[1 a-1],rr_intervals);  
hr_pantompkins = 60 ./ rr_intervals;

trial_time = time_fieldwiz(end);

% Comparison heart rate
tiledlayout(2,1)
ax1 = nexttile;
x1 = time_fieldwiz;
y1 =  ECG;
plot(x1, y1)
title('Raw ECG','Fontsize',20)
ylim([-500 500])
xlim([0 trial_time])


ax2 = nexttile;
x2 = 1 : 1 : length(hr_garmin);
x2 = x2 + 300;
y2 = hr_garmin; %sampled at 1 Hz

x3 = rr_time;
y3 = hr_pantompkins;

y4 = hr_fieldwiz;
x4 = 0:1:length(hr_fieldwiz) -1;
x4 = x4; %delay of gps

plot(x2, y2,'--k','linewidth', 3)
title('Heart Rate Estimation','Fontsize',20)
hold on
plot(x3,y3,'r','linewidth', 2)
plot(x4,y4,'linewidth', 2)
xlabel('Time (s)')
ylabel('Heart Rate (bpm)')
ylim([50 200])
xlim([0 trial_time])

linkaxes([ax1,ax2],'x');

grid on
legend(ax2,{'Garmin Forerunner 235', 'FieldWiz using PanTompkins', 'FieldWiz'},'FontSize',12,'Location','southeast')
legend('boxoff')
sgtitle('Garmin Forerunner 235 Vs FieldWiz shirt','Fontsize',30)


