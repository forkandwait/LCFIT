
%make m5296 and p5296 (mid-yr pop)
clear
load c:\Limpi\multicountry0\data\spain\mx5001.txt
load c:\Limpi\multicountry0\data\spain\px5002.txt

for iyr=1:45%1952--1996
    for iage=1:18%0,1-4,...,80-84
        kk=(iyr+1)*24+iage;%start from 1952, not 1950
        m5296(iyr,iage)=mx5001(kk,5);
        p5296(iyr,iage)=0.5*(px5002(kk,5)+px5002(kk+24,5));
    end
end
save c:\Limpi\multicountry0\data\spain\m5296.txt m5296 -ascii;
save c:\Limpi\multicountry0\data\spain\p5296.txt p5296 -ascii;





 

