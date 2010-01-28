
%make m5296 and p5296 (mid-yr pop)
clear
load d:\multicountry\data\germanye\mx5696.txt
load d:\multicountry\data\germanye\px5697.txt

for iyr=1:41%1956--1996
    for iage=1:18%0,1-4,...,80-84
        kk=(iyr-1)*24+iage;%start from 1952, not 1950
        m5696(iyr,iage)=mx5696(kk,5);
        p5696(iyr,iage)=0.5*(px5697(kk,5)+px5697(kk+24,5));
    end
end
save d:\multicountry\data\germanye\m5696.txt m5696 -ascii;
save d:\multicountry\data\germanye\p5696.txt p5696 -ascii;



 

