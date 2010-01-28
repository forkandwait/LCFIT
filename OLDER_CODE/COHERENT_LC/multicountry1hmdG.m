

function [epr,ar,rsq] = multicountry1hmdG(Bx,Kt,mx,nht);

%Caole-Guo
    for i=1:nht
        for j=1:18;
       drt(j)=mx(i,j);
        end     
    mxcg=CoaleGt(drt);
    mx(i,19:24)=mxcg(19:24);
   end

%SVD for single country
     for i=1:nht
        for j=1:24
        lnmxc(i,j) = log(mx(i,j));
        end
     end
     for j=1:24
       xx=0;
        for i=1:nht 
        xx=xx+log(mx(i,j));
        end
       ax(j)=xx/nht;
     end
     for i=1:nht
       for j=1:24
          lnmxc2(i,j)=log(mx(i,j))-ax(j)-Bx(j)*Kt(i);
          lnmxc1(i,j)=log(mx(i,j))-ax(j);
        end
     end
   [U S V] = svd(lnmxc1,0);
    epr(1)=S(1,1)^2/trace(S'*S);%Ro
     %Group  
    [U S V] = svd(lnmxc2,0);
    kt= (S(1,1)*U(:,1)*sum(V(:,1)))';bx=(V(:,1)/sum(V(:,1)));
    xx1=0;xx2=0;xx3=0;
    for i=1:nht
        for j=1:24
        xx1=xx1+(log(mx(i,j))-ax(j))^2;
        xx2=xx2+(log(mx(i,j))-ax(j)-Bx(j)*Kt(i))^2;
        xx3=xx3+(log(mx(i,j))-ax(j)-Bx(j)*Kt(i)-bx(j)*kt(i))^2;
        end
     end
     epr(2)=1-xx2/xx1;%Rc;
     epr(3)=1-xx3/xx1;%Rcs
     %AR(1) coef.
       for i=1:nht-1
         X(i,2)=kt(i);X(i,1)=1;y(i)=kt(i+1);    
       end
     %OLS  
       b(1)=sum(y);b(2)=y*X(:,2);
       a(1,1)=nht-1;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
       xxx=(a^-1)*b';
       a0=xxx(1);a1=xxx(2);a00=mean(y);
       ar=a1;
       Ktc(1)=kt(1);
       for i=2:nht
          Ktc(i)=a0+a1*Ktc(i-1);
       end
       for i=1:nht
          %e(i)=y(i)-a0-a1*X(i,2);
       e(i)=kt(i)-Ktc(i);   
       e0(i)=kt(i)-mean(kt);
       end
       sdckt=sqrt(cov(e));
       rsq=1-cov(e)/cov(e0);%R^2
       
 

