clear all;close all;clc;
load data
data=data;
S_S = size(data);k=1;l=1;
temp=[]; temp_num=[];
for i = 1 : 80;
    for j=3:8;
        time_temp(j,1)=0+(j-1)*4000;
        time_temp(j,2)=3500+(j-1)*4000;

        temp=data(find(data(:,2)==(i-1)),:);
        temp_num(1,j-2)=size(find(temp(:,1)<=time_temp(j,2)&temp(:,1)>=time_temp(j,1)),1);
        temp=[];
    end
    freq_p(i,1)=mean(temp_num/3.5);
    temp_num=[];
    
end
Pyr_Spon_mean=mean(freq_p);spon_freq_p_std=std(freq_p);

temp=[]; temp_num=[];

for i = 81 : 100;
    for j=3:8;
        time_temp(j,1)=0+(j-1)*4000;
        time_temp(j,2)=3500+(j-1)*4000;

        temp=data(find(data(:,2)==(i-1)),:);
        temp_num(1,j-2)=size(find(temp(:,1)<=time_temp(j,2)&temp(:,1)>=time_temp(j,1)),1);
        temp=[];
    end
    freq_inter(i-80,1)=mean(temp_num/3.5);
    temp_num=[];
    
end        
Int_Spon_mean=mean(freq_inter);spon_freq_inter_std=std(freq_inter);
block_spon=[Pyr_Spon_mean;spon_freq_p_std;Int_Spon_mean;spon_freq_inter_std];





