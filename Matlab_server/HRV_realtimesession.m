function [hrmean,rmssd,rr_interval,rr_time] = HRV_realtimesession(rpeaksposition,fs)
%% Description
%{
Real Time HRV 
Time-Domain: hrmean (bpm), RMSSD (ms)
%}

%% Inputs
%{
rpeaksposition: last R-peak position
fs: sampling frequency (e.g. 250 Hz)
%}
    % define n samples for HRV
    persistent bufferlastpeaks lastpeak
    if isempty(bufferlastpeaks)
        n_lastpeaks = 60; 
        lastpeak = 0;
        bufferlastpeaks = zeros(1,n_lastpeaks);
    end

    bufferlastpeaks = [bufferlastpeaks(2:end), 1000 * (rpeaksposition - lastpeak)./fs ]; % add last rpeakposition to buffer
    lastpeak = rpeaksposition;
    
    if bufferlastpeaks(1) == 0
        rmssd = nan;
        rr_interval = nan;
        rr_time = nan;
        hrmean = nan;
        
    else
        samples = 51;
        rr_intervals = rmoutliers(bufferlastpeaks,'movmedian',samples);
        
        % hrv metrics
        dist_square = sum(diff(rr_intervals).^2);
        
        hrmean = 60/(mean(rr_intervals(end-10:end)/1000)); % only take the last 10 samples
        if hrmean < 40 || hrmean > 200
            hrmean = nan;
        end
        
        rmssd = sqrt(dist_square/length(rr_intervals));
        rr_interval = rr_intervals(end);
        rr_time = rpeaksposition / fs;
    end

end

