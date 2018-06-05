clear all;close all;
clc;

dname='';  %%%% this is the directory for load spiking data first
fname=fullfile(dname,'data');
data=load(fname);  
  
start_time=1000;
stop_time=max(data(:,1));     



%load LP.mat;
upscale=1;
num=900*upscale; %define the cell number used for plots
inter_num=100*upscale;
all_num=num+inter_num;
principal_cell = [1:num]' - 1;

%load NP_cell.mat;
Inter_cell = [num+1:all_num]' - 1;
TypeA=640*upscale;TypeC=260*upscale;

principal_cell_A = [1:TypeA]' - 1;
principal_cell_C = [TypeA+1:num]' - 1;

figure (1)
data_P=data(find(data(:,2)<num),:);
data_I=data(find(data(:,2)>=num),:);
subplot (2,2,[1 3])
plot(data_P(:,1),data_P(:,2)+1,'blue.')
hold on; plot(data_I(:,1),data_I(:,2)+1,'r.'); axis tight;  
title('rastor plot');ylabel('ID of Neurons'); xlabel('time (ms)'); xlim([10000 15000]);


%FR distribution plot for plastic cell%   
% for i = 1:size(principal_cell,1);                   
%     plastic_cell_time{i,1} = data(find(data(:,1) >= start_time & data(:,1) <= stop_time & data(:,2) ==principal_cell(i,1)),:);
% end;
data_analysis=data(data(:,1)>=start_time&data(:,1)<=stop_time,:);
spikes_sort=sortrows(data_analysis,2);
[n, bin] = histc(spikes_sort(:,2), unique(spikes_sort(:,2)));
n_cum=cumsum(n);
cell_freq=zeros(all_num,1);
cell_freq(spikes_sort(n_cum(1),2)+1,1)=n(1)/(stop_time-start_time)*1e3;
for i=2:length(n);                  
cell_freq(spikes_sort(n_cum(i),2)+1,1)=n(i)/(stop_time-start_time)*1e3;
end;
plastic_cell_freq_mean=mean(cell_freq(1:num));
plastic_cell_freq_std=std(cell_freq(1:num));
plastic_cell_A_freq=cell_freq(1:TypeA);
plastic_cell_C_freq=cell_freq(TypeA+1:num);
plastic_cell_freq=cell_freq(1:num);

Nplastic_cell_freq_mean=mean(cell_freq(num+1:end));
Nplastic_cell_freq_std=std(cell_freq(num+1:end));
Nplastic_cell_freq=cell_freq(num+1:end);

% GG_list = ['PN_freq','.txt'];
% dlmwrite(GG_list,plastic_cell_freq,'delimiter','\t','precision', '%f');
% 
% GG_list = ['ITN_freq','.txt'];
% dlmwrite(GG_list,Nplastic_cell_freq,'delimiter','\t','precision', '%f');
figure (1)
subplot (2,2,4)
A=[0:0.1:10];
[nb_A,xb_A]=hist(plastic_cell_A_freq,A);

%histoutline(plastic_cell_A_freq,20)
%h = findobj(gca,'Type','patch');
%h.FaceColor = [1 1 1];
[X,I]=find(nb_A>0);   %%%delete any zero histogram bar
     bh_A=bar(xb_A(:,I),nb_A(:,I));
     set(bh_A,'facecolor',[0.7 0.7 1]);

nb_A_plot=xb_A(:,I)';
xb_A_plot=nb_A(:,I)';

set(gca,'xscale','log'); 
xlim([10^(-2) 10^2]);

[nb_C,xb_C]=hist(plastic_cell_C_freq,A);
[X,I]=find(nb_C>0);   %%%delete any zero histogram bar

%h = findobj(gca,'Type','patch');
%h.FaceColor = [1 1 1];
figure (1)
hold on; bh_C=bar(xb_C(:,I),nb_C(:,I));
set(bh_C,'facecolor',[0 0 1]);

nb_C_plot=xb_C(:,I)';
xb_C_plot=nb_C(:,I)';

x=sprintf('Spiking freq histogram for PNs (firing freq mean+/-std is %3.2fHz+/-%3.2fHz)',plastic_cell_freq_mean,plastic_cell_freq_std);
title(x);ylabel('counts(#)');
subplot (2,2,2)
% hist(Nplastic_cell_freq);
A=[0:0.5:100];
[nb,xb]=hist(Nplastic_cell_freq,A);
[X,I]=find(nb>0);
%h = findobj(gca,'Type','patch');
%h.FaceColor = [1 1 1];
 hold on; bh=bar(xb(:,I),nb(:,I));
 set(bh,'facecolor',[1 0 0]);
nb_I_plot=xb(:,I)';
xb_I_plot=nb(:,I)';
     
set(gca,'xscale','log');xlabel('Hz'); 
xlim([10^(-1) 10^(2)]);
x=sprintf('Spiking freq histogram for ITNs (firing freq mean+/-std is %3.2fHz+/-%3.2fHz)',Nplastic_cell_freq_mean,Nplastic_cell_freq_std);
title(x);ylabel('counts(#)');


%%%%%%%%for analyzing LFP%%%%%%%%%
dname='';
fname=fullfile(dname,'LFPs','LFP_elec_0');
LFP=load(fname);
highBand=1.17;
dt=1;
[bFilt, aFilt] = butter(4,highBand/(1000/(2*dt)),'high');
LFP_afterHP=filtfilt(bFilt,aFilt,LFP);

figure (2)
subplot(2,1,2)
ev=[];
ev=LFP;windowLen = 1024;
ev(1:start_time) = [];
%ev=ev-mean(ev);
[f,Pxxn,tvect,Cxx] = psautospk(ev, 1, windowLen, bartlett(windowLen), windowLen/2, 'none') ;
hold on ; plot(f,Pxxn,'black', 'LineWidth', 2);ylabel('PSD');xlabel('Freq(Hz)')
set(gca,'yscale','log'); set(gca,'xscale','log');xlim([0 500]);title('PSD of LFP');grid on;

subplot(2,1,1)
plot(LFP_afterHP);
title('raw LFP trace');xlim([10000 15000]);

