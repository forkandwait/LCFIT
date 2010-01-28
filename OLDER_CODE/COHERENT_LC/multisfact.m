function [bx,kt,ktf]=multisfact(Bx,Kt,mx,nfor,nfor5,nspt)
% MULTISFACT -- get empirical bx & kt, and projected kt ("ktf") for convergent LC empirical
%  data. Use adjustment with common factor (computed elsewhere and parameterized). 
%  
%  Note that the log mx from which we derive kt etc is adjusted using Bx and Kt from parameters
%  see "NOTE" in the comments for where this happens
%
% input:  
%    Bx -- bx from collective mx
%    Kt -- kt from collective mx
%    nfor -- ??
%    nfor5 -- ???
%    nspt -- ???
% 
% output:
%    bx -- empirical bx
%    kt -- empirical kt
%    ktf -- ??? forecasted kt

  xxx=size(mx);
  nht=xxx(1);
  %Caole-Guo
  for i=1:nht
	for j=1:18;
	  drt(j)=mx(i,j);
	end     
	mxt(i,:)=CoaleGt(drt);
	eoh(i)=lfexpt(mxt(i,:));
  end
  
  % Li Nan:      
  %mxt--matrix of ASDR,
  %nffy--first year of forecasting,
  %nfor--number of time to be forecasted,
  %nfor--number of time to be forecasted in 5-yr interval,
  %nspt--different bewteen first year of forscast in 5-yr and the last hist data 
  %ntrj--number of trajectories,

  xxx=size(mxt);
  nag=xxx(2);
  
  %(2)SVD 
  %(1.1)make matrix for SVD
  lnmx = log(mxt);
  ax= mean(lnmx);
  for ix = 1:nht,
    for j=1:nag
	  lnmx1(ix,j) = lnmx(ix,j)-ax(j)-Bx(j)*Kt(ix); % NOTE!!!  
	end
  end
  % SVD, where bx is sum to 1
  [U S V] = svd(lnmx1,0);
  bx = V(:,1)/sum(V(:,1));
  kt= S(1,1)*U(:,1)*sum(V(:,1));		% empirical kt (to return it later)
  %End (2)
  
  %(4) Estimating drift and sdgkt for the RWD of group
  dKt=diff(Kt);
  drft=mean(dKt); 
  sdgkt=sqrt(cov(dKt));
  %End (4)

  %(5) Estimating a0,a1 and sdckt for the AR(1)-->k(t)=a0+a1*k(t-1)+sdckt*e(t) of a country.
  for i=1:nht-1
    X(i,2)=kt(i);
	X(i,1)=1;
	y(i)=kt(i+1);    
  end
  %OLS
  b(1)=sum(y);
  b(2)=y*X(:,2);
  a(1,1)=nht-1;
  a(1,2)=sum(X(:,2));
  a(2,1)=a(1,2);
  a(2,2)=X(:,2)'*X(:,2);
  xxx=(a^-1)*b';
  a0=xxx(1);
  a1=xxx(2);
  a00=mean(y);
  ktm(1)=kt(1);
  for i=2:nht
	ktm(i)=a0+a1*ktm(i-1);
  end
  for i=1:nht    
	e(i)=kt(i)-ktm(i);   
	e0(i)=kt(i)-mean(kt);
  end
  sdckt=sqrt(cov(e));
  Rsq = 1-cov(e)/cov(e0); 				% R^2
  % Estimating SDT of a0 and a1
  sda0=sdckt/sqrt((nht-1));
  sda1=sdckt/sqrt((kt'*kt));              
  % End (5)


  % Project kt using coefficients from AR(1) ('a0' and 'a1').  Deterministic (just run out the
  %   innovations without any error terms).
  ktf1=zeros(nfor+1);
  ktf1(1)=kt(nht);
  for it=2:(nfor+1),					% Single yr forecast for handle AR(1) simplier
	ktf1(it)=a0+a1*ktf1(it-1);			% AR(1)      
  end

  % make it 5-yr
  ktf(1)=ktf1(nspt);
  for i=2:nfor5
	it=nspt+5*(i-1);
	ktf(i)=ktf1(it);
  end 