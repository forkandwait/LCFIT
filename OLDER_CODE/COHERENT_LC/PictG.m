function [e95,e50,e5]=PictG(mxf)  % -*-matlab-*-
% PictG
%  Calculates percentile life expect for year from a matrix of simulated ASDR's.  So for each
%  year in simulation, get three e_0's (5%, 50%, 95%), but then return these as vectors of e_0
%  per year for 5%, etc.
%
% input:
%    mxf -- array of simulated mx'es, trajectories in the rows, years forward in the columns.
%
% output
%    3 vectors, with entries per year:  e95, e50, e5 -- 95%, 50%, and 5% e_0's.
	 
xxs=size(mxf);
ntrj=xxs(1);
nfor=xxs(2);

% (2.2) Use simulated mx (input to f() as "mxf") to get range E0 for each trajectory in each year 
for tt=1:nfor
  for tind=1:ntrj
	for i=1:xxs(3)
	  drt(i)=mxf(tind,tt,i);
	end
	[eo]=lfexpt(drt);
	e0(tind,tt)=eo;
  end
end 									% End of (2.2) 
e95=prctile(e0,97.5);					% prctile() is from mathworks, in the current director
e50=prctile(e0,50);
e5=prctile(e0,2.5); 