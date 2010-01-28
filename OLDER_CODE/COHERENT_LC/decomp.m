

%(I)Get mxc, Bx and Kt, and country-specific kt for the G7
clear
[mxc,mx,Bx,Kt,bxc,ktc] = multicountry1(39);

[bxco,ktco] = singlecountry(39);

yr=1951+(1:39);age(1)=0;age(2)=(1);age(3:24)=5*(1:22);

%Compare Bx
clf
for i=1:5
subplot(3,2,i)
plot(age,Bx);hold;plot(age,bxco(i,:),'.-');
%clf;plot(age,Bx);hold;plot(age,bxco(5,:),'.-');
%For Japan, mort declined faster at older ages by Bx then by bxco, 
%so the bxc and ktc is a compensition to the gap of BxKt and bxcoktco, 
%not a model of bxco change over time.
%For others,revised.
end


%Is BxKt+bxcktc a decomposition of bxcoktco?
for ic=1:5
    mo=bxco(ic,:)'*ktco(ic,:);
    m1=bxc(ic,:)'*ktc(ic,:)+Bx*Kt;
ss=size(mo);
xx=0;yy=0;
for i=1:ss(1)
    for j=1:ss(2)
        xx=xx+mo(i,j)^2;
        yy=yy+(mo(i,j)-m1(i,j))^2;
    end
end
RT(ic)=1-yy/xx;%0.94-0.98, Yes, BxKt+bxcktc is a decomposition of bxcoktco.
end


%Decomposition
for i=1:5
deltabx(i,:)=bxco(i,:)-Bx';
deltakt(i,:)=ktco(i,:)-Kt;
end

clf;
plot(age,deltabx(1,:));hold;plot(age,deltabx(2,:),'--');plot(age,deltabx(3,:),'o-');plot(age,deltabx(4,:),'x-');
plot(age,deltabx(5,:),'^-');%plot(age,bxc(6,:),'-<');plot(age,bxc(7,:),'->');
legend('Canada','France','Germany','Italy','Japan');
xlabel('Age');ylabel('\Delta(b(x,i))')
title('Figure 1. G5 country-specific \Delta(b(x,i))')
print rplnondiv1(1) -dmeta

clf;
plot(yr,deltakt(1,:));hold;plot(yr,deltakt(2,:),'--');plot(yr,deltakt(3,:),'o-');plot(yr,deltakt(4,:),'x-');
plot(yr,deltakt(5,:),'^-');%plot(age,bxc(6,:),'-<');plot(age,bxc(7,:),'->');
legend('Canada','France','Germany','Italy','Japan');
xlabel('Year');ylabel('\Delta(k(t,i))')
title('Figure 2. G5 country-specific \Delta(k(t,i)');
print rplnondiv1(2) -dmeta


%Delta(k(t,i)) are similar to k(t,i)



for ic=1:5
    mcon=Bx*Kt;%common matrix
    ms=Bx*deltakt(ic,:);%speed effect
    ma=deltabx(ic,:)'*Kt;%age effect
    mc=deltabx(ic,:)'*deltakt(ic,:);%cross effect
    x=0;ys=0;ya=0;yc=0;ysa=0;ysc=0;yac=0;ysac=0;
     for i=1:ss(2)
        for j=1:ss(1)
        lnmxc(i,j) = log(mxc(ic,i,j));
        end
    end
    for j=1:ss(1)
       xx=0;
        for i=1:ss(2) 
        xx=xx+log(mxc(ic,i,j));
        end
       ax(ic,j)=xx/39;
   end
   for i=1:ss(2)
       for j=1:ss(1)
        lnmxc1(i,j)=log(mxc(ic,i,j))-ax(ic,j);
        end
    end
    for i=1:ss(1)
        for j=1:ss(2)
            x=x+lnmxc1(j,i)^2;
            ys=ys+(lnmxc1(j,i)-mcon(i,j)-ms(i,j))^2;
            ya=ya+(lnmxc1(j,i)-mcon(i,j)-ma(i,j))^2;
            yc=yc+(lnmxc1(j,i)-mcon(i,j)-mc(i,j))^2;
            ysa=ysa+(lnmxc1(j,i)-mcon(i,j)-ms(i,j)-ma(i,j))^2;
            ysc=ysc+(lnmxc1(j,i)-mcon(i,j)-ms(i,j)-mc(i,j))^2;
            yac=yac+(lnmxc1(j,i)-mcon(i,j)-ma(i,j)-mc(i,j))^2;
            ysac=ysac+(lnmxc1(j,i)-mcon(i,j)-ms(i,j)-ma(i,j)-mc(i,j))^2;
        end
    end
    Rs(ic)=1-ys/x;
    Ra(ic)=1-ya/x;
    Rc(ic)=1-yc/x;
    Rsa(ic)=1-ysa/x;
    Rsc(ic)=1-ysc/x;
    Rac(ic)=1-yac/x;
    Rsac(ic)=1-ysac/x;
    R(ic,1)=Rs(ic);R(ic,2)=Ra(ic);R(ic,3)=Rc(ic);R(ic,4)=Rsa(ic);R(ic,5)=Rsc(ic);R(ic,6)=Rac(ic);R(ic,7)=Rsac(ic);
end

            
    








