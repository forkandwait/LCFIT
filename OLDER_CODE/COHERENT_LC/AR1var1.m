
function [k1,k2,k3]=AR1var1(w1,w2,w3,c0,sec0,c1,sec1,sigma,ntrj,nfor);
%(6)Forcsting

randn('state',1);rndgc=randn(ntrj,nfor); 
randn('state',2);rndgce=randn(ntrj,1);%estimating errors are independent to ...
  stokc=zeros(ntrj,nfor+1);stokc(:,1)=0;
for tind =1:ntrj,
   for yind0=1:nfor,%Single yr forecast for handle AR(1) simplier
      zzz=c0+sec0*rndgce(tind)+(c1+sec1*rndgce(tind))*stokc(tind,yind0);
      stokc(tind,yind0+1)=zzz+sigma*rndgc(tind,yind0);   
   end
end
k1(1)=0;k2(1)=0;k3(1)=0;
for i=2:nfor+1,%Single yr forecast for handle AR(1) simplier
   k1(i)=prctile(stokc(:,i),w1);
   k2(i)=prctile(stokc(:,i),w2);
   k3(i)=prctile(stokc(:,i),w3);
end 





