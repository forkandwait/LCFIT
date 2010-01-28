function [nmx]= CoaleGt(drt)
% CoaleGt
%
% Input: "drt" 18 age-specific death rates for 0, 1-4, 5-9,...80-84.
%
% Output: "nmx" 22 age-specific death rates for 0, 1-4, 5-9,...100-104.
%
% Note: We get lx, Lx for 0,...80-84; using Lifetable(mx_ages, mx_data)

A=110;

%Here is CG for 1-yr mx(i), i=85,86,....,A;
k85=.2*log(drt(18)/drt(17));
m84=drt(18)*exp(3*k85);
mA=0.66+drt(17);
%mA=1,male;mA=.8,female
HA=A-85+1;
s=(log(mA/m84)-HA*k85)*2/(HA*(HA-1));
for i=1:HA
   a=84+i;%the age over 85
   H=a-85+1;
   mx(i)=m84*exp(H*k85+s*H*(H-1)/2);
end
%Get 1-yr q(i)
for i=1:HA;%85,86,...,125,
   %q(i)=2*mx(i)/(2+mx(i));
   q(i)=1-exp(-(mx(i) + .008*(mx(i)^2)));
end
%Get 1-yr lx(i)
lx(1)=1; %1 means 85
nlx(1)=1;
for i=1:HA;%lx, 85,86,...,125,126
   lx(i+1)=lx(i)*(1-q(i));
end
%Get 5-yr lx and nLx
HB=(HA-1)/5;%the max age of 5-yr
for i=1:HB;%nLx:85,90,...120
   ki1=1+5*(i-1);
   ki2=i;
   nLx(ki2)=0;
   for j=ki1:ki1+4
      nLx(ki2)=nLx(ki2)+0.5*(lx(j)+lx(j+1));
   end
   nlx(ki2+1)=lx(ki1+5);
end


%get 5-yr mx
for i=1:18
   nmx(i)=drt(i);
end
%for i=19:18+HB%HB=5
for i=19:23 %use as G7
   nmx(i)=(nlx(i-18)-nlx(i-17))/nLx(i-18);
end
nmx(24)=mx(HA);%the last open interval

