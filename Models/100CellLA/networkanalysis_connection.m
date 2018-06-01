clc;clear all;close all;
% load shock2Idd.txt;
% load shock2Idv.txt;
%load shock2LAdd.txt;
%load shock2LAdv.txt;

% load tone2Idd.txt;
% load tone2Idd2.txt;
% load tone2Idv.txt;
% load tone2Idv2.txt;
load Syn_Matrix_Adel.txt;
Syn_Matrix=Syn_Matrix_Adel
% exc
for i=1:80;
    connetto(i,1)=size(find(Syn_Matrix(i,1:80)>0),2);
end   
 connetto_ave_exc=mean(connetto);
 connetto_std_exc=std(connetto);

for i=1:80;
    connetfrom(i,1)=size(find(Syn_Matrix(1:80,i)>0),1);
end   
 connetfrom_ave_exc=mean(connetfrom);
 connetfrom_std_exc=std(connetfrom);
 % inh
 connetfrom=[];
 for i=1:80;
    connetfrom(i,1)=size(find(Syn_Matrix(81:100,i)>0),1);
end   
 connetfrom_ave_inh=mean(connetfrom);
 connetfrom_std_inh=std(connetfrom);
 
  connetfrom=[];
  for i=81:100;
    connetfrom(i-80,1)=size(find(Syn_Matrix(1:80,i)>0),1);
end   
 connetfrom_ave_inter_exc=mean(connetfrom);
 connetfrom_std_inter_exc=std(connetfrom);
 
 
 
 
 
 % method3
 allconnections=size(find(Syn_Matrix(1:80,1:80)>0),1);
 connectivity=100*allconnections./(80)./(80-1);