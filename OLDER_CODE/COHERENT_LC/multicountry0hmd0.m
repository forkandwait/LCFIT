%  
%
% This code makes pictures, but also does a bunch of analyses on death rates (see instances of
% multisfact() below)
clear
load BXKT % get collective Bx and Kt here
nfor=55;nfor5=11;nspt=5;

drift=mean(diff(Kt));%Get R^2 for RW
Ktm(1)=Kt(1);
for i=2:45
    Ktm(i)=Kt(i-1)+drift;
end
RKt=1-var(Kt-Ktm)/var(Kt);


%drift; dKt=diff(Kt);drft=mean(dKt)
%SD=sqrt(cov(dKt)/45);
%95% CI Non-d;vn=[3.8 4.2 13.5 4.9 4.2 4.1 8.8 3.9 4.1 4.4 4.7 7.5 3.9 3.9 5.7];
%Sep; vs=[4.7 3.5 9.1 5.9 7.9 6.5 7.9 4.8 6.7 4.7 6.5 6.5 6.0 6.1 5.7];

%var96=[77.4 78.4 75.8 77.1 76.9 78.0 75.5 77.1 78.5 80.5 77.6 78.2 79.0 79.1 76.3];
%var50n=[84.9 86.4 82.3 84.9 84.8 85.9 83.3 84.8 86.2 88.1 85.5 85.3 86.2 86.7 84.9];
%var50s=[84.9 85.4 80.1 83.7 85.8 86.7 81.1 84.6 87.1 90.9 83.0 83.0 85.6 87.5 84.0]; 
%Official G7 2050, vof=[81.2 83.5 81.5 83.0 82.5 80.5]; 

% Figure2, common factor
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
timeh=1951+(1:45);
clf;subplot(2,1,1);plot(age,Bx,'k');
set(gca, 'Ylim', [0 max(Bx)]);
set(gca, 'Xlim', [0 110]);
ylabel('The B(x) in common factor');xlabel('Age')

subplot(2,1,2);plot(timeh,Kt,'k');
set(gca, 'Ylim', [min(Kt) max(Kt)]);
set(gca, 'Xlim', [1952 1996]);
ylabel('The K(t) in common factor');xlabel('Year')
gtext('Figure 2. The common factor values of B(x) and K(t)');
gtext('for 15 low-mortality countries','Fontsize',12)

%print fig2 -dbitmap
print fig2 -deps



nfor=55;nfor5=11;nspt=5;
load c:\users\linan\surrey04\multicountry1\multicountry0\data\usa\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
clf;plot(age,bx);hold;z(1:24)=0;plot(age,z,'--');


%Figure 3. b(x,i) with higative values, Finland, Italy and Switzerland
nfor=55;nfor5=11;nspt=5;
load c:\users\linan\surrey04\multicountry1\multicountry0\data\denmark\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0179
load c:\users\linan\surrey04\multicountry1\multicountry0\data\england\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0115
load c:\users\linan\surrey04\multicountry1\multicountry0\data\france\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0712
load c:\users\linan\surrey04\multicountry1\multicountry0\data\italy\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0950
load c:\users\linan\surrey04\multicountry1\multicountry0\data\japan\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0032
load c:\users\linan\surrey04\multicountry1\multicountry0\data\netherland\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0186
load c:\users\linan\surrey04\multicountry1\multicountry0\data\norway\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%0.0046
load c:\users\linan\surrey04\multicountry1\multicountry0\data\spain\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0485
load c:\users\linan\surrey04\multicountry1\multicountry0\data\sweden\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0359
load c:\users\linan\surrey04\multicountry1\multicountry0\data\sweitzerland\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.1194
load c:\users\linan\surrey04\multicountry1\multicountry0\data\usa\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
min(bx)%-0.0020



load c:\users\linan\surrey04\multicountry1\multicountry0\data\france\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
clf;plot(age,bx,'k>-');hold
load c:\users\linan\surrey04\multicountry1\multicountry0\data\italy\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
plot(age,bx,'k<-');
load c:\users\linan\surrey04\multicountry1\multicountry0\data\sweitzerland\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
plot(age,bx,'k+-');
z(1:24)=0;
plot(age,z,'k--');
legend ('France','Italy','Switzerland')
xlabel('Age');ylabel('The b(x,i) in specific factor');
title('Figure 3. Typical b(x,i) with significant negative values','Fontsize',12)
%print fig3 -dbitmap


%Figure 4. 2 countries with non-divergent k(t,i):
%Japan, US
nfor=55;nfor5=11;nspt=5;
load c:\users\linan\surrey04\multicountry1\multicountry0\data\japan\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
clf;plot(timeh,kt,'ko-');hold;
load c:\users\linan\surrey04\multicountry1\multicountry0\data\usa\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
plot(timeh,kt,'k^-');
legend ('Japan','US')
xlabel('Year');ylabel('The k(t,i) in specific factor');
title('Figure 4. Typical k(t,i) that fits convergent AR(1) model','Fontsize',12)
%print fig4 -dbitmap


%Figure 5. Common-specific factor
iage=6;%aged 20-24, make most notable difference
timef=1995+5*(1:11);timeh=1951+(1:45);
%commen factor
drft=mean(diff(Kt));
for it=1:11
   Ktf(it)=Kt(45)+5*it*drft;
end
for it=1:45%Death rate at age 0
   Kthp(it)=Bx(iage)*(Kt(it)-Kt(45));
end
for it=1:11
   Ktfp(it)=Bx(iage)*(Ktf(it)-Kt(45));
end

%Specific factor
%Japan
load ..\multicountry1\multicountry0\data\japan\m5296.txt;
mx=m5296;
nfor=55;nfor5=11;nspt=5;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
for it=1:45%Death rate at age 0
   KthpJP(it)=Bx(iage)*(Kt(it)-Kt(45))+bx(iage)*(kt(it)-kt(45));
end
for it=1:11
   KtfpJP(it)=Bx(iage)*(Ktf(it)-Kt(45))+bx(iage)*(ktf(it)-kt(45));
end

%US
%Denmark
clear mx
%load ..\multicountry1\multicountry0\data\usa\m5296.txt;
load ..\multicountry1\multicountry0\data\denmark\m5296.txt;
mx=m5296;
nfor=55;nfor5=11;nspt=5;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
for it=1:45%Death rate at age 0
   KthpUS(it)=Bx(iage)*(Kt(it)-Kt(45))+bx(iage)*(kt(it)-kt(45));
end
for it=1:11
   KtfpUS(it)=Bx(iage)*(Ktf(it)-Kt(45))+bx(iage)*(ktf(it)-kt(45));
end

Ktc=[Kthp Ktfp];KtJP=[KthpJP KtfpJP];KtUS=[KthpUS KtfpUS];Time=[timeh timef];
clf;plot(Time, Ktc,'k');hold;plot(Time, KtJP,'ko-');plot(Time, KtUS,'k^-');
legend('[B(20)(K(t)-K(T))], Common factor','[B(20)(K(t)-K(T))+b(20,i)(k(t,i)-k(T,i))], Japan','[B(20)(K(t)-K(T))+b(20,i)(k(t,i)-k(T,i))], Denmark')
xlabel('Year');ylabel('Log[(death rate 20-24,year)/(death rate 20-24,1996)')
gtext('Figure 5. Log of 20-24 death rate relative to value in 1996 for Denmark and Japan')
gtext('illustrating short-term specific factor and long-term common factor in forecasts')
%print fig5 -dbitmap

%Figure 6 non-div Eo
clear
load Eohf
epdm=Eoh(4,:);epdm(46:56)=Eof(4,2,:);%Denmark
epus=Eoh(18,:);epus(46:56)=Eof(18,2,:);%US
timeus(1:45)=1951+(1:45);timeus(46:56)=1995+5*(1:11);
epjp=Eoh(11,:);epjp(46:56)=Eof(11,2,:);%Japan
timejp(1:45)=1951+(1:45);timejp(46:56)=1995+5*(1:11);

clf;plot(timeus,epjp,'ko-','LineWidth',2);hold;plot(timeus,epus,'k','LineWidth',2);plot(timeus,epdm,'k+-','LineWidth',2);

epdm=Eoh(4,:);epdm(46:56)=Eofs(4,2,:);%Denmark
epus=Eoh(18,:);epus(46:56)=Eofs(18,2,:);%US
timeus(1:45)=1951+(1:45);timeus(46:56)=1995+5*(1:11);
epjp=Eoh(11,:);epjp(46:56)=Eofs(11,2,:);%Japan
timejp(1:45)=1951+(1:45);timejp(46:56)=1995+5*(1:11);
plot(timejp,epjp,'ko-');plot(timeus,epus,'k');plot(timeus,epdm,'k+-');
set(gca, 'Ylim', [60 95]);
legend('Coherent for Japan','Coherent for the US','Coherent for Denmark','Separate for Japan','Separate for the US','Separate for Denmark')
xlabel('Year');ylabel('Observed and median forecast of life expectancy')
title('Figure 6. Coherent and separate forecasts of life expectancy','Fontsize',12)
%print fig6 -dbitmap



%Figure 7. 2 countries with divergent k(t,i):
%'Bulgaria','Hungary'
clear
load BXKT; %get common factor
nfor=55;%Number of 1-yr intervals of forecasting
ntrj=500;%Number of trajectories
timeh=1951+(1:45);
load c:\users\linan\surrey04\multicountry1\multicountry0\data\bulgaria\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
clf;plot(timeh,kt,'ko-');hold;
load c:\users\linan\surrey04\multicountry1\multicountry0\data\hungary\m5296.txt;mx=m5296;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
plot(timeh,kt,'k^-');
legend ('Bulgaria','Hungary')
xlabel('Year');ylabel('The k(t,i) in specific factor');
title('Figure 7. Typical k(t,i) that fits neither RW nor AR(1) model','Fontsize',12)
%print fig7 -dbitmap



%Figure8
%Lithuania(CS)
randn('state',0); 
rndgk=randn(ntrj,nfor); %Random var for modelling group Kt, 1-yr
nfor5=11;%5-yr
nffy=1997;nffy5=2000;
nspt=4;%1996+4=2000
ntrj=500;%Number of trajectories

clear mx;
load ..\multicountry1\multicountry0\data\lithuania\m6096.txt;
mx=m6096;
nhly=1996;
timeh=1959+(1:37);
timef=1995+5*(1:11);
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
subplot(2,2,3);plot(timeh,eoh,'k');hold;plot(timef,eofs(2,:),'k');plot(timef,eofs(1,:),'k--');plot(timef,eofs(3,:),'k--');
ylabel('Life expectancy');xlabel('Year');set(gca, 'Ylim', [50 90]);
subplot(2,2,4);plot(timeh,eoh,'k');hold;plot(timef,eof(2,:),'k');plot(timef,eof(1,:),'k--');plot(timef,eof(3,:),'k--');
ylabel('Life expectancy');xlabel('Year');
gtext('Separate LC');
gtext('Coherent LC');
gtext('Figure 8. Coherent and separate forecasts of Lithuania','Fontsize',12) 
print fig8 -dbitmap
print fig8 -dbitmap
print fig8 -deps


















%OLd Figure 3, cancelled
%Figure 3. Goodness of fitting of the common factor

load c:\users\linan\surrey04\multicountry1\multicountry0\data\sweden\m5296.txt;%R=0.87
mxsd=log(m5296);axsd=mean(mxsd);
load c:\users\linan\surrey04\multicountry1\multicountry0\data\denmark\m5296.txt;%R=0.37
mxdm=log(m5296);axdm=mean(mxdm);


for j=1:18
   er(j)=0;
   for i=1:45
   mc(i,j)=Bx(j)*Kt(i);
   msd(i,j)=mxsd(i,j)-axsd(j);
   er(j)=er(j)+(msd(i,j)-mc(i,j))^2;
   end
end
er%max at age=0-1 but marginally
max(abs(msd-mc))%max at iage=15--19 and significantly,


iage=5;%aged 15-19, make most notable difference
%iage=1;
clf;plot(timeh,mc(:,iage));hold;plot(timeh,msd(:,iage),'o');
legend('B(15)K(t), common factor','[log(m(15,t,i))-a(15,i)], Sweden')
xlabel('Year');ylabel('B(15)K(t) and observed values')
title('Figure 3. The worst fitting of the common factor','Fontsize',12)
%print fig3 -dmeta
