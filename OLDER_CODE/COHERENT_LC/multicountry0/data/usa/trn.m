
%make m5296 and p5296 (mid-yr pop)
clear
load C:\Users\Linan\LiHome\multipop\data\usa\m5999.txt
load C:\Users\Linan\LiHome\multipop\data\usa\p5900.txt

for iyr=1:38%1959--1996
    for iage=1:18%0,1-4,...,80-84
        kk=(iyr-1)*24+iage;%start from 1952, not 1950
        m5296(iyr+7,iage)=m5999(kk,5);
        p5296(iyr+7,iage)=0.5*(p5900(kk,5)+p5900(kk+24,5));
    end
end

load C:\Users\Linan\LiUvic\berkeley1\us\m5094m.dat
load C:\Users\Linan\LiUvic\berkeley1\us\m5094f.dat
load C:\Users\Linan\LiUvic\berkeley1\us\p5094m.dat
load C:\Users\Linan\LiUvic\berkeley1\us\p5094f.dat

for iyr=1:7
    for iage=1:18
        p5296(iyr,iage)=100*(p5094m(iyr,iage)+p5094f(iyr,iage));
        m5296(iyr,iage)=100*(m5094m(iyr,iage)*p5094m(iyr,iage)+m5094f(iyr,iage)*p5094f(iyr,iage))/p5296(iyr,iage);
    end
end

save C:\Users\Linan\LiHome\multipop\data\usa\m5296.txt m5296 -ascii;
save C:\Users\Linan\LiHome\multipop\data\usa\p5296.txt p5296 -ascii;



 

