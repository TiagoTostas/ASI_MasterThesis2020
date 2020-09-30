%% Load Data
pathname = '/Users/tiagorodrigues/Universidade de Lisboa/Ana Luisa Nobre Fred - TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/HRV_5min/';
directory = dir(pathname); 
dircell = struct2cell(directory)' ;   
filenames = dircell(4:end,1);

name = 'TR';
indexes = find(~cellfun(@isempty,strfind(filenames,name)));
num_recordings = length(indexes);

for i=1:num_recordings-1
    filename = filenames{indexes(i+1)};
    
    filedir = strcat(pathname,filename);
    fid = fopen(filedir);
    data = textscan(fid,'%f','HeaderLines',10);
    ecg = cell2mat(data);
    fclose(fid);
    
    
    time = 1/250:1/250:length(ecg)/250;
    [rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(ecg,250,0,2);
    fs = 250;
    [sdnn,rmssd,lnrmssd,rr_intervals,rr_time] = HRV(rpeaks_positions,fs) ;

        
    subplot(num_recordings-1,3,(i-1)*3+1)
    plot(time,ecg)
    title(filename)
    xlim([0,300])
    ylim([-300,300])

   

    subplot(num_recordings-1,3,(i-1)*3+2)
    plot(rmssd)
    ylim([0 100])
    xlim([0 300])

    
    subplot(num_recordings-1,3,(i-1)*3+3)
    boxplot(rmssd)
    ylim([0 100])

end
 xlabel('Time (s)')
 
 
 %%
 fid = fopen('Users/tiagorodrigues/Universidade de Lisboa/Ana Luisa Nobre Fred - TiagoRodrigues_EPFL_FieldWiz_tese_2020/Data/Experiments/20200416-TR-FWv2series.txt') ;
data = textscan(fid,'%f','HeaderLines',10);
ecg = cell2mat(data);
fclose(fid);


% R-peak position
%ecg = -1.*ecg;
[rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(ecg,250,0,2);
fs = 250;
[LFnorm,HFnorm,sdnn,rmssd,lnrmssd,rr_intervals,rr_time] = HRV(rpeaks_positions,fs);


%%
z = rr_intervals;
 
T = length(z);
lambda = 200; 
I = speye(T);
D2 = spdiags(ones(T-2,1)*[1 -2 1],[0:2],T-2,T);
z_stat = (I - inv(I + lambda^2*D2'*D2))*z';


