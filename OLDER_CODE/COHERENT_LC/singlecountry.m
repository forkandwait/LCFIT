

function [bxco,ktco] = singlecountry(iger);
%For G7 1952--90 (Germany)


clear
nc0=7;%number of initial countries
nc=5;%number of countries
mxc=zeros(7,39,24);%country-specific mx
pxc=zeros(7,39,18);%country-specific px

%Canada
clear m5094m m5094f p5094m p5094f pxt
load multicountry/data/canada/m5094m.dat
load multicountry/data/canada/m5094f.dat
load multicountry/data/canada/p5094m.dat
load multicountry/data/canada/p5094f.dat
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:39 %Get sex-combined death rates, for 1952--90
   for j=1:18
      pxc(1,i,j)=pxt(i+2,j);
      mxc(1,i,j)=(m5094m(i+2,j)*p5094m(i+2,j)+m5094f(i+2,j)*p5094f(i+2,j))/pxt(i+2,j);
   end
end

%France
clear m5094m m5094f p5094m p5094f pxt
load multicountry/data/france/m5094m.dat
load multicountry/data/france/m5094f.dat
load multicountry/data/france/p5094m.dat
load multicountry/data/france/p5094f.dat
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:39 %Get sex-combined death rates
   for j=1:18
      pxc(2,i,j)=pxt(i+2,j);
      mxc(2,i,j)=(m5094m(i+2,j)*p5094m(i+2,j)+m5094f(i+2,j)*p5094f(i+2,j))/pxt(i+2,j);
   end
end

%Germany
clear m5094m m5094f p5094m p5094f pxt
load multicountry/data/germany/m5094m.dat
load multicountry/data/germany/m5094f.dat
load multicountry/data/germany/p5094m.dat
load multicountry/data/germany/p5094f.dat
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:39%Get sex-combined death rates
   for j=1:18
      pxc(3,i,j)=pxt(i,j);
      mxc(3,i,j)=(m5094m(i,j)*p5094m(i,j)+m5094f(i,j)*p5094f(i,j))/pxt(i,j);
   end
end

%Italy
clear m5094m m5094f p5094m p5094f pxt
load multicountry/data/italy/m5094m.dat
load multicountry/data/italy/m5094f.dat
load multicountry/data/italy/p5094m.dat
load multicountry/data/italy/p5094f.dat
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:39%Get sex-combined death rates
   for j=1:18
      pxc(4,i,j)=pxt(i+1,j);
      mxc(4,i,j)=(m5094m(i+1,j)*p5094m(i+1,j)+m5094f(i+1,j)*p5094f(i+1,j))/pxt(i+1,j);
   end
end

%Japan
clear m5094m m5094f p5094m p5094f pxt
load multicountry/data/japan/m5094m.dat
load multicountry/data/japan/m5094f.dat
load multicountry/data/japan/p5094m.dat
load multicountry/data/japan/p5094f.dat
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:39 %Get sex-combined death rates
   for j=1:18
      pxc(5,i,j)=pxt(i+2,j);
      mxc(5,i,j)=(m5094m(i+2,j)*p5094m(i+2,j)+m5094f(i+2,j)*p5094f(i+2,j))/pxt(i+2,j);
   end
end

%UK
clear m5094m m5094f p5094m p5094f pxt
load multicountry/data/uk/m5094m.dat
load multicountry/data/uk/m5094f.dat
load multicountry/data/uk/p5094m.dat
load multicountry/data/uk/p5094f.dat
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:39 %Get sex-combined death rates
   for j=1:18
      pxc(6,i,j)=pxt(i+2,j);
      mxc(6,i,j)=(m5094m(i+2,j)*p5094m(i+2,j)+m5094f(i+2,j)*p5094f(i+2,j))/pxt(i+2,j);
   end
end

%US
clear m5094m m5094f p5094m p5094f pxt
load multicountry/data/us/m5094m.dat
load multicountry/data/us/m5094f.dat
load multicountry/data/us/p5094m.dat
load multicountry/data/us/p5094f.dat
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:39 %Get sex-combined death rates
   for j=1:18
      pxc(7,i,j)=pxt(i+2,j);
      mxc(7,i,j)=(m5094m(i+2,j)*p5094m(i+2,j)+m5094f(i+2,j)*p5094f(i+2,j))/pxt(i+2,j);
   end
end

%Caole-Guo
for ic=1:nc0
    for i=1:39
        for j=1:18;
       drt(j)=mxc(ic,i,j);
    end     
    mxcg=CoaleGt(drt);
    mxc(ic,i,19:24)=mxcg(19:24);
end
end


%SVD for single country

for ic=1:nc%For G5
    for i=1:39
        for j=1:24
        lnmxc(i,j) = log(mxc(ic,i,j));
        end
    end
    
    for j=1:24
       xx=0;
        for i=1:39 
        xx=xx+log(mxc(ic,i,j));
        end
       ax(ic,j)=xx/39;
   end
   
   for i=1:39
       for j=1:24
        lnmxc1(i,j)=log(mxc(ic,i,j))-ax(ic,j);
        end
    end
    [U S V] = svd(lnmxc1,0);bxco(ic,:) = (V(:,1)/sum(V(:,1)))';k(ic,:)= (S(1,1)*U(:,1)*sum(V(:,1)))';
    bx=(V(:,1)/sum(V(:,1)));
    %epr(1)=S(1,1)^2/trace(S'*S);%Explanation ratio of log(mx)-ax;
    xx1=0;xx2=0;xx3=0;
    for i=1:39
        for j=1:24
        lnmxc(i,j) = log(mxc(ic,i,j));
        xx1=xx1+(log(mxc(ic,i,j))-ax(ic,j))^2;
        xx2=xx2+(log(mxc(ic,i,j))-ax(ic,j)-bx(j)*k(ic,i))^2;
        end
    end
    1-xx2/xx1
    for i=1:39
    kt=k(ic,i);
    for j=1:24
        mx1(j)=mxc(ic,i,j);
    end
    axo=ax(ic,:);
   [kt1]=fiteo(axo,bx,kt,mx1);   
   ktco(ic,i)=kt1;
   end
end

%ktc=ktc';save ktc.txt ktc -ascii
