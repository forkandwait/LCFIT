% -*-matlab-*-

% (I)Get mxc, Bx and Kt, and country-specific kt for the G7
clear
load ./sweden/BxKt;     % get common factor
nfor=100;               % Number of 1-yr intervals of forecasting
ntrj=500;               % Number of trajectories
randn('state',10);      % To be indep. 
rndgk=randn(ntrj,nfor); % Random var for modelling group Kt, 1-yr. Only used by passing to multicountry2GC 
nfor5=20;               % 5-yr
nffy5=2005;
nspt=3;                 % 2002+3=2005
nht=53;

% Get R^2 for RW
drift=mean(diff(Kt));
Ktm(1)=Kt(1);
for i=2:nht
    Ktm(i)=Kt(i-1)+drift;
end
RKt=1-var(Kt-Ktm)/var(Kt);

load ./sweden/mxm5002.txt;
load ./sweden/mxf5002.txt;
load ./sweden/pxm5002.txt;
load ./sweden/pxf5002.txt;

%Male(C)  multicountry2GC, multicountry2S, multicountry2GC (residuals)
ic=1
mx=mxm5002;

% following yields empirical e_0, 5/50/95% projected e_0, and the drift and stdev of Kt. Does NOT use residuals.
[eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt); % 2MIN
Eoh(ic,:)=eoh;
Eof(ic,1:3,1:nfor5)=eof;
nhly=2002;

% following yields matrix of e_0 for forecasted death rates, 5% + 50% + 95% in rows, projected years
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);  % Separate forecast
Eofs(ic,1:3,1:nfor5)=eofs;

% Output the results (male) to the matlab prompt
%eoh(nht)%eo(2002)=77.7950 output
%eof(2,nfor5)%eo(2010)=89.7131 output
%eof(1,nfor5)-eof(3,nfor5)%%95CI(2010)=6.7308 output
%eofs(2,nfor5)%eo(2010)=86.8288
%eofs(1,nfor5)-eofs(3,nfor5)%95CI(2010)=6.5419

%female(CS)
ic=2
mx=mxf5002;
[eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;
Eof(ic,1:3,1:nfor5)=eof;
nhly=2002;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj); % Separate forecast
Eofs(ic,1:3,1:nfor5)=eofs;

% Output results for female
% eoh(nht)%eo(2002)=82.2286
% eof(2,nfor5)%eo(2010)=92.7059
% eof(1,nfor5)-eof(3,nfor5)%95CI(2010)=5.7455
% eofs(2,nfor5)%eo(2000)=94.3997
% eofs(1,nfor5)-eofs(3,nfor5)%95CI(2010)=8.5795

%save ./sweden/EohfRESULTS Eoh Eof Eofs%save results

em=Eoh(1,:);
em(nht+1:nht+nfor5)=Eof(1,2,:);
ems(1:nfor5)=Eofs(1,2,:);   % male

ef=Eoh(2,:);
ef(nht+1:nht+nfor5)=Eof(2,2,:);
efs(1:nfor5)=Eofs(2,2,:);   % female

time(1:nht)=1949+(1:nht);
times(1:nfor5)=2000+5*(1:nfor5);
clf;
plot(time,em(1:nht),'k');
hold;
plot(time,ef(1:nht),'k.-');
plot(times,em(nht+1:nht+nfor5),'ko-');
plot(times,ems,'k^-');
plot(times,ef(nht+1:nht+nfor5),'ko-');
plot(times,efs,'k^-');
legend('Historical male','Historical female','Non-divergent forecasts','Separate forecasts')
xlabel('Year','Fontsize',12);
ylabel('Observed and median forecast of life expectancy')
title('Figure 1. Non-divergent and separate forecasts of life expectancy, Sweden','Fontsize',12)
print fig1 -deps  % Required by Demography

x=ef-em;
mean(x(1:nht))

%Difference of Eo:  2002   2010(Non-dic.) 2010(separate)  
%                   4.4         2.7              7.6