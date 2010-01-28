

%(I)Get mxc, Bx and Kt, and country-specific kt for the G7
clear
load c:\limpi\multicountry1\data\BxKt; %get common factor
nfor=100;%Number of 1-yr intervals of forecasting
ntrj=1000;%Number of trajectories
randn('state',10);%To be independent with others 
rndgk=randn(ntrj,nfor); %Random var for modelling group Kt, 1-yr
nfor5=20;%5-yr
nffy5=2005;
nspt=5;%2000+9=2005
nht=51;
nhly=2000;

%Denmark(CS)
ic=1
clear mx;
load c:\limpi\multicountry1\data\denmark\mx5000.txt;
mx=mx5000;
[eoh,eof,drft,sdgkt,sdckt,a0,sda0,a1,sda1,kinf]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
%a0=0.0205;a1=0.0777;a1=0.9222;sda1=0.0965;;kinf=0.2641;
Eoh(ic,:)=eoh;Eof(ic,1:3,1:nfor5)=eof;
eoh(nht)%eo(2000)=76.8142
eof(2,nfor5)%Non-div eo(2100)=88.5676
eof(1,nfor5)-eof(3,nfor5)%95CI(Non-div)=8.2098
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:nfor5)=eofs;
eofs(2,nfor5)%86.8939
eofs(1,nfor5)-eofs(3,nfor5)%13.0248

%Norway(C)
ic=2
clear mx;
load c:\limpi\multicountry1\data\norway\mx5000.txt;
mx=mx5000;
[eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,:)=eoh;Eof(ic,1:3,1:nfor5)=eof;
eoh(nht)%eo(2000)=78.5097
eof(2,nfor5)%Non-div eo(2100)=89.2614
eof(1,nfor5)-eof(3,nfor5)%95CI(Non-div)=7.3923
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:nfor5)=eofs;
eofs(2,nfor5)%87.0176
eofs(1,nfor5)-eofs(3,nfor5)%7.3503

%Sweden(C)
ic=3
clear mx;
load c:\limpi\multicountry1\data\sweden\mx5000.txt;
mx=mx5000;
[eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:nfor5)=eof;
eoh(nht)%eo(2000)=79.6017
eof(2,nfor5)%Non-div eo(2100)=90.0333
eof(1,nfor5)-eof(3,nfor5)%95CI(Non-div)=7.2109
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:nfor5)=eofs;
eofs(2,nfor5)%91.1321
eofs(1,nfor5)-eofs(3,nfor5)%7.8007


save Eohf Eoh Eof Eofs%save results

load Eohf
load c:\limpi\multicountry1\data\BxKt
%Making Fifures
%Figure1, common factor
nht=51;
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
timeh=1949+(1:nht);
clf;subplot(2,1,1);plot(age,Bx);
set(gca, 'Ylim', [0 max(Bx)]);
set(gca, 'Xlim', [0 110]);
ylabel('B(x)');xlabel('Age')

subplot(2,1,2);plot(timeh,Kt);
set(gca, 'Ylim', [min(Kt) max(Kt)]);
set(gca, 'Xlim', [1950 2000]);
ylabel('K(t)');xlabel('Time')
gtext('Figure 1. The common factor of the 3 north-European countries','Fontsize',12)

print fig1 -dmeta

%Canceled Figure 2. Goodness of fitting of the common factor
%Figure 2. b(x,i) with higative values, Finland, Italy and Switzerland

nfor=100;nfor5=20;nspt=5;
load c:\limpi\multicountry1\data\denmark\mx5000.txt;
mx=mx5000;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
clf;plot(age,bx);hold;z(1:24)=0;plot(age,z,'--');
xlabel('Age');ylabel('b(x,i)');
title('Figure 2. The b(x,i) with negative values, Denmark','Fontsize',12)
print fig2 -dmeta


%Figure 3. Six countries with non-divergent k(t,i):
%Denmark
timef=2000+5*(1:20);
clf;plot(timeh,kt);hold;plot(timef,ktf,'o-');
xlabel('Year');ylabel('k(t,i)');
title('Figure 3. Historical and AR(1) forecasted k(t,i), Denmark','Fontsize',12)
print fig3 -dmeta


%Cancel Figure 5-7

%Figure4.
ed=Eoh(1,:);ed(nht+1:nht+nfor5)=Eof(1,2,:);%Denmark
en=Eoh(2,:);en(nht+1:nht+nfor5)=Eof(2,2,:);%Norway
es=Eoh(3,:);es(nht+1:nht+nfor5)=Eof(3,2,:);%Sweden
eds=Eoh(1,:);eds(nht+1:nht+nfor5)=Eofs(1,2,:);
ens=Eoh(2,:);ens(nht+1:nht+nfor5)=Eofs(2,2,:);
ess=Eoh(3,:);ess(nht+1:nht+nfor5)=Eofs(3,2,:);

time(1:nht)=1949+(1:nht);
times(1:nfor5)=2000+5*(1:nfor5);
timehs=[time times];
clf;plot(timehs,ed);hold;plot(timehs,en,'+-');plot(timehs,es,'o-');
set(gca, 'Ylim', [70 95]);
legend('Denmark','Norway','Sweden');
xlabel('Year');ylabel('Observed and mean-forecast of life expectancy')
title('Figure 4. Non-divergent forecasts of life expectancy','Fontsize',12)
print fig4 -dmeta

clf;plot(timehs,eds);hold;plot(timehs,ens,'+-');plot(timehs,ess,'o-');
legend('Denmark','Norway','Sweden');
set(gca, 'Ylim', [70 95]);
xlabel('Year');ylabel('Observed and mean-forecast of life expectancy')
title('Figure 5. Separate forecasts of life expectancy','Fontsize',12)

print fig5 -dmeta




%Figure 7. Common-specific factor
iage=10;%aged 5-9, make most notable difference
nht=51;nfor5=20;
timeh=1949+(1:nht);timef=2000+5*(1:nfor5);
%commen factor
drft=mean(diff(Kt));
for it=1:nfor5
   Ktf(it)=Kt(nht)+5*it*drft;
end
for it=1:nht%Death rate at age 0
   Kthp(it)=Bx(iage)*(Kt(it)-Kt(nht));
end
for it=1:nfor5
   Ktfp(it)=Bx(iage)*(Ktf(it)-Kt(nht));
end

%Specific factor
%Denmark
load c:\limpi\multicountry1\data\denmark\mx5000.txt;
mx=mx5000;
nspt=5;
[bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt);
for it=1:nht%Death rate at age 0
   KthpD(it)=Bx(iage)*(Kt(it)-Kt(nht))+bx(iage)*(kt(it)-kt(nht));
end
for it=1:nfor5
   KtfpD(it)=Bx(iage)*(Ktf(it)-Kt(nht))+bx(iage)*(ktf(it)-kt(nht));
end

Ktc=[Kthp Ktfp];KtD=[KthpD KtfpD];Time=[timeh timef];
clf;plot(Time, Ktc);hold;plot(Time, KtD,'o-');

legend('[B(20)(K(t)-K(T))]','[B(20)(K(t)-K(T))+b(20,i)(k(t,i)-k(T,i))], Japan','[B(20)(K(t)-K(T))+b(20,i)(k(t,i)-k(T,i))], US')
xlabel('Time');ylabel('Common and common-specific factors')
title('Figure 7. Common and common-specific factors of age gourp 20-24')
%print multiF7 -dmeta
