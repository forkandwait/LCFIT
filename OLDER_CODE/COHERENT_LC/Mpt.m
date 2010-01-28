
clear
%(I) Data 

nt=10;
pm(1:13,1:nt,1:51)=0;dm(1:13,1:nt,1:51)=0;pf(1:13,1:nt,1:51)=0;df(1:13,1:nt,1:51)=0;
%Country 1-13; yr 1992-2001; age 80-130

pmc(1:13,1:31)=0;dmc(1:13,1:31)=0;pfc(1:13,1:31)=0;pfc(1:13,1:31)=0;
%country 1-13; cohort age 85-115(2001), born in 1876-1885


%(1) Austria
ic=1;
load ..\Mplateau1\austria\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\austria\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort


%(2) Denmark
ic=2;
load ..\Mplateau1\denmark\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\denmark\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(3) England and Wales
ic=3;
load ..\Mplateau1\EW\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\EW\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(4) Finland
ic=4;
load ..\Mplateau1\finland\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\finland\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort


%(5) France
ic=5;
load ..\Mplateau1\france\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\france\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(6) GermanyW
ic=6;
load ..\Mplateau1\germanyW\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\germanyW\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(7) Italy
ic=7;
load ..\Mplateau1\italy\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\italy\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(8) Japan
ic=8;
load ..\Mplateau1\japan\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\japan\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(9) Netherlands
ic=9;
load ..\Mplateau1\netherlands\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\netherlands\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(10) Norway
ic=10;
load ..\Mplateau1\norway\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\norway\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(11) Sweden
ic=11;
load ..\Mplateau1\sweden\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\sweden\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(12) Switzerland
ic=12;
load ..\Mplateau1\switzerland\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(47-nt:46,:);dm(ic,:,:)=d(47-nt:46,:);%yr 1992-2001
[pc,dc] = trnc(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\switzerland\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(47-nt:46,:);df(ic,:,:)=d(47-nt:46,:);
[pc,dc] = trnc(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort

%(13) US
ic=13;
load ..\Mplateau1\us\m.txt
[p,d]=trn(m);pm(ic,:,:)=p(44-nt:43,:);dm(ic,:,:)=d(44-nt:43,:);%yr 1992-2001
[pc,dc] = trncus(m);pmc(ic,:)=pc;dmc(ic,:)=dc;%cohort
load ..\Mplateau1\us\f.txt
[p,d]=trn(f);pf(ic,:,:)=p(44-nt:43,:);df(ic,:,:)=d(44-nt:43,:);
[pc,dc] = trncus(f);pfc(ic,:)=pc;dfc(ic,:)=dc;%cohort





%(II.1) For country-combined cohorts
clear drtmc drtfc
for ia=1:31%age 85--115
 xxm=0;yym=0;xxf=0;yyf=0;
 for ic=1:13%Number of countries
         xxm=xxm+pmc(ic,ia);
         yym=yym+dmc(ic,ia);
         xxf=xxf+pfc(ic,ia);
         yyf=yyf+dfc(ic,ia);
 end
 pmoc(ia)=xxm;pfoc(ia)=xxf;dmoc(ia)=yym;dfoc(ia)=yyf;
 drtmc(ia)=yym/xxm;
 drtfc(ia)=yyf/xxf;
end
%age=84+(1:31);
%clf;plot(age,drtmc,'k+-');hold;plot(age,drtfc,'ko-')

ns=16;ns1=22;nt=29;%male, 13countries, ns>23 the relative error >10%;
%ns=16;ns1=20;nt=27;%male, 12 countries, ns>20 the relative error >10%;nt>27 relative error >60%
%ns=19;ns1=23;nt=31;%male US
clear drtl drth
for ib=ns:nt
    mx=drtmc(ns);np=pmoc(ib);
    [mxl,mxh,nmi]=binomconf(np,mx);
    drtl(ib)=mxl;drth(ib)=mxh;
end
age=84+(1:31);
clf;plot(age(1:ns1),drtmc(1:ns1),'k+-','LineWidth',2.5);hold;plot(age(ns+1:nt),drtmc(ns+1:nt),'k+','LineWidth',2.5);
plot(age(ns:nt),drtl(ns:nt),'k+--');plot(age(ns:nt),drth(ns:nt),'k+--');
   
ns=21;ns1=25;nt=31;%female, 13 countries, ns>25 the relative error >10%;
%ns=21;ns1=23;nt=30;%female, 12 countries, nt>23 the relative error >10%; nt>30 relative error >60%
%ns=20;ns1=25;nt=31;%female US
clear drtl drth
for ib=ns:nt
    mx=drtfc(ns);np=pfoc(ib);
    [mxl,mxh,nmi]=binomconf(np,mx);
    drtl(ib)=mxl;drth(ib)=mxh;
end
plot(age(1:ns1),drtfc(1:ns1),'ko-','LineWidth',2.5);plot(age(ns+1:nt),drtfc(ns+1:nt),'ko','LineWidth',2.5);
plot(age(ns:nt),drtl(ns:nt),'ko--');plot(age(ns:nt),drth(ns:nt),'ko--');
set(gca, 'Ylim', [.1 .8]);
xlabel('Age');ylabel('Death rate')



%ns--larger than which relative error >.1
clear drtl drth
ns=16;ns1=22;nt=29;%male 13
%ns=16;ns1=20;nt=29;%male 12
%ns=19;ns1=22;%male US
for ib=ns:29
    mx=drtmc(ns);np=pmoc(ib);
    [mxl,mxh,nmi]=binomconf(np,mx);
    if abs((mxl-drtmc(ns))/drtfc(ns))<.1 
    ib%show ib when relative error (CI95%) <10%
    end
    if abs((mxh-drtmc(ns))/drtfc(ns))<.1
    ib%show ib when relative error (CI95%) <10%
    end
end

ns=21;ns1=25;nt=31;%female, 13 countries, ns>25 the relative error >10%;
%ns=21;ns1=23;nt=30;%female, 12 countries, nt>23 the relative error >10%; nt>30 relative error >60%
%ns=20;ns1=26;nt=31;%female US
clear drtl drth
for ib=ns:31
    mx=drtfc(ns);np=pfoc(ib);
    [mxl,mxh,nmi]=binomconf(np,mx);
    if abs((mxl-drtfc(ns))/drtfc(ns))<.1%(10%)
    ib%show ib when relative error (CI95%) <10%
    end
    if abs((mxh-drtfc(ns))/drtfc(ns))<.1
    ib%show ib when relative error (CI95%) <10%
    end
end







%(III) The US proportion
for ia=1:31%age 85--115
 xxm=0;yym=0;xxf=0;yyf=0;
 for ic=1:13%Number of countries
         xxm=xxm+pmc(ic,ia);
         xxf=xxf+pfc(ic,ia);    
 end
 prom(ia)=pmc(13,ia)/xxm;
 prof(ia)=pfc(13,ia)/xxf;
end
agem=84+(1:23);agef=84+(1:25);

clf; plot(agem,prom(1:23),'k+-'); hold; plot(agef,prof(1:25),'ko-')
xlabel('Age');ylabel('The fraction of the US population')
%US has lower mortality than the other 12 populations.




%(II) For country-combined cohorts
clear drtmc drtfc
for ia=1:15%two-yr age group: 85-86, 87-88, ..., 113-114.
 hh=2*(ia-1)+1;   
 xxm=0;yym=0;xxf=0;yyf=0;
 for ic=13:13%Number of countries
         xxm=xxm+pmc(ic,hh)+pmc(ic,hh+1);
         yym=yym+dmc(ic,hh)+dmc(ic,hh+1);
         xxf=xxf+pfc(ic,hh)+pfc(ic,hh+1);
         yyf=yyf+dfc(ic,hh)+dfc(ic,hh+1);
 end
 pmoc(ia)=xxm;pfoc(ia)=xxf;dmoc(ia)=yym;dfoc(ia)=yyf;
 drtmc(ia)=yym/xxm;
 drtfc(ia)=yyf/xxf;
end
age2=84+2*(1:15);
clf;plot(age2,drtmc,'k+-');hold;plot(age2,drtfc,'ko-')



%(VI) For country-combined period
for ia=1:31%
 xxm=0;yym=0;xxf=0;yyf=0;
 for ic=1:13%Number of countries
     for it=1:10
         xxm=xxm+pm(ic,it,ia+5);
         yym=yym+dm(ic,it,ia+5);
         xxf=xxf+pf(ic,it,ia+5);
         yyf=yyf+df(ic,it,ia+5);
     end
 end
 pmo(ia)=xxm;pfo(ia)=xxf;dmo(ia)=yym;dfo(ia)=yyf;
 drtm(ia)=yym/xxm;
 drtf(ia)=yyf/xxf;
end
age=84+(1:31);

%clf;plot(age,drtm,'+-');hold;plot(age,drtf,'o-');
%ns--at which the pop=500
ns=24;;nt=31;%male, 13 countries, nt>40 will make mean death<1
%ns=22;nt=26;%male, 12 countries, nt>40 will make mean death<1
for ib=ns:nt
    mx=drtm(ns);np=pmo(ib);
    [mxl,mxh,nmi]=binomconf(np,mx);
    if nmi<10
    ib%show ib when the mean death <10
    end
    drtl(ib)=mxl;drth(ib)=mxh;dm(ib)=nmi;
end
clf;plot(age(1:ns),drtm(1:ns),'k+-','LineWidth',2.5);hold;plot(age(ns+1:nt),drtm(ns+1:nt),'k+','LineWidth',2.5);
plot(age(ns:nt),drtl(ns:nt),'k+--');plot(age(ns:nt),drth(ns:nt),'k+--');


ns=26;nt=31;%female, 13 countries
%ns=25;nt=29;%female, 12 countries
for ib=ns:nt
    mx=drtf(ns);np=pfo(ib);
    [mxl,mxh,nmi]=binomconf(np,mx);
     if nmi<10
    ib%show ib when the mean death <10
    end
    drtl(ib)=mxl;drth(ib)=mxh;
end
plot(age(1:ns),drtf(1:ns),'ko-','LineWidth',2.5);plot(age(ns+1:nt),drtf(ns+1:nt),'ko','LineWidth',2.5);
plot(age(ns:nt),drtl(ns:nt),'ko--');plot(age(ns:nt),drth(ns:nt),'ko--');
set(gca, 'Ylim', [.1 .8]);
xlabel('Age');ylabel('Death rate')

