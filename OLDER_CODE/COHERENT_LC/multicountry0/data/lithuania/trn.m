
%make m5296 and p5296 (mid-yr pop)

clear
load c:\Limpi\multicountry0\data\lithuania\mx6001.txt
load c:\Limpi\multicountry0\data\lithuania\px6002.txt

for iyr=1:37%1960--1996
    for iage=1:18%0,1-4,...,80-84
        kk=(iyr+1)*24+iage;%start from 1952, not 1950
        m6096(iyr,iage)=mx6001(kk,5);
        p6096(iyr,iage)=0.5*(px6002(kk,5)+px6002(kk+24,5));
    end
end
save c:\Limpi\multicountry0\data\lithuania\m6096.txt m6096 -ascii;
save c:\Limpi\multicountry0\data\lithuania\p6096.txt p6096 -ascii;







 

