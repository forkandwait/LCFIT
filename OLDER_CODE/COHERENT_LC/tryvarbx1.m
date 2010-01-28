

function [bx,cx] = tryvarbx1(nhts,nht1,nht,mxo);
%For 1952--96 (Germany)

%Caole-Guo
for i=1:nht
    for j=1:18;
       drt(j)=mxo(i,j);
    end     
    mx(i,:)=CoaleGt(drt);
end

for i=1:nht1%First half
   for j=1:24
      lnmxo(i,j)=log(mx(i,j));
   end
end
ax=mean(lnmxo);%average decline rate
for ix = 1:nht1
   lnmx1(ix,:) = lnmxo(ix,:)-ax;
end
% SVD, 
[U S V] = svd(lnmx1,0);bx = V(:,1)/sum(V(:,1));K= S(1,1)*U(:,1)*sum(V(:,1));
epr(1)=S(1,1)^2/trace(S'*S);
%adjust k
drft=mean(diff(K));
for i=(nht1+1):nht
   K(i)=K(i-1)+drft;
end
for i=1:nht
   ko=K(i);
   mx1=mx(i,:);
   [kt1]=fiteo(ax,bx,ko,mx1);
   kt(i)=kt1;    
end%End


%Second half
for i=(nht1+1):nht
   i1=i+2-nht1;
   lnmxs(i1,:)=log(mx(i,:));
end
ax1=mean(lnmxs);
for i =(nht1+1):nht
   i1=i+2-nht1;
   for j=1:24
      %lnmxs1(i1,j) = lnmxo(i,j)-ax(j)-bx(j)*K(i);
      lnmxs1(i1,j) = log(mx(i,j))-ax1(j);
   end
end
[U S V] = svd(lnmxs1,0); bx2 = V(:,1)/sum(V(:,1));
k2= S(1,1)*U(:,1)*sum(V(:,1));

%clf;plot(bx);hold;plot(cx,'--')

%Use the first half to describe the second
%Error matrix 
for i =(nht1+1):nht
   i1=i-nht1;
   for j=1:24
      %lnmxs1(i1,j) = lnmxo(i,j)-ax(j)-bx(j)*K(i);
      er(i1,j) = log(mx(i,j))-ax(j)-bx(j)*kt(i);
   end
end

[U S V] = svd(er,0);
if mean(diff(U(:,1)))<0;
   cx = V(:,1);h= S(1,1)*U(:,1);
else
   cx = -V(:,1);h= -S(1,1)*U(:,1);
end
   
z=bx2-bx;cxo=z/sqrt((z'*z));
zo(1:24)=0;

nht2=nht-nht1;
for i=1:nht2
   g(i)=h(i)/kt(i+nht1);
end

for i=1:nht2-2
    X(i,2)=g(i);X(i,1)=1;y(i)=g(i+1);    
end
%OLS
b(1)=sum(y);b(2)=y*X(:,2);
a(1,1)=nht2-2;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
xxx=(a^-1)*b';
a0=xxx(1);a1=xxx(2);a00=mean(y);
gm(1)=g(1);
      for i=2:nht2
          gm(i)=a0+a1*gm(i-1);
       end
       for i=1:nht2-1    
       e(i)=g(i)-gm(i);   
       e0(i)=g(i)-mean(g);
       end
       sdckt=sqrt(cov(e));
       Rsq=1-cov(e)/cov(e0)%R^2
       %Estimating SDT of a0 and a1
       sda0=sdckt/sqrt((nht-1));sda1=sdckt/sqrt((g*g'));              
       %End (5)
       
ginf=a0/(1-a1);cxi=ginf*cx;
det=min(bx+ginf*cx);
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
time=nhts+nht1-1+(1:nht-nht1);
clf;subplot(2,1,1);plot(age,cxi);hold;plot(age,z,'o');plot(age,zo,'--');
legend('b(x,\infty)-b(x,1)','b(x,2)-b(x,1)');xlabel('Age')  
%subplot(2,1,2);plot(ek);
subplot(2,1,2);plot(time,g,'o');hold;plot(time,gm);legend('Observed g(t)','AR(1) modeled g(t)');
xlabel('Years in the second half period')