
function [mxf]=mort(mx,nhly,nffy,nfor,ntrj)


nfst=nffy-nhly;
nstp=5;
%Inputs age-specific death rates mx(time,age)
%and parameters nfor--number of time to be forecasted 
%               nfst--first time of forecast from the hostorical data,
%               nstp--length of time interval in forecasting,
%               ntrj--number of trajectories.
%Returns forecasted age-specific death rates mxf(trajectory,time,age).
%E.g.,
%Historical mortality in XXXX--1993 each year, forecasting 50 years 
%starting at 1995 with 5-year time interval and 1000 trajectries.
%Inputs: nfor=10(50/5),nfst=2(1995-1993),nstp=5,ntrj=1000,
%Returns: Mortality in 1995, 2000, 2005, ... 2045;

%(1) Data
xxx=size(mx);
nht=xxx(1); %Get sizes of historical time
[nmx]= CoaleGt(mx(1,:));
mxt=NaN*zeros(nht,size(nmx,2));
for it=1:nht %Using Coale-Guo to get 85-89,...100-104.
   drt=mx(it,:);
   [nmx]= CoaleGt(drt);
   mxt(it,:)=nmx ;% extended by CG
end;
nag=22;

%(2)Lee-carter model 
 %(1.1)make matrix for SVD
lnmx = log(mxt);
ax= mean(lnmx);
for ix = 1:nht,
   lnmx1(ix,:) = lnmx(ix,:)-ax;
end;
% SVD, where bx is sum to 1
[U S V] = svd(lnmx1,0);
bx = V(:,1)/sum(V(:,1));
k= S(1,1)*U(:,1)*sum(V(:,1));
%End of (1.1)
%(1.2)To modify kt by fitting Eo, need fiteo.m
for i=1:nht
   kt=k(i);
   mx1=mxt(i,:);
   [kt1]=fiteo(ax,bx,kt,mx1);
   kteo(i)=kt1;    
end;%End of (1.2)
%End of (1)

%(2)Forcsting
%(2.0)Get the random numbers rdn(ntrj,nfor)
%start_state = randn('state');
%save ran_start start_state;
load ran_start
randn('state', start_state);
rnd1= randn(ntrj,nfor);

xm=mean(rnd1);%Normalize by ntrj
for i=1:nfor
    for j=1:ntrj
      rnd2(j,i)=(rnd1(j,i)-xm(i));
    end
    for j=1:ntrj
      rdn(j,i)=rnd2(j,i)/sqrt(rnd2(:,i)'*rnd2(:,i)/(ntrj-1));
    end
end;

% Fit the random walk model
dkteo=diff(kteo); drft=mean(dkteo); sdktnd=sqrt(cov(dkteo));
% (2.1)Now generate stochastic trajectories of ktnd:
stok=zeros(ntrj,nfor+1);%stok(:,1)=ktnd(nht);
for tind =1:ntrj,
   for yind0=1:nfor,
      yind=nstp*(yind0-1)+nfst;
       stok(tind,yind0+1)=kteo(nht)+yind*drft+(yind+yind^2/nht)^.5*sdktnd*rdn(tind,yind0);
      %here the error of estimating drft term is included by (yrs/nht)      
   end;					
end;

stok(:,1)=kteo(nht); %End of (2.1)
% _ (2.2)mx 
for tt=1:nfor
  for tind=1:ntrj
    for j=1:nag
      drtf(j)=mxt(nht,j)*exp((stok(tind,tt+1)-kteo(nht))*bx(j)');
    end;
    mxf(tind,tt,:)=drtf;      
  end;
end; %End of (2.2)

 
 clf;%pictures
 subplot(2,2,1)%ax
 age(1)=0;age(2)=1;age(3:22)=5*(1:20); 
 plot(age,ax);ylabel('a(x)');xlabel('Age')
 subplot(2,2,2)%bx
 age(1)=0;age(2)=1;age(3:22)=5*(1:20); 
 plot(age,bx);;ylabel('b(x)');xlabel('Age')
 
[kt95,kt50,kt5,e95,e50,e5]=pict(mxf,stok);%kt
timeh=nhly-nht+(1:nht);timef=nffy-5+5*(1:nfor);
subplot(2,2,3)
plot(timeh,kteo);hold;plot(timef,kt95(2:nfor+1),'--');
plot(timef,kt50(2:nfor+1),'--');plot(timef,kt5(2:nfor+1),'--');
set(gca, 'Xlim', [timeh(1) timef(nfor)]);
ylabel('Ajusted (by Eo) k(t) and its 90% forecast');xlabel('Year')

 for i=1:nht%Eo
    eoh(i)=lfexpt(mxt(i,:));
 end
subplot(2,2,4)
plot(timeh,eoh);hold;plot(timef,e95,'--');
plot(timef,e50,'--');plot(timef,e5,'--');
set(gca, 'Xlim', [timeh(1) timef(nfor)]);
ylabel('Eo and its 90% forecast');xlabel('Year') 

keyboard
 
%for i=1:nag
 %   drt(i)=mxt(45,i)*exp(bx(i)*(kt50(13)-kteo(45)));
 %end

