
%make m5296 and p5296 (mid-yr pop)
clear
load C:\Users\Linan\LiHome\multipop\data\italy\m5099.txt
load C:\Users\Linan\LiHome\multipop\data\italy\p5000.txt

for iyr=1:45%1922--1996
    for iage=1:18%0,1-4,...,80-84
        kk=(iyr+1)*24+iage;%start from 1952, not 1950
        m5296(iyr,iage)=m5099(kk,5);
        p5296(iyr,iage)=0.5*(p5000(kk,5)+p5000(kk+24,5));
    end
end
save C:\Users\Linan\LiHome\multipop\data\italy\m5296.txt m5296 -ascii;
save C:\Users\Linan\LiHome\multipop\data\italy\p5296.txt p5296 -ascii;



 

