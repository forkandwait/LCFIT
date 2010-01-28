function [kt95,kt50,kt5,e95,e50,e5]=pict(mxf,stok)
%Using Lee-Carter to do G7 forecast, 
% This matrix contains ntraj*nft points means ntraj*nft*5 years,
xxs=size(mxf);ntrj=xxs(1);nfor=xxs(2);
% (2.2)Get simulated E0  
   for tt=1:nfor
      for tind=1:ntrj
          for i=1:xxs(3)
          drt(i)=mxf(tind,tt,i);
      end
      [eo]=lfexpt(drt);e0(tind,tt)=eo;%Tim formula         
   end
   end%End of (2.2)
   kt95=prctile(stok,95);
   kt50=prctile(stok,50);
   kt5=prctile(stok,5); 
   e95=prctile(e0,95);
   e50=prctile(e0,50);
   e5=prctile(e0,5); 
