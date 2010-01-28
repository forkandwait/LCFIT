
%make m5296 and p5296 (mid-yr pop)
clear
load C:\Users\Linan\LiHome\multipop\data\canada\m5096.txt
load C:\Users\Linan\LiHome\multipop\data\canada\p5097.txt

for iyr=1:45%1952--1996
    for iage=1:18%0,1-4,...,80-84
        kk=(iyr+1)*24+iage;%start from 1952, not 1950
        m5296(iyr,iage)=m5096(kk,5);
    end
end
for iyr=1:45%1952--1996
    for iage=1:18%0,1-4,...,80-84
        kk=(iyr+1)*22+iage;%start from 1952, not 1950
        p5296(iyr,iage)=0.5*(p5097(kk,5)+p5097(kk+22,5));
    end
end

save C:\Users\Linan\LiHome\multipop\data\canada\m5296.txt m5296 -ascii;
save C:\Users\Linan\LiHome\multipop\data\canada\p5296.txt p5296 -ascii;



 

