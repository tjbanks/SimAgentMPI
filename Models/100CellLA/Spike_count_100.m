% Get Tone Response of All Pyr Cells by Trial
% Response from a cell is stored in a row (8 row all together)
% For 8 Sens, 16 Conds and 20 Exts. 

clc;clear all;close all;

load data;
data=data;

[C1,I]=sort(data(:,1));
C2=data(I,:);clear data;   % Sort the data in column dimension


Ncells=100;
  
gap1 = 0;               % duration before the Sensitization 
gap2 = 0;               % gap between Sens. and Cond.
gap3 = 100000;           % gap between Cond. and Ext.

Trial_Sen = 8;
Trial_Con = 16;
Trial_Ext = 20;

d_Sen = Trial_Sen*4000;
d_Con = Trial_Con*4000;
d_Ext = Trial_Ext*4000;

bin = 300;                        % 50 or 300

Trial_Start  = 3500;             % 3500
Trial_End    = Trial_Start + bin; % 3550 or  3700
r1=size(C2);         % r1 is the overall spike #


% =====================================================
% ======================  Sensitization Phase =========

min_T  = Trial_Start  + gap1;
max_T  = Trial_End    + gap1;


T_l  = min_T;
T_h  = min_T  + bin;

T1 = T_l ;
T2 = T_h ;

%%%%%%%%%%Number of cells in LAdd%%%%%%%%%%%%%

%%%%%%%%%%Number of cells in LAdd%%%%%%%%%%%%%
V1 = 1;      %transiently plastic cell
V2 = 3;
V3 = 4;
V4 = 8;



%%%%%%%%%%Habituation%%%%%%%%%%%%%

SENS(1:Ncells,1:Trial_Sen) = 0;

 C3=cell(Trial_Sen,1);
for i=1:Trial_Sen
C3{i,1} = C2(find(C2(:,1)>=(3500+4000*(i-1))& C2(:,1)<=(3800+4000*(i-1))),:);
end

for Hab_tone=1:Trial_Sen
  for i=1:size(C3{Hab_tone})
    d=C3{Hab_tone}(i,2)+1;%neuron ID +1
    U = SENS(d,Hab_tone)+1;
    SENS(d,Hab_tone)= U;
   end
end


%%%%%%%%%%Conditioning%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
COND(1:Ncells,1:Trial_Con) = 0;
C4=cell(Trial_Con,1);

for i=1:Trial_Con
C4{i,1} = C2(find(C2(:,1)>=(Trial_Sen*4000+3500+4000*(i-1))& C2(:,1)<=(Trial_Sen*4000+3800+4000*(i-1))),:);
end

for Con_tone=1:Trial_Con
  for i=1:size(C4{Con_tone})
    d=C4{Con_tone}(i,2)+1;         %neuron ID +1
    U = COND(d,Con_tone)+1;
    COND(d,Con_tone)= U;
   end
end

%%%%%%%%%%Extinction%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
EXT(1:Ncells,1:Trial_Ext) = 0;
C5=cell(Trial_Ext,1);

for i=1:Trial_Ext
C5{i,1} = C2(find(C2(:,1)>=((Trial_Con+Trial_Sen)*4000+gap3+3500+4000*(i-1))& C2(:,1)<=((Trial_Con+Trial_Sen)*4000+gap3+3800+4000*(i-1))),:);
end

for Ext_tone=1:Trial_Ext
  for i=1:size(C5{Ext_tone})
    d=C5{Ext_tone}(i,2)+1;         %neuron ID +1
    U = EXT(d,Ext_tone)+1;
    EXT(d,Ext_tone)= U;
   end
end

save('SENS','SENS');
save('COND','COND');
save('EXT','EXT');
