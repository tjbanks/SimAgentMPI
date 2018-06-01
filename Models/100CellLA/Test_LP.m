close all;clear all;clc;

load SENS;load COND; load EXT;
DATA = [SENS,COND,EXT];
%Cell_type = Cell_type;
threshold_tp = 0;
threshold_lp = 0;
DATA_Block(:,1)=mean(DATA(:,3:8));
for cellID=1:size(DATA,1);
    DATA_Block(cellID,1)=mean(DATA(cellID,3:8));
for i=2:10
DATA_Block(cellID,i)=mean(DATA(cellID,9+(i-2)*4:9+(i-2)*4+3));
end
end

%%%%%%%%%%%%%%% criterion for plastic cell %%%%%%%%%%%%%%%%%%%%%%
k=1;h=1;
for i = 1 : 80
    p(i,1) = ttest2(DATA(i,3:8),DATA(i,9:12),0.05,'both');     % t-test between hab and 1st group of conditioning
    p(i,2) = ttest2(DATA(i,3:8),DATA(i,13:16),0.05,'both');    % t-test between hab and 2nd group of conditioning
    p(i,3) = ttest2(DATA(i,3:8),DATA(i,17:20),0.05,'both');    % t-test between hab and 3rd group of conditioning
    p(i,4) = ttest2(DATA(i,3:8),DATA(i,21:24),0.05,'both');    % t-test between hab and 4th group of conditioning
    avg(i,1) = mean(DATA(i,9:12))-mean(DATA(i,3:8));           % avg. comparison between hab and 1st group of conditioning
    avg(i,2) = mean(DATA(i,13:16))-mean(DATA(i,3:8));          % avg. comparison between hab and 2nd group of conditioning
    avg(i,3) = mean(DATA(i,17:20))-mean(DATA(i,3:8));          % avg. comparison between hab and 3rd group of conditioning
    avg(i,4) = mean(DATA(i,21:24))-mean(DATA(i,3:8));          % avg. comparison between hab and 4th group of conditioning
    for j = 1 : 4
        if (p(i,j)==1 && avg(i,j)<=0)
            p2(i,j)=0;
        else
            p2(i,j)=p(i,j);
        end
    end
    
    if (sum(p2(i,:)>=1))
        P_cell(k,1) = i;                                     % P_cell is plastic cell's id
        DATA_Pcell(k,:) = DATA(i,:);                         % DATA_Pcell is plastic cell's tone response data
        k=k+1;
    else
        NP_cell(h,1) =i;                                          % NP_cell is non-plastic cell's id
        h=h+1;
    end
    
end

threshold_TPLP=0.75;
%%%%%%%%%%%%%%% criterion for seperation into TP and LP %%%%%%%%%%%%%%%%%%%%%%
k=1;m=1;n=1;h=1;l=1;p=1;q=1;
for i = 1 : size(DATA_Pcell,1)
    P_V(i,1) = (mean(DATA_Pcell(i,17:24))-mean(DATA_Pcell(i,3:8)))/(mean(DATA_Pcell(i,9:16))-mean(DATA_Pcell(i,3:8)));  % Persistence value 
    if (P_V(i,1)<=threshold_TPLP)                                        % <0.75 is the criteria for TP cell 
        if mean(DATA_Pcell(i,25:28))/0.3 >= threshold_tp;
        TP(k,:) = P_cell(i,1);                                 % TP is TP cell's id
        TP_DATA (k,1)=P_cell(i,1); 
        TP_DATA(k,2:45) = DATA_Pcell(i,:);                        % TP_DATA is TP cell's tone response data
        k=k+1;
        end;
    elseif (P_V(i,1)>threshold_TPLP)                                     % >0.75 is the criteria for LP cell 
        if mean(DATA_Pcell(i,25:28))/0.3 >= threshold_lp;
        LP(m,:) = P_cell(i,1);                                 % LP is LP cell's id
        LP_DATA(m,1)=P_cell(i,1); 
        LP_DATA(m,2:45) = DATA_Pcell(i,:);                       % LP_DATA is LP cell's tone response data
        m=m+1;
        end
    end      
end
 
%%%%%%%%%%%%%%% stringent criteria for screening  LP cells  %%%%%%%%%%%%%%%%%
F_boundary=10;  %%Hz
k=1;h=1;l=1;m=1;
for i = 1 : size(LP_DATA) 
    p = ttest2(LP_DATA(i,4:9),LP_DATA(i,10:13),0.05,'both');  % t-test between hab and 1st group of conditioning
    avg = mean(LP_DATA(i,10:13))-mean(LP_DATA(i,4:9)); 
    if (p ==1 && avg>=0)
        LP_block1(k,:)=LP_DATA(i,1);k=k+1;
    end
    p = ttest2(LP_DATA(i,4:9),LP_DATA(i,14:17),0.05,'both');    % t-test between hab and 2nd group of conditioning
    avg = mean(LP_DATA(i,14:17))-mean(LP_DATA(i,4:9));  
    if (p==1 && avg>=0)
        LP_block2(h,:)=LP_DATA(i,1);h=h+1;
    end
    
    p = ttest2(LP_DATA(i,4:9),LP_DATA(i,18:21),0.05,'both');    % t-test between hab and 3rd group of conditioning
    avg = mean(LP_DATA(i,18:21))-mean(LP_DATA(i,4:9));
      if (p==1 && avg>=0)
        LP_block3(l,:)=LP_DATA(i,1);l=l+1;
      end
      
     p = ttest2(LP_DATA(i,4:9),LP_DATA(i,22:25),0.05,'both');
     avg = mean(LP_DATA(i,22:25))-mean(LP_DATA(i,4:9));          % avg. comparison between hab and 4th group of conditioning
        if (p==1 && avg>=0)
        LP_block4(m,:)=LP_DATA(i,1);m=m+1;
        end  
end
 block34=unique([LP_block3;LP_block4]);

k=1;
for i = 1 : size(block34,1)   
    temp_LP(i,3) = mean(DATA(block34(i),17:20))/0.3;
    temp_LP(i,4) = mean(DATA(block34(i),21:24))/0.3;
  if temp_LP(i,3)>=F_boundary||temp_LP(i,4)>=F_boundary
         LP_new(k,1)=block34(i);
        k=k+1;
  end
end

for i = 1 : size(LP_new)  
    LPs_new(i,1) = mean(DATA(LP_new(i),3:8));
    LPs_new(i,2) = mean(DATA(LP_new(i),9:12));
    LPs_new(i,3) = mean(DATA(LP_new(i),13:16));
    LPs_new(i,4) = mean(DATA(LP_new(i),17:20));
    LPs_new(i,5) = mean(DATA(LP_new(i),21:24));
    LPs_new(i,6) = mean(DATA(LP_new(i),25:28));
    LPs_new(i,7) = mean(DATA(LP_new(i),29:32));
    LPs_new(i,8) = mean(DATA(LP_new(i),33:36));
    LPs_new(i,9) = mean(DATA(LP_new(i),37:40));
    LPs_new(i,10) = mean(DATA(LP_new(i),41:44));
end
LPss_new = mean(LPs_new);
LPss_new = LPss_new';
SEM_LP_new = std(LPs_new)/sqrt(size(LP_new,1));
LP_Num=size(LPs_new,1);LP_response=LPss_new;
block_LP_new=[LPss_new,SEM_LP_new']; 
x=1:10
figure (1)
plot(x,LPss_new,'--rs','LineWidth',2,...
                'MarkerEdgeColor','b',...
                'MarkerFaceColor','b',...
                'MarkerSize',5);
  title('new criteria LP');






