
%Denmark
clear
v=.67;
%v=1.96;
c0=.14;sec0=.10;c1=.99;sec1=.04;sigma=.69;ntrj=1000;nfor=200;
[ciak,cik]=AR1var2(v,c0,sec0,c1,sec1,sigma,ntrj,nfor)



%England
clear
v=.67;
%v=1.96;
c0=.07;sec0=.06;c1=.93;sec1=.05;sigma=.40;ntrj=1000;nfor=200;
[ciak,cik]=AR1var2(v,c0,sec0,c1,sec1,sigma,ntrj,nfor)

w1=25;w2=50;w3=75;%50% CI
[k1,k2,k3]=AR1var1(w1,w2,w3,c0,sec0,c1,sec1,sigma,ntrj,nfor);
clf;plot(k3,'.-');hold;plot(k2);plot(k1,'--');
Title('Figure 1. The 50% confidence intervals of k(t,i) for England')
xlabel('Years');ylabel('k(t,i)');
legend('Above which there are 25% trajectories','Medium','Below which there are 25% trajectories');
print comment(4)1 -dmeta

w1=2.5;w2=50;w3=97.5;%95% CI
[k1,k2,k3]=AR1var1(w1,w2,w3,c0,sec0,c1,sec1,sigma,ntrj,nfor);
clf;plot(k3,'.-');hold;plot(k2);plot(k1,'--');
Title('Figure 2. The 95% confidence intervals of k(t,i) for England')
xlabel('Years');ylabel('k(t,i)');
legend('Above which there are 2.5% trajectories','Medium','Below which there are 2.5% trajectories');
print comment(4)2 -dmeta


%GermanyE
clear
v=.67;
%v=1.96;
c0=.1;sec0=.15;c1=.94;sec1=.08;sigma=.96;ntrj=1000;nfor=200;
[ciak,cik]=AR1var2(v,c0,sec0,c1,sec1,sigma,ntrj,nfor)


%Japan
clear
v=.67;
%v=1.96;
c0=-.27;sec0=.09;c1=.95;sec1=.02;sigma=.56;ntrj=1000;nfor=200;
[ciak,cik]=AR1var2(v,c0,sec0,c1,sec1,sigma,ntrj,nfor)


%Netherland
clear
v=.67;
%v=1.96;
c0=.1;sec0=.05;c1=.93;sec1=.04;sigma=.35;ntrj=1000;nfor=200;
[ciak,cik]=AR1var2(v,c0,sec0,c1,sec1,sigma,ntrj,nfor)


%Norway
clear
v=.67;
%v=1.96;
c0=.1;sec0=.11;c1=.95;sec1=.06;sigma=.74;ntrj=1000;nfor=200;
[ciak,cik]=AR1var2(v,c0,sec0,c1,sec1,sigma,ntrj,nfor)


%US
clear
v=.67;
%v=1.96;
c0=.09;sec0=.06;c1=.98;sec1=.05;sigma=.41;ntrj=1000;nfor=200;
[ciak,cik]=AR1var2(v,c0,sec0,c1,sec1,sigma,ntrj,nfor)


