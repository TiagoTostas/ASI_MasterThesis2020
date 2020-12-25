%% Sensitivity and Positive Predictivity
%{
Benchmarking comparison of the ASI_segmenteer algorithm in the common ECG
databases: MIT-BIH, ST-T database, noise and stress MIT-BIH (nstd) and
Challenge 2014.
%}


%% Compare against European ST-T Database
fid = fopen('/Users/tiagorodrigues/Universidade de Lisboa/Ana Luisa Nobre Fred - TiagoRodrigues_EPFL_FieldWiz_tese_2020/FieldWiz_MATLAB/Database_comparison/ST-segment/RECORDS.txt');
id = textscan(fid,'%s');
fclose(fid);

id = id{1,1};

TP = zeros(1, length(id)); 
FP = zeros(1, length(id)); 
FN = zeros(1, length(id)); 


for i = 1 :length(id)

% read signal and compute peaks
[sig, Fs, tm] = rdsamp(strcat('edb/',id{i,1}), 1);
sig = 1000.*sig;  %sig value was below 1 

[rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(sig,250,1,3);
[ann,anntype,subtype,chan,num,comments]= rdann(strcat('edb/',id{i,1}),'atr');

% Consider only Beat annotations
beat_ann = {'N','L','R','B','A','a','J','S','V','r','F','e','j','n','E','/','f','Q','?'};
bol_beats = ismember(anntype,beat_ann);
rpeaks_ref = ann(bol_beats);

tol = round (0.1 / (1/Fs));
    % go for every detected peaks
    for j = 1 : length(rpeaks_positions)
        distances = abs( rpeaks_ref - rpeaks_positions(j));
        if min(distances) < tol
            TP(i) = TP(i)+1;   
        end
    end
    
    FP(i) = length(rpeaks_positions) - TP(i);
    FN(i) = length(rpeaks_ref) - TP(i);   
    
end

% Simulation ended signal
load handel
sound(y,Fs)

%%
for i = 1:length(id)
     Se(i) = TP(i)/ (TP(i) + FN(i));
     P(i) = TP(i) / (TP(i) +FP(i));
     Der(i) = (FP(i)+FN(i))/(TP(i)+FN(i));
end


bar(P)
ylabel('PPV')
title('MIT-BIH (nstdb)')
set(gca,'xticklabel',id)

Se_total = mean(Se).*100;
P_total = mean(P).*100;
Der_total = mean(Der).*100;


%% Compare against MIT-BIH Arrythmia
id = cat(2,100:109,111:119,121:124,200:203,205,207:210,212:215,217,219:223,228,230:234);

TP = zeros(length(id),26);
FP = zeros(length(id),26);
FN = zeros(length(id),26);
Fs = 250;

for i = 1 :length(id)
    
% read signal and compute peaks
[sig(:,i), Fs, tm] = rdsamp(strcat('mitdb/',num2str(id(i))), 1);
[ann,anntype,subtype,chan,num,comments] = rdann(strcat('mitdb/',num2str(id(i))),'atr');

% consider only beat annotations
beat_ann = {'N','L','R','B','A','a','J','S','V','r','F','e','j','n','E','/','f','Q','?'};
%beat_ann = {'N'};
bol_beats = ismember(anntype,beat_ann);
rpeaks_ref = ann(bol_beats);

[rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(sig(:,i),360,0,3);

tol = round (0.1 / (1/Fs));
    % go for every detected peaks
    for p = 1 : length(rpeaks_positions)

        distances = abs( rpeaks_ref - rpeaks_positions(p));
        if min(distances) < tol
            TP(i) = TP(i)+1;   
        end
    end

    FP(i) = length(rpeaks_positions) - TP(i);
    FN(i) = length(rpeaks_ref) - TP(i);
end

%%
id = cat(2,100:109,111:119,121:124,200:203,205,207:210,212:215,217,219:223,228,230:234);
     
Se = TP ./ (TP + FN);
PPV = TP ./ (TP +FP);
F1 = (2*TP)./(2*TP+FP+FN);


% Plot
bar(Se(:,14))

xlabel('Record id','FontSize',20)
title('Se','FontSize',20)
set(gcf,'defaultfigurecolor','w')
ylim([0 1])

%% ROC curves

Pth_values = 1:0.2:6;
Se_total = mean(Se).*100;
P_total = mean(PPV).*100;
F1_total = mean(F1).*100;


plot(Pth_values,Se_total,'linewidth',2)
hold on
plot(Pth_values,P_total,'linewidth',2)

ylabel('%')
xlabel('P_{th} values')
legend('Se', 'PPV','Location','SE')
grid minor

ylim([90 100])

%% Compare against noise and stress MIT-BIH (nstd)

fid = fopen('/Users/tiagorodrigues/Universidade de Lisboa/Ana Luisa Nobre Fred - TiagoRodrigues_EPFL_FieldWiz_tese_2020/FieldWiz_MATLAB/Database_comparison/Noise/RECORDS.txt');
id = textscan(fid,'%s');
fclose(fid);

id = id{1,1};
id = id(1:end-3);



TP = zeros(1, length(id)); 
FP = zeros(1, length(id)); 
FN = zeros(1, length(id)); 


for i = 1  :length(id)
% read signal and compute peaks

[sig, Fs, tm] = rdsamp(strcat('nstdb/',num2str(id{i})), 1);
sig = 1000.*sig;  %sig value was below 1 

[rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(sig,360,1,3);

[ann,anntype,subtype,chan,num,comments]= rdann(strcat('nstdb/',id{i}),'atr');

% Consider only Beat annotations
beat_ann = {'N','L','R','B','A','a','J','S','V','r','F','e','j','n','E','/','f','Q','?'};
bol_beats = ismember(anntype,beat_ann);
rpeaks_ref = ann(bol_beats);


tol = round (0.1 / (1/Fs));
    % go for every detected peaks
    for j = 1 : length(rpeaks_positions)
        
        distances = abs( rpeaks_ref - rpeaks_positions(j));
        if min(distances) < tol
            TP(i) = TP(i)+1;   
        end
    end
    
    FP(i) = length(rpeaks_positions) - TP(i);
    FN(i) = length(rpeaks_ref) - TP(i);
    
end

%%
for i = 1:length(id)
     Se(i) = TP(i)/ (TP(i) + FN(i));
     P(i) = TP(i) / (TP(i) +FP(i));
     Der(i) = (FP(i)+FN(i))/(TP(i)+FN(i));
end


bar(P)
ylabel('PPV')
title('MIT-BIH (nstdb)')
set(gca,'xticklabel',id)



%% Compare against Challenge 2014

fid = fopen('/Users/tiagorodrigues/Universidade de Lisboa/Ana Luisa Nobre Fred - TiagoRodrigues_EPFL_FieldWiz_tese_2020/FieldWiz_MATLAB/Database_comparison/Challenge2014/RECORDS.txt');
id = textscan(fid,'%s');
fclose(fid);

id = id{1,1};

TP = zeros(1, length(id)); 
FP = zeros(1, length(id)); 
FN = zeros(1, length(id)); 


for i = 34 % :length(id)
% read signal and compute peaks

[sig, Fs, tm] = rdsamp(strcat('challenge/2014/set-p/',num2str(id{i})), 1);
sig = 1000.*sig;  %sig value was below 1 

[rpeaks_positions, rpeaksproc_amp] = ASI_segmenter(sig,360,1,3);

[ann,anntype,subtype,chan,num,comments]= rdann(strcat('challenge/2014/set-p//',id{i}),'atr');

% Consider only Beat annotations
beat_ann = {'N','L','R','B','A','a','J','S','V','r','F','e','j','n','E','/','f','Q','?'};
bol_beats = ismember(anntype,beat_ann);
rpeaks_ref = ann(bol_beats);


tol = round (0.1 / (1/Fs));
    % go for every detected peaks
    for j = 1 : length(rpeaks_positions)
        
        distances = abs( rpeaks_ref - rpeaks_positions(j));
        if min(distances) < tol
            TP(i) = TP(i)+1;   
        end
    end
    s
    FP(i) = length(rpeaks_positions) - TP(i);
    FN(i) = length(rpeaks_ref) - TP(i);
    
end

%%
for i = 1:length(id)
     Se(i) = TP(i)/ (TP(i) + FN(i));
     P(i) = TP(i) / (TP(i) +FP(i));
     Der(i) = (FP(i)+FN(i))/(TP(i)+FN(i));
end


bar(P)
ylabel('PPV')
title('MIT-BIH (nstdb)')
set(gca,'xticklabel',id)


