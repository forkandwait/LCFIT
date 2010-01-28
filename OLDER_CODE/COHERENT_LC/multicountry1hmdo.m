

function [mxc,mx,Bx,Kt,bxc,ktc] = multicountry114(iger);
%For 1952--96 (Germany)

nc0=14;%number of initial countries
nht=45;%historical years
%nc=5;%number of countries
mxc=zeros(nc0,nht,24);%country-specific mx, until age 105--110
pxc=zeros(nc0,nht,18);%country-specific px
%Austria
load c:\limpi\multicountry0\data\austria\m5296.txt;load c:\limpi\multicountry0\data\austria\p5296.txt
mxc(1,1:nht,1:18)=m5296;pxc(1,1:nht,1:18)=p5296;
%Canada
load c:\limpi\multicountry0\data\canada\m5296.txt;load c:\limpi\multicountry0\data\canada\p5296.txt
mxc(2,1:nht,1:18)=m5296;pxc(2,1:nht,1:18)=p5296;
%denmark
load c:\limpi\multicountry0\data\denmark\m5296.txt;load c:\limpi\multicountry0\data\denmark\p5296.txt
mxc(3,1:nht,1:18)=m5296;;pxc(3,1:nht,1:18)=p5296;
%england
load c:\limpi\multicountry0\data\england\m5296.txt;load c:\limpi\multicountry0\data\england\p5296.txt
mxc(4,1:nht,1:18)=m5296;pxc(4,1:nht,1:18)=p5296;
%finland
load c:\limpi\multicountry0\data\finland\m5296.txt;load c:\limpi\multicountry0\data\finland\p5296.txt
mxc(5,1:nht,1:18)=m5296;pxc(5,1:nht,1:18)=p5296;
%france
load c:\limpi\multicountry0\data\france\m5296.txt;load c:\limpi\multicountry0\data\france\p5296.txt
mxc(6,1:nht,1:18)=m5296;pxc(6,1:nht,1:18)=p5296;
%germanyw
load c:\limpi\multicountry0\data\germanyw\m5296.txt;load c:\limpi\multicountry0\data\germanyw\p5296.txt
mxc(7,1:nht,1:18)=m5296;pxc(7,1:nht,1:18)=p5296;
%italy
load c:\limpi\multicountry0\data\italy\m5296.txt;load c:\limpi\multicountry0\data\italy\p5296.txt
mxc(8,1:nht,1:18)=m5296;pxc(8,1:nht,1:18)=p5296;
%Japan
load c:\limpi\multicountry0\data\japan\m5296.txt;load c:\limpi\multicountry0\data\japan\p5296.txt
mxc(9,1:nht,1:18)=m5296;pxc(9,1:nht,1:18)=p5296;
%netherland
load c:\limpi\multicountry0\data\netherland\m5296.txt;load c:\limpi\multicountry0\data\netherland\p5296.txt
mxc(10,1:nht,1:18)=m5296;pxc(10,1:nht,1:18)=p5296;
%norway
load c:\limpi\multicountry0\data\norway\m5296.txt;load c:\limpi\multicountry0\data\norway\p5296.txt
mxc(11,1:nht,1:18)=m5296;pxc(11,1:nht,1:18)=p5296;
%sweden
load c:\limpi\multicountry0\data\sweden\m5296.txt;load c:\limpi\multicountry0\data\sweden\p5296.txt
mxc(12,1:nht,1:18)=m5296;pxc(12,1:nht,1:18)=p5296;
%sweitzerland
load c:\limpi\multicountry0\data\sweitzerland\m5296.txt;load c:\limpi\multicountry0\data\sweitzerland\p5296.txt
mxc(13,1:nht,1:18)=m5296;pxc(13,1:nht,1:18)=p5296;
%usa
load c:\limpi\multicountry0\data\usa\m5296.txt;load c:\limpi\multicountry0\data\usa\p5296.txt
mxc(nc0,1:nht,1:18)=m5296;pxc(nc0,1:nht,1:18)=p5296;

%Caole-Guo
for ic=1:nc0
    for i=1:nht
        for j=1:18;
       drt(j)=mxc(ic,i,j);
    end     
    mxcg=CoaleGt(drt);
    mxc(ic,i,19:24)=mxcg(19:24);
end
end

%Making mx for total group    
for i=1:nht %Get sex-combined death rates
   for j=1:18
       p=0;d=0;
       for ic=1:nc0%For nc0
           p=p+pxc(ic,i,j);
           d=d+pxc(ic,i,j)*mxc(ic,i,j);
       end
       drt(j)=d/p;%mx for nc0
   end
   mxcg=CoaleGt(drt);%Caole-Guo
   mx(i,1:24)=mxcg;
end

%SVD for nc0 combined
lnmx = log(mx);Ax= mean(lnmx);
for ix = 1:nht,
   lnmx1(ix,:) = lnmx(ix,:)-Ax;
end
% SVD, where bx is sum to 1
[U S V] = svd(lnmx1,0);Bx = V(:,1)/sum(V(:,1));K= S(1,1)*U(:,1)*sum(V(:,1));
epr(1)=S(1,1)^2/trace(S'*S);
% Fit eo
for i=1:nht
   kt=K(i);mx1=mx(i,:);
   [Kt(i)]=fiteo(Ax,Bx,kt,mx1);    
end


%SVD for single country

for ic=1:nc0%For nc0
     for i=1:nht
        for j=1:24
        lnmxc(i,j) = log(mxc(ic,i,j));
        end
     end
    
     for j=1:24
       xx=0;
        for i=1:nht 
        xx=xx+log(mxc(ic,i,j));
        end
       ax(ic,j)=xx/nht;
     end
   
     for i=1:nht
       for j=1:24
          lnmxc2(i,j)=log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i);
          lnmxc1(i,j)=log(mxc(ic,i,j))-ax(ic,j);
        end
     end
    %Separate 
    [U S V] = svd(lnmxc1,0);
    k(ic,:)= (S(1,1)*U(:,1)*sum(V(:,1)))';bxo=(V(:,1)/sum(V(:,1)));
    for i=1:nht
     kt=k(ic,i);mx1(1:24)=mxc(ic,i,1:24);
    [kto(i)]=fiteo(ax(ic,:),bxo,kt,mx1);    
    end
     xx1=0;xx2=0;
    for i=1:nht
        for j=1:24
        lnmxc(i,j) = log(mxc(ic,i,j));
        xx1=xx1+(log(mxc(ic,i,j))-ax(ic,j))^2;
        xx2=xx2+(log(mxc(ic,i,j))-ax(ic,j)-bxo(j)*kto(i))^2;
        end
    end
    epr(ic,1)=1-xx2/xx1;   
    %Group
    [U S V] = svd(lnmxc2,0);
    kc(ic,:)= (S(1,1)*U(:,1)*sum(V(:,1)))';bxc=(V(:,1)/sum(V(:,1)));
    %for i=1:nht%Give up adjusting k(t,i)
    %   kt=kc(ic,i);mx1(1:24)=mxc(ic,i,1:24);
    %   axo=ax(ic,:)'+Bx*Kt(i);
    %   [ktc(i)]=fiteoc(axo',bxc,kt,mx1,i);     
    % end
     xx1=0;xx2=0;xx3=0;
    for i=1:nht
        for j=1:24
        lnmxc(i,j) = log(mxc(ic,i,j));
        xx1=xx1+(log(mxc(ic,i,j))-ax(ic,j))^2;
        xx2=xx2+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i))^2;
        xx3=xx3+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i)-bxc(j)*kc(ic,i))^2;
     %   xx3=xx3+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i)-bxc(j)*ktc(i))^2;
        end
     end
     epr(ic,2)=1-xx2/xx1;
     epr(ic,3)=1-xx3/xx1;%epr(ic,3)=1-xx3/xx1;
     bxC(ic,:)=bxc';
     
     %AR(1) coef.
       for i=1:nht-1
         X(i,2)=kc(ic,i);X(i,1)=1;y(i)=kc(ic,i+1);    
       end
     %OLS  
       b(1)=sum(y);b(2)=y*X(:,2);
       a(1,1)=nht-1;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
       xxx=(a^-1)*b';
       a0=xxx(1);a1=xxx(2);a00=mean(y);
       ar(ic)=a1;
       Ktc(ic,1)=kc(ic,1);
       for i=2:nht
          %Ktc(ic,i)=a0+a1*Ktc(ic,i-1);
          Ktc(ic,i)=a0+a1*kc(ic,i-1);
       end
       for i=1:nht
          %e(i)=y(i)-a0-a1*X(i,2);
       e(i)=kc(ic,i)-Ktc(ic,i);   
       e0(i)=kc(ic,i)-mean(kc(ic,:));
       end
       sdckt=sqrt(cov(e));
       Rsq(ic)=1-cov(e)/cov(e0);%R^2
       
 ic   
end


clf;plot(kc(ic,:));hold;plot(Ktc(ic,:),'r')
 
 
 
