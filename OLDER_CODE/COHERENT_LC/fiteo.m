function [kt1]=fiteo(ax,bx,kt,mx1)
% modifies kt to fit Eo 

if 1
  [kt1, fval, exitflag, output] = fminsearch(@(k) e0_diff(mx1(1,:), ax, bx, k), kt);
  if exitflag <= 0
    warning('exitflag <= 0: output: %s', output)
  end
else
  bx=bx';	
  [eoo]=lfexpt(mx1);
  [eo1]=lfexpt(exp(ax+bx*kt));%Use Tim formula
  if abs(kt)>0.1
    kto=abs(kt);
  else
    kto=0.1;
  end
  n=1;kt1=kt;
  while abs(eo1-eoo)>0.1
    if (eo1-eoo)<-0.1
      kt1=kt1-kto*(0.99)^n;
      eo1=lfexpt(exp(ax+bx*kt1));
      n=n+1;
    else
      kt1=kt1+kto*(0.99)^n;
      eo1=lfexpt(exp(ax+bx*kt1));
      n=n+1;
    end   
  end
end