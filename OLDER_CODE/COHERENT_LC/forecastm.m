
%Inputs age-specific death rates mx(time,age)
clear
load chinamx.txt; %data of China
mx=chinamx;
yrs=[1974 1981 1990];
nffy=1995;
ntrj=1000;agm=19;
nfor=10;%Minimum years (85) for cohort life expectancy
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);

clear 
load usmx.txt; %data of US
mx=usmx;
xxx=size(mx);nht=xxx(1);
yrs=1949+(1:nht);
nffy=1995;ntrj=1000;agm=19;
nfor=12;%Minimum years (85) for cohort life expectancy
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);


%For G7
clear
load d:\li\berkeley1\canada\m5094m.dat
load d:\li\berkeley1\canada\m5094f.dat
load d:\li\berkeley1\canada\p5094m.dat
load d:\li\berkeley1\canada\p5094f.dat
xxx=size(m5094m);nht=xxx(1);nag=xxx(2);%Get sizes
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:nht %Get sex-combined death rates
   for j=1:nag
      mx(i,j)=(m5094m(i,j)*p5094m(i,j)+m5094f(i,j)*p5094f(i,j))/pxt(i,j);
   end
end
xxx=size(mx);nht=xxx(1);
yrs=1949+(1:nht);%1950-94
nffy=1995;ntrj=1000;agm=19;
nfor=12;
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);



clear
load d:\li\berkeley1\france\m5094m.dat
load d:\li\berkeley1\france\m5094f.dat
load d:\li\berkeley1\france\p5094m.dat
load d:\li\berkeley1\france\p5094f.dat
xxx=size(m5094m);nht=xxx(1);nag=xxx(2);%Get sizes
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:nht %Get sex-combined death rates
   for j=1:nag
      mx(i,j)=(m5094m(i,j)*p5094m(i,j)+m5094f(i,j)*p5094f(i,j))/pxt(i,j);
   end
end
xxx=size(mx);nht=xxx(1);
yrs=1949+(1:nht);%1950-94
nffy=1995;ntrj=1000;agm=19;
nfor=12;
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);

clear
load d:\li\berkeley1\germany\m5094m.dat
load d:\li\berkeley1\germany\m5094f.dat
load d:\li\berkeley1\germany\p5094m.dat
load d:\li\berkeley1\germany\p5094f.dat
xxx=size(m5094m);nht=xxx(1);nag=xxx(2);%Get sizes
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:nht %Get sex-combined death rates
   for j=1:nag
      mx(i,j)=(m5094m(i,j)*p5094m(i,j)+m5094f(i,j)*p5094f(i,j))/pxt(i,j);
   end
end
xxx=size(mx);nht=xxx(1);
yrs=1951+(1:nht);%1952-90
nffy=1995;ntrj=1000;agm=19;
nfor=12;
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);

clear
load d:\li\berkeley1\italy\m5094m.dat
load d:\li\berkeley1\italy\m5094f.dat
load d:\li\berkeley1\italy\p5094m.dat
load d:\li\berkeley1\italy\p5094f.dat
xxx=size(m5094m);nht=xxx(1);nag=xxx(2);%Get sizes
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:nht %Get sex-combined death rates
   for j=1:nag
      mx(i,j)=(m5094m(i,j)*p5094m(i,j)+m5094f(i,j)*p5094f(i,j))/pxt(i,j);
   end
end
xxx=size(mx);nht=xxx(1);
yrs=1950+(1:nht);%1951-93
nffy=1995;ntrj=1000;agm=19;
nfor=12;
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);


clear
load d:\li\berkeley1\japan\m5094m.dat
load d:\li\berkeley1\japan\m5094f.dat
load d:\li\berkeley1\japan\p5094m.dat
load d:\li\berkeley1\japan\p5094f.dat
xxx=size(m5094m);nht=xxx(1);nag=xxx(2);%Get sizes
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:nht %Get sex-combined death rates
   for j=1:nag
      mx(i,j)=(m5094m(i,j)*p5094m(i,j)+m5094f(i,j)*p5094f(i,j))/pxt(i,j);
   end
end
xxx=size(mx);nht=xxx(1);
yrs=1949+(1:nht);%1950-94
nffy=1995;ntrj=1000;agm=19;
nfor=12;
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);

clear
load d:\li\berkeley1\uk\m5094m.dat
load d:\li\berkeley1\uk\m5094f.dat
load d:\li\berkeley1\uk\p5094m.dat
load d:\li\berkeley1\uk\p5094f.dat
xxx=size(m5094m);nht=xxx(1);nag=xxx(2);%Get sizes
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:nht %Get sex-combined death rates
   for j=1:nag
      mx(i,j)=(m5094m(i,j)*p5094m(i,j)+m5094f(i,j)*p5094f(i,j))/pxt(i,j);
   end
end
xxx=size(mx);nht=xxx(1);
yrs=1949+(1:nht);%1950-94
nffy=1995;ntrj=1000;agm=19;
nfor=12;
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);


clear
load d:\li\berkeley1\us\m5094m.dat
load d:\li\berkeley1\us\m5094f.dat
load d:\li\berkeley1\us\p5094m.dat
load d:\li\berkeley1\us\p5094f.dat
xxx=size(m5094m);nht=xxx(1);nag=xxx(2);%Get sizes
pxt=p5094m+p5094f;%Get sex-combined pop.
nag=18;%Before Coale-G
for i=1:nht %Get sex-combined death rates
   for j=1:nag
      mx(i,j)=(m5094m(i,j)*p5094m(i,j)+m5094f(i,j)*p5094f(i,j))/pxt(i,j);
   end
end
xxx=size(mx);nht=xxx(1);
yrs=1949+(1:nht);%1950-94
nffy=1995;ntrj=1000;agm=19;
nfor=12;
[mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj);

