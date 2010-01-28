
function [ciak,cik]=AR1var2(v,c0,sec0,c1,sec1,sigma,ntrj,nfor);
if c0>0
 %CI of average k
  if c1+sec1*v<1
   ciak(1)=(c0-v*sec0)/(1-c1+v*sec1);
   ciak(2)=(c0+v*sec0)/(1-c1-v*sec1);
  else
   ciak(1)=(c0-v*sec0)/(1-c1+v*sec1);
   ciak(2)=0;
  end
%CI for k
  if c1+sec1*v<1
   cik(1)=(c0-v*sec0)/(1-c1+v*sec1)-v*sqrt(sigma^2/(1-(c1-v*sec1)^2));
   cik(2)=(c0+v*sec0)/(1-c1-v*sec1)+v*sqrt(sigma^2/(1-(c1+v*sec1)^2));
  else
   cik(1)=(c0-v*sec0)/(1-c1+v*sec1)-v*sqrt(sigma^2/(1-(c1-v*sec1)^2));
   cik(2)=0;
 end
else %C0<0
   %CI of average k
  if c1+sec1*v<1
   ciak(1)=(c0-v*sec0)/(1-c1+v*sec1);
   ciak(2)=(c0+v*sec0)/(1-c1-v*sec1);
  else
   ciak(1)=(c0-v*sec0)/(1-c1+v*sec1);
   ciak(2)=0;
  end
%CI for k
  if c1+sec1*v<1
   cik(1)=(c0-v*sec0)/(1-c1+v*sec1)+v*sqrt(sigma^2/(1-(c1-v*sec1)^2));
   cik(2)=(c0+v*sec0)/(1-c1-v*sec1)-v*sqrt(sigma^2/(1-(c1+v*sec1)^2));
  else
   cik(1)=(c0-v*sec0)/(1-c1+v*sec1)+v*sqrt(sigma^2/(1-(c1-v*sec1)^2));
   cik(2)=0;
  end
end






