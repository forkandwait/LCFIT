%-*-matlab-*-

%(I)Get mxc, Bx and Kt, and country-specific kt for the G7
clear
[mxc,mx,Bx,Kt,bxc,ktc] = multicountry1(39);
yr=1951+(1:39);age(1)=0;age(2)=(1);age(3:24)=5*(1:22);

clf;
subplot(2,1,1);plot(age,Bx);set(gca, 'Ylim', [0 max(Bx)]);legend('B(x)')
title('Figure 1. G5-combined B(x) and K(t)')
subplot(2,1,2);plot(yr,Kt);legend('Adjusted K(t)');
print d:\li\berkeley2\code4\report2(03)1  -dmeta


clf;
plot(age,bxc(1,:));hold;plot(age,bxc(2,:),'--');plot(age,bxc(3,:),'o-');plot(age,bxc(4,:),'x-');
plot(age,bxc(5,:),'^-');%plot(age,bxc(6,:),'-<');plot(age,bxc(7,:),'->');
legend('Canada','France','Germany','Italy','Japan');
xlabel('Age');ylabel('b(x,i)')
title('Figure 2. G5 country-specific b(x,i)')
print d:\li\berkeley2\code4\report2(03)2  -dmeta

clf;
plot(yr,ktc(1,:));hold;plot(yr,ktc(2,:),'--');plot(yr,ktc(3,:),'o-');plot(yr,ktc(4,:),'x-');
plot(yr,ktc(5,:),'^-');%plot(yr,ktc(6,:),'-<');plot(yr,ktc(7,:),'->');
legend('Canada','France','Germany','Italy','Japan');
xlabel('Year');ylabel('k(t,i)')
title('Figure 3. G5 country-specific adjusted k(t,i)')
print d:\li\berkeley2\code4\report2(03)3  -dmeta

%All AR(1);
%All except Japan slower than common, but decelerate 
%Japan faster than common, but decelerate
%All converge
%End (I), all AR(1)!!!


%(II) G7 correlated forecast
nfor=55;%Number of 5-yr intervals of forecasting
ntrj=500;%Number of trajectories
nffy=1991;
randn('state',0); rndgk=randn(ntrj,nfor); %Random var for modelling group Kt

%Canada
ic=1;
[eof,drft,sdgkt,a0,a1,sdckt,Rsq]=multicountry2(ic,Bx,Kt,mxc,rndgk,nfor,ntrj);
eofc=eof;

%France
ic=2;
[eof,drft,sdgkt,a0,a1,sdckt,Rsq]=multicountry2(ic,Bx,Kt,mxc,rndgk,nfor,ntrj);
eoff=eof;

%Germany
ic=3;
[eof,drft,sdgkt,a0,a1,sdckt,Rsq]=multicountry2(ic,Bx,Kt,mxc,rndgk,nfor,ntrj);
eofg=eof;

%Italy
ic=4;
[eof,drft,sdgkt,a0,a1,sdckt,Rsq]=multicountry2(ic,Bx,Kt,mxc,rndgk,nfor,ntrj);
eofi=eof;

%Japan
ic=5;
[eof,drft,sdgkt,a0,a1,sdckt,Rsq]=multicountry2(ic,Bx,Kt,mxc,rndgk,nfor,ntrj);
eofj=eof;

ic=6;
[eof,drft,sdgkt,a0,a1,sdckt,Rsq]=multicountry2(ic,Bx,Kt,mxc,rndgk,nfor,ntrj);
eofuk=eof;

ic=7;
[eof,drft,sdgkt,a0,a1,sdckt,Rsq]=multicountry2(ic,Bx,Kt,mxc,rndgk,nfor,ntrj);
eofus=eof;

%(III) Picture
%Historical (1952--1990) eo
%for ic=1:5
    for ic=1:7
    for i=1:39
        for j=1:24
            drt(j)=mxc(ic,i,j);
        end
        eo(ic,i)=lfexpt(drt);
    end
end

yrsh=1951+(1:39);yrsf=1990+(1:55);


yr=[yrsh yrsf];eoc=[eo(1,:) eofc(2,:)];eof=[eo(2,:) eoff(2,:)];eog=[eo(3,:) eofg(2,:)];
eoi=[eo(4,:) eofi(2,:)];eoj=[eo(5,:) eofj(2,:)];
eouk=[eo(6,:) eofuk(2,:)];eous=[eo(7,:) eofus(2,:)];

clf;
plot(yr,eoc);hold;plot(yr,eof,'--');plot(yr,eog,'o-');plot(yr,eoi,'x-');plot(yr,eoj,'^-');
plot(yr,eouk,'<');plot(yr,eous,'>')
legend('Canada','France','Germany','Italy','Japan','UK','US');

xlabel('Year');ylabel('Historical and mean forecast of Eo')
title('Figure 4. Correlated forecasts of Eo for G5 countries')

print rplnondiv1(3) -dmeta


print d:\li\berkeley2\code4\report2(03)4  -dmeta
%End (III)

%(IV) Separete forecasts
yrs=1951+(1:39);agm=0;nffy=1991;nfor=13;ntrj=500;stok0=zeros(ntrj,nfor);
for ic=1:5
    ic
    for i=1:39
        for j=1:24
            mx0(i,j)=mxc(ic,i,j);
        end
    end    
    [mxh,mxf0]=mortG0(mx0,yrs,agm,nffy,nfor,ntrj);
    [kt9750,kt500,kt250,e9750,e500,e250]=pict(mxf0,stok0);%kt
    eos(ic,:)=e500;
    e9750-e250
end

yrf5=1986+5*(1:13);
yr5=[yrs yrf5];

eosc=[eo(1,:) eos(1,:)];eosf=[eo(2,:) eos(2,:)];eosg=[eo(3,:) eos(3,:)];
eosi=[eo(4,:) eos(4,:)];eosj=[eo(5,:) eos(5,:)];

%save corEo mxc eofc eoff eofg eofi eofj eosc eosf eosg eosi eosj 
load corEo


clf;
plot(yr5,eosc);hold;plot(yr5,eosf,'--');plot(yr5,eosg,'o-');plot(yr5,eosi,'x-');plot(yr5,eosj,'^-');
set(gca, 'Xlim', [1950 2050]);
legend('Canada','France','Germany','Italy','Japan');

xlabel('Year');ylabel('Historical and mean forecast of Eo')
title('Figure 5. Separate forecasts of Eo for G5 countries')
print d:\li\berkeley2\code4\report2(03)5  -dmeta

%End(IV)