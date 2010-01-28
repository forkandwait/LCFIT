
function [ex,EX] = cohorte(mxh,mxf);
%ex--period life expectancies at the last year of historical ASDR 'mxh'
%EX--forecasted life expectancies for cohorts at the last historical year
%make asdr for cohort aged 0
xx=size(mxh);nht=xx(1);
xx=size(mxf);ntrj=xx(1);nfor=xx(2);
for i=1:ntrj;%for cohort aged 0
    for na=1:nfor+1
    mc(i,1,na)=sqrt(mxh(nht,na)*mxf(i,1,na));%cohort age na at starting time
    end
    for tt=1:nfor-1
        for na=tt:nfor+1
        mc(i,tt+1,na)=sqrt(mxf(i,tt,na)*mxf(i,tt+1,na));%age i
        end
   end
end
for i=1:ntrj
    drt0(1)=mc(i,1,1);
    drt0(2)=mc(i,1,2);%ASDR(0) and ASDR(1-4) are in the first 5 years
    for na=3:nfor+1
    drt0(na)=mc(i,na-1,na);
    end
    drt=CoaleGt(drt0);
    [Ex]=lfexptex(drt);%life exp at birth and at 1
    EO(i,1)=Ex(1);%life exp at birth 
    EO(i,2)=Ex(2);%life exp at 1
    for k=3:nfor
        for j=k:nfor+1
        drt0(j)=mc(i,j-k+1,j);
        end
        drt=CoaleGt(drt0);    
        [Ex]=lfexptex(drt);
        EO(i,k)=Ex(k);
    end
end
EX=zeros(3,nfor);
if ntrj>1
EX(1,:)=prctile(EO,97.5);EX(2,:)=prctile(EO,50);EX(3,:)=prctile(EO,2.5);
else
EX(1,:)=EO;EX(2,:)=EO;EX(3,:)=EO;
end
[ex]=lfexptex(mxh(nht,:));
age(1)=0;age(2)=1;age(3:nfor)=5*(1:nfor-2);

clf;plot(age,ex(1:nfor),'o');hold;plot(age,EX(2,:));plot(age,EX(1,:),'.-');plot(age,EX(3,:),'--');
xlabel('Age');ylabel('Life expectancy');legend('Period','Cohort median','Cohort 97.5%','Cohort 2.5%')
title('Period and cohort life expectancies')