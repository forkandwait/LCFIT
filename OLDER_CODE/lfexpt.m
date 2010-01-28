%%%%%      10/19/2001
%
%  This m script give eo from mx
%  From Tim
%%%%%
function [eo]=lfexpt(drt)
nag0=size(drt);
      q(1)=drt(1)/(1+(0.93 -1.7 *drt(1))*drt(1));
      q(2)=4*drt(2)/(1+2.5*drt(2)); 
      kk=0;
      for k=3:nag0(2)
         q(k) =5*drt(k)/(1+2.5*drt(k));
         if q(k)>=1
             q(k)=1;
         else
             kk=k;
         end
      end
    nag=min(kk+1,nag0(2));  
      
      %lx
      lx(1)=1;
      for k=2:(nag+1)
         lx(k)=lx(k-1)*(1-q(k-1)); 
      end
      %Lx
      for i=1:nag-1
          Lx(i)=(lx(i)-lx(i+1))/drt(i);
      end
      Lx(nag)=lx(nag)/drt(nag);
      
      %Get new lx for x>=10 (i>=4), according to Tim Oct 18
      for i=4:nag-1
          c(i)=(1/(48*Lx(i)))*(Lx(i-1)-Lx(i+1))*(drt(i+1)-drt(i-1));
      end
      llx=lx;
      for i=4:nag-1
          llx(i+1)=llx(i)*exp(-5*(drt(i)+c(i)));
      end
      for i=1:nag-1
          LLx(i)=(llx(i)-llx(i+1))/drt(i);
          qq(i)=(llx(i)-llx(i+1))/llx(i);
      end
      qq(nag)=1;
      LLx(nag)=llx(nag)/drt(nag);
      for i=1:nag
          Tx(i)=sum(LLx(i:nag));
          Ex(i)=Tx(i)/llx(i);
      end
      eo=Ex(1);
          
      %age(1)=0;age(2)=1;age(3:22)=5*(1:20);
      %clear X
      %X(:,1)=age(1:nag)';X(:,2)=drt(1:nag)';X(:,3)=qq(1:nag)';X(:,4)=llx(1:nag)';
      %X(:,5)=LLx(1:nag)';X(:,6)=Tx(1:nag)';X(:,7)=Ex(1:nag)';
      
      
      