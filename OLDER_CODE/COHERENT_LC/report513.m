
function [ax0,ax1,bx,cx]=report151(Bx,Kt,mx);
%This code does non-divergent LC forecast, including:
xxx=size(mx);nht=xxx(1);
%Caole-Guo
    for i=1:nht
        for j=1:18;
       drt(j)=mx(i,j);
        end     
        mxt(i,:)=CoaleGt(drt);
        eoh(i)=lfexpt(mxt(i,:));
    end
          
%mxt--matrix of ASDR,
%nffy--first year of forecasting,
%nfor--number of time to be forecasted,
%nfor--number of time to be forecasted in 5-yr interval,
%nspt--different bewteen first year of forscast in 5-yr and the last hist data 
%ntrj--number of trajectories,

xxx=size(mxt);nag=xxx(2);
                    
%(2)SVD 
 %(1.1)make matrix for SVD
lnmx = log(mxt);ax0= mean(lnmx);
for ix = 1:nht,
   for j=1:nag
   lnmx0(ix,j) = lnmx(ix,j)-ax0(j);   
   lnmx1(ix,j) = lnmx(ix,j)-ax0(j)-Bx(j)*Kt(ix);
   end
end
% SVD, where bx is sum to 1
[U S V] = svd(lnmx0,0);bx = V(:,1)/sum(V(:,1));
[U S V] = svd(lnmx1,0);cx = V(:,1)/sum(V(:,1));kt= S(1,1)*U(:,1)*sum(V(:,1));
%End (2)
      

%(5) Estimating a0,a1 and sdckt for the AR(1)-->k(t)=a0+a1*k(t-1)+sdckt*e(t) of a country.
for i=1:nht-1
    X(i,2)=kt(i);X(i,1)=1;y(i)=kt(i+1);    
end
%OLS
b(1)=sum(y);b(2)=y*X(:,2);
a(1,1)=nht-1;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
xxx=(a^-1)*b';
a0=xxx(1);a1=xxx(2);a00=mean(y);
for i=1:nag
   ax1(i)=ax0(i)+cx(i)*(a0/(1-a1));
end
