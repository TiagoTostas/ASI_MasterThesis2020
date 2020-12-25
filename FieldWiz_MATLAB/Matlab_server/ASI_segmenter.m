function [rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(ecg,fs,gr,Pth)
%% Description
%{
 R-peakdetection based on a combination of derivative, integration and
 squaring and adaptive exponential decay threshold.
%}

%% References
%{
Modification by Tiago Rodrigues, based on:
[R. Gutiérrez-rivas 2015] Novel Real-Time Low-Complexity QRS Complex Detector Based on Adaptive Thresholding. Vol. 15,no. 10, pp. 6036?6043, 2015.
[D. Sadhukhan] R-Peak Detection Algorithm for Ecg using Double Difference And RRInterval Processing. Procedia Technology, vol. 4, pp. 873?877, 2012.
%}
 
%% Inputs
%{
ecg = raw ECG signal
fs = sampling frequency
gr = 1 for plots; gr = 0 no plots
Pth = exponential decay rate (rest=2 -> up to intense exercise = 10)
%}
 
%% Outputs
% rpeaks = location of the rpeaks
% rpeaks_amp = peaks of the processed ecg


%% Bandpass filter the signal
% Bandpass filter [3 45]Hz
% Fn = fs/2;  %nquyst frequency
% b = fir1(48,[3, 45]/Fn);
% a = 1;
%ecg = filtfilt(b,a,ecg);

%% R-peaks detection algorithm
%constants for Fs = 250Hz
Nd = 4;
Rmin = 0.2;
rpeaks_positions = [];

% buffers for the pre processed signals
i = 9;
tf = length(ecg);
diff = zeros(1,tf);
ddiff = zeros(1,tf);
squar = zeros(1,tf);
processed_ecg = zeros(1,tf);
threshold = zeros(1,tf);
  
% adaptive detection threshold
Thr = 0;

% counter for the state
Rpeakamp = 0;
Ramptotal = 0;
counter = 6;  % sets duration in each state, starting at 6 
tf1 = round (Rmin*fs);  %time in the first state
state = 1;  %initial state of the fsm
delay = Nd; % from the diff and ddiff


while i < tf
    
    %Pre-processing: derivative x[n]-x[n-Nd]; derivative x[n]-x[n-1]; squaring: x[n]^2 and integration: 5 samples
    diff(i) = ecg(i) - ecg(i - Nd);
    ddiff(i) = diff(i) - diff(i - 1);
    squar(i) = ddiff(i) * ddiff(i); 
    processed_ecg(i) = (squar(i)+squar(i-1)+squar(i-2)+squar(i-3)+squar(i-4))/5;
    
    % State 1: looking for maximum    
    % Rpeak amplitude and position 
    if state == 1
        if counter < tf1
            if processed_ecg(i) > Rpeakamp
                Rpeakamp = processed_ecg(i);
                rpeakpos = i-delay;
            else 
                threshold(i) = Rpeakamp;
            end
            threshold(i) = Rpeakamp;
        else
            threshold(i) = Rpeakamp;
            state = 2;
            Ramptotal = (19/20) * Ramptotal + (1/20) * Rpeakamp;
            rpeaks_positions = [rpeaks_positions,rpeakpos];
                
            % setting time for state 2
            d = (i - rpeakpos);
            tf2 = tf1 + 0.2 * fs - d;
            Thr = Ramptotal;   %threshold for state 3
            
        end
        
    % State 2: waiting state
    elseif state == 2
       threshold(i) = Ramptotal;
       if counter > tf2
            state = 3;  
       end
          
    % State 3: decreasing threshold        
    elseif state == 3
        threshold(i) = Thr;
        if processed_ecg(i) < Thr
            Thr = round(Thr*exp(-Pth/fs));  % exponential decay
        else
            Rpeakamp = 0;
            counter = 0;              
            state = 1;
        end            
    end
    counter = counter+1;
    i=i+1;   
end


%% Graphics
rpeaks_pos = rpeaks_positions;
time = 1/250:1/250:length(ecg)/250;
rpeaksproc_amp = ecg(rpeaks_pos);    
heartrate= (250*60)./diff(rpeaks_pos);
median_hr = movmedian(heartrate,20);

if gr == 1
    
    set(gcf,'Position',  [100, 100, 500, 300])

    tiledlayout(2,1)
    % ECG plot
    ax1 = nexttile; 
    x1 = time; 
    x2 = rpeaks_pos./250; 
    y1 = ecg;
    plot(x1,y1,'linewidth',1.5)
    hold on
    plot(x2,rpeaksproc_amp,'*r','linewidth',1.5)
    legend('Raw ECG','R-peaks','Location','bestoutside')
    xlim([0 x2(end)])
    %ylim([-200 200])
    ylabel('ADC value')
    grid on
    
    % R-peaks plot and threshold
    ax2 = nexttile;
    x1 = time;
    y2 = processed_ecg;
    y21 = threshold;
    plot(x1,y2,'linewidth',1.5)
    hold on
    plot(x1,y21, 'r--','linewidth',1)
    hold off
    
    legend('Processed ECG','Detection Treshold','Location','bestoutside')
    xlabel('Time(s)')
    ylabel('Processed ECG')
    xlim([0 x2(end)])
    grid on
    
    linkaxes([ax1 ax2],'x')
end
    