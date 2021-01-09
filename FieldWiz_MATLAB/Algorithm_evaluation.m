%{
1) Load ECG signal and evaluate R-peak detection
2) Compute instantaneous heartrate and hearrate from the moving median
3) Compare signal quality from wearable T-shirt with water / no-waater and
electrode gel
%}

%% Load Data
fid = fopen('Users/tiagorodrigues/OneDrive - Universidade de Lisboa/TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/Activities/20200508-SS-Belt.txt') ;
data = textscan(fid,'%f','HeaderLines',3);
ecg = cell2mat(data);
fclose(fid);

fs = 250;
[rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(ecg,fs,1,5);

rpeaks = ecg(rpeaks_positions);
time = 1/250:1/250:length(ecg)/250;

heartrate = (250*60)./diff(rpeaks_positions);
median_hr = movmedian(heartrate,15,'omitnan');
median_replace = filloutliers(heartrate,'spline','movmedian',4);


% Plot results 
figure
tiledlayout(1,1)
% ECG plot
ax1 = nexttile; 
x1 = time; 
x2 = rpeaks_positions./250; 
y1 = ecg;
plot(x1,y1,'linewidth',1.5)
hold on
plot(x2,rpeaksproc_amp,'*r','linewidth',1.5)


%% Evaluate ECG

ecg = -1.*ecg;
set(gcf,'Position',  [100, 100, 400, 200])
plot(time,ecg,'linewidth',2)
xlim([300 305])
%ylim([-500 500])

legend('Raw ECG')
xlabel('Time(s)','Fontsize',20)
ylabel('A.u ','Fontsize',20)
grid on


%% Heart Rate

tiledlayout(2,1)
%First plot
ax1 = nexttile;
x1 = time;
x2 = rpeaks_positions./250;
y1 = ecg;
plot(x1,y1)
hold on
plot(x2,rpeaks,'*r','linewidth',2)
title('Raw ECG','FontSize',20)
legend('Raw ECG','R-peaks')
xlabel('Time(s)')
xlim([0 x1(end)])


%Second Plot
ax2 = nexttile;
x2 = rpeaks_positions./250;
y2 = heartrate;
y3 = median_hr;
plot(x2(2:end),y2)
hold on 
plot(x2(2:end),y3,'linewidth',3)
legend('HR from Raw  R-peaks','HR from median R-peaks','Location','SE')

xlim([0 x1(end)])
ylim([40 200])

xlabel('Time (s)')
ylabel('Heart Rate (bpm)')
grid minor

linkaxes([ax1 ax2],'x')
set(gcf,'color','w');

%% 
% No water, water and gel

fid = fopen('Users/tiagorodrigues/OneDrive - Universidade de Lisboa/TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/Activities/20200420-JT-FWv2.txt') ;
data = textscan(fid,'%f','HeaderLines',3);
ecg_nowater = cell2mat(data);
fclose(fid);

fid = fopen('Users/tiagorodrigues/OneDrive - Universidade de Lisboa/TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/Activities/20200421-JT-FWv2.txt') ;
data = textscan(fid,'%f','HeaderLines',3);
ecg_water = cell2mat(data);
fclose(fid);

fid = fopen('Users/tiagorodrigues/OneDrive - Universidade de Lisboa/TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/Activities/20200422-JT-FWv2.txt') ;
data = textscan(fid,'%f','HeaderLines',3);
ecg_gel = cell2mat(data);
fclose(fid);

% plots
subplot(1,3,1)
time_nowater = 1/250 : 1/250 : length(ecg_nowater)/250;
plot(time_nowater,ecg_nowater,'linewidth',2)
ylabel('ADC Value','LineWidth', 15)
xlim([500,505])
ylim([-300,300])
title('No Water','LineWidth', 15)

subplot(1,3,2)
time_water = 1/250 : 1/250 : length(ecg_water)/250;
plot(time_water,ecg_water,'linewidth',2)
xlabel( 'Time (s)','LineWidth', 15)
xlim([500,505])
ylim([-300,300])
title('Water','LineWidth', 25)

subplot(1,3,3)
time_gel = 1/250 : 1/250 : length(ecg_gel)/250;
plot(time_gel,ecg_gel,'linewidth',2)
xlim([500,505])
ylim([-300,300])
title('Gel','LineWidth', 15)