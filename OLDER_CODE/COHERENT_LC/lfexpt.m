function [eo]=lfexpt(drt)  %-*-matlab-*-
% lfexpt
% 
%  input 
%     drt -- single vector of ASDR
% 
%  output 
%     eo -- life expect age 0


q(1)=drt(1)/(1+(0.93 -1.7 *drt(1))*drt(1));
q(2)=4*drt(2)/(1+2.5*drt(2)); 

[xxx, nag0]=size(drt);
kk=0;
for k=3:nag0
  q(k) =5*drt(k)/(1+2.5*drt(k));
  if q(k)>=1
	q(k)=1;
  else
	kk=k;                               % At the qx=1, so can stop working on this
  end
end
nag=min(kk+1,nag0);  

% lx
lx(1)=1;
for k=2:(nag+1)
  lx(k)=lx(k-1)*(1-q(k-1)); 
end

% Lx
for i=1:nag-1
  Lx(i)=(lx(i)-lx(i+1))/drt(i);
end
Lx(nag)=lx(nag)/drt(nag);

% Adjust lx for x>=10 (i>=4), according to Tim Oct 18
%    Compute adj for each age ...
c(3)=0;
for i=4:nag-1
  if Lx(i)>0.000001
	c(i)=(1/(48*Lx(i))) * (Lx(i-1)-Lx(i+1))*(drt(i+1)-drt(i-1));
  else
	c(i)=c(i-1);
  end
end

%    ... recalculate lx with adj and mort rates ...
llx=lx;
for i=4:nag-1
  llx(i+1)=llx(i)*exp(-5*(drt(i)+c(i)));
end

%    ... recalculate Lx and qx, use new variables (LLx, qq, etc) now...
for i=1:nag-1
  LLx(i)=(llx(i)-llx(i+1))/drt(i);
  qq(i)=(llx(i)-llx(i+1))/llx(i);
end
qq(nag)=1;
LLx(nag)=LLx(nag-1);
% Finis with weird adjustment.

for i=1:nag
  Tx(i)=sum(LLx(i:nag));
end
eo=Tx(1)/llx(1);
