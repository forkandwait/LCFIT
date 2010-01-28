%%%%%   Title: fiteo.m
%
%  This m script modifies kt to fit Eo 
%  
%%%%%

function [kt1]=fiteo(ax,bx,kt,mx1)
bx=bx';
 [eoo]=lfexpt(mx1);
 [eo1]=lfexpt(exp(ax+bx*kt));%Use Tim formula
 if abs(kt)>0.1
    kto=abs(kt);
 else
    kto=0.1;
 end
 n=1;kt1=kt;
 while abs(eo1-eoo)>0.001
    if (eo1-eoo)<-0.001
       kt1=kt1-kto*(0.99)^n;
       eo1=lfexpt(exp(ax+bx*kt1));
       n=n+1;
    else
       kt1=kt1+kto*(0.99)^n;
       eo1=lfexpt(exp(ax+bx*kt1));
       n=n+1;
    end
 end
 
       
 