

%(I)Get mxc, Bx and Kt, and country-specific kt for the G7
clear
load BXKT; %get common factor


%Denmark(CS, k(inf)=17.01)
ic=1
clear mx;
load d:\multicountry\data\denmark\m5296.txt;
mx=m5296;
[ax0,ax1,bx,cx]=report513(Bx,Kt,mx);
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
zz(1:24)=1;
for i=1:24
   rax01(i)=exp(ax1(i))/exp(ax0(i));
end
clf;
subplot(2,1,1);plot(age,ax0);hold;plot(age,ax1,'o');
legend('a(x,i)','a(x,i)+b(x,i)*k(infinite,i)')
subplot(2,1,2);plot(age,rax01);hold;plot(age,zz,'--');
legend('exp[a(x,i)+b(x,i)*k(infinity,i)]/exp[a(x,i)]')
gtext('Figure 1. Denmark');
print report5(03)1 -dmeta




%England(CS,k(inf)=1.00)
ic=2
clear mx;
load d:\multicountry\data\england\m5296.txt;
mx=m5296;
[ax0,ax1,bx,cx]=report513(Bx,Kt,mx);
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
zz(1:24)=1;
for i=1:24
   rax01(i)=exp(ax1(i))/exp(ax0(i));
end
clf;
subplot(2,1,1);plot(age,ax0);hold;plot(age,ax1,'o');
legend('a(x,i)','a(x,i)+b(x,i)*k(infinite,i)')
subplot(2,1,2);plot(age,rax01);hold;plot(age,zz,'--');
legend('exp[a(x,i)+b(x,i)*k(infinity,i)]/exp[a(x,i)]')
gtext('Figure 6. England');
print report5(03)6 -dmeta

%GermanyE(CS,k(inf)=1.50)
ic=3
clear mx;
load d:\multicountry\data\germanye\m5696.txt;
mx=m5696;
Kto=Kt(5:45);
[ax0,ax1,bx,cx]=report513(Bx,Kto,mx);
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
zz(1:24)=1;
for i=1:24
   rax01(i)=exp(ax1(i))/exp(ax0(i));
end
clf;
subplot(2,1,1);plot(age,ax0);hold;plot(age,ax1,'o');
legend('a(x,i)','a(x,i)+b(x,i)*k(infinite,i)')
subplot(2,1,2);plot(age,rax01);hold;plot(age,zz,'--');
legend('exp[a(x,i)+b(x,i)*k(infinity,i)]/exp[a(x,i)]')
gtext('Figure 2. East Germany');
print report5(03)2 -dmeta

%Japan(CS,k(inf)=-5.63)
ic=4
clear mx;
load d:\multicountry\data\japan\m5296.txt;
mx=m5296;
[ax0,ax1,bx,cx]=report513(Bx,Kt,mx);
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
zz(1:24)=1;
for i=1:24
   rax01(i)=exp(ax1(i))/exp(ax0(i));
end
clf;
subplot(2,1,1);plot(age,ax0);hold;plot(age,ax1,'o');
legend('a(x,i)','a(x,i)+b(x,i)*k(infinite,i)')
subplot(2,1,2);plot(age,rax01);hold;plot(age,zz,'--');
legend('exp[a(x,i)+b(x,i)*k(infinity,i)]/exp[a(x,i)]')
gtext('Figure 3. Janap');
print report5(03)3 -dmeta

%Netherlands(CS,k(inf)=1.55))
ic=5
clear mx;
load d:\multicountry\data\netherland\m5296.txt;
mx=m5296;
[ax0,ax1,bx,cx]=report513(Bx,Kt,mx);
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
zz(1:24)=1;
for i=1:24
   rax01(i)=exp(ax1(i))/exp(ax0(i));
end
clf;
subplot(2,1,1);plot(age,ax0);hold;plot(age,ax1,'o');
legend('a(x,i)','a(x,i)+b(x,i)*k(infinite,i)')
subplot(2,1,2);plot(age,rax01);hold;plot(age,zz,'--');
legend('exp[a(x,i)+b(x,i)*k(infinity,i)]/exp[a(x,i)]')
gtext('Figure 7. Netherlands');
print report5(03)7 -dmeta

%Norway(CS,k(inf)=2.01)
ic=6
clear mx;
load d:\multicountry\data\norway\m5296.txt;
mx=m5296;
[ax0,ax1,bx,cx]=report513(Bx,Kt,mx);
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
zz(1:24)=1;
for i=1:24
   rax01(i)=exp(ax1(i))/exp(ax0(i));
end
clf;
subplot(2,1,1);plot(age,ax0);hold;plot(age,ax1,'o');
legend('a(x,i)','a(x,i)+b(x,i)*k(infinite,i)')
subplot(2,1,2);plot(age,rax01);hold;plot(age,zz,'--');
legend('exp[a(x,i)+b(x,i)*k(infinity,i)]/exp[a(x,i)]')
gtext('Figure 4. Norway');
print report5(03)4 -dmeta


%Usa(CS,k(inf)=4.45)
ic=7
load d:\multicountry\data\usa\m5296.txt;
mx=m5296;
[ax0,ax1,bx,cx]=report513(Bx,Kt,mx);
age(1)=0;age(2)=1;age(3:24)=5*(1:22);
zz(1:24)=1;
for i=1:24
   rax01(i)=exp(ax1(i))/exp(ax0(i));
end
clf;
subplot(2,1,1);plot(age,ax0);hold;plot(age,ax1,'o');
legend('a(x,i)','a(x,i)+b(x,i)*k(infinite,i)')
subplot(2,1,2);plot(age,rax01);hold;plot(age,zz,'--');
legend('exp[a(x,i)+b(x,i)*k(infinity,i)]/exp[a(x,i)]')
gtext('Figure 5. USA');
print report5(03)5 -dmeta


