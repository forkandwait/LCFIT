% -*-matlab-*- 

%This code (1) loads a collective Bx and Kt, (2) runs both coherent and separate LC on several
% countries saving the results into several 3-d matrices (Austria is the model but much
% repetition), (3) saves the 3-d matrices for later use.   Uses "ic" to increment on each country
% so that can stuff the data in the right dimension.

% Outputs to a file:
%    Eohf -- XXX Never used!!
%    Eoh  -- multicountry (convergent) empirical e0
%    Eof  -- multicountry (convergent) projected  e0, at 5%, 50%, 95%
%    Eofs -- independent (non-convergent) projected e0, at 5%, 50%, 95%

% Look for uses (massively redundant all of this) of multisfactAR
% (gets regression data - so do other functions), and multicountry2GC
% (infer TS params for kt and resid and simulate), multicountry2G,
% multicountry2S

clear
load BXKT; 								% get common factor.  Sets variables "Bx" and "Kt"
nfor=55;								% Number of 1-yr intervals of forecasting
ntrj=500;								% Number of trajectories
randn('state',0); 
rndgk=randn(ntrj,nfor); 				% Random var for modelling group Kt, 1-yr
nfor5=11;								% 5-yr
nffy=1997;								% XXX NEVER USED
nffy5=2000;
nspt=4;									% 1996+4=2000

%Austria(C)
% loads mx and px for austria (1).  Does a convergent forecast Bx_all, Kt_all, mx_austria (2) saves
% it in a 3-d array "Eof". then does a separate forecast for austria as well as saves that in a 3-d
% array "Eofs" (3).  I think the lines sans semicolons and assignments are for information to the screen.  
clear mx;
ic=1
load multicountry0/data/austria/m5296.txt; %(1)
mx=m5296;

% NOTE
[eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt); % Convergent forecast
Eoh(ic,:)=eoh;							% empirical e0
Eof(ic,1:3,1:11)=eof;					% simulated e0 forward -- 5%, 50%, 95%
eoh(45)									% INFO
eof(2,11)								% INFO
eof(1,11)-eof(3,11)						% INFO
nhly=1996;
% NOTE								
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj); % returns eofs for 5%, 50%, 95% projections for
                                                 % NON-convegent LC (don't input Bx and Kt from
                                                 % collective mx).
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)								% INFO
eofs(1,11)-eofs(3,11)					% INFO

%Canada(C)
ic=2
clear mx;
load multicountry0/data/canada/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Czech(CS)
ic=3
clear mx;
load multicountry0/data/czech/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)


%Denmark(CS)
ic=4
clear mx;
load multicountry0/data/denmark/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%England(CS)
ic=5
clear mx;
load multicountry0/data/england/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Finland(C)
ic=6
clear mx;
load multicountry0/data/finland/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%France(CS)
ic=7
clear mx;
load multicountry0/data/france/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%GermanyE(CS)
ic=8
clear mx;
load multicountry0/data/germanye/m5696.txt;
mx=m5696;
Kto=Kt(5:45);
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kto,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,1:4)=0;Eoh(ic,5:45)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(41)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%GermanyW(C)
ic=9
clear mx;
load multicountry0/data/germanyw/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Italy(CS)
ic=10
clear mx;
load multicountry0/data/italy/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Japan(CS)
ic=11
clear mx;
load multicountry0/data/japan/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)


%Lithuania(CS)
ic=12
clear mx;
load multicountry0/data/lithuania/m6096.txt;
mx=m6096;
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,9:45)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(37)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Netherlands(CS)
ic=13
clear mx;
load multicountry0/data/netherland/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Norway(CS)
ic=14
clear mx;
load multicountry0/data/norway/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Spain(CS)
ic=15
clear mx;
load multicountry0/data/spain/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)


%Sweden(CS)
ic=16
clear mx;
load multicountry0/data/sweden/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Switzerland(CS)
ic=17
clear mx;
load multicountry0/data/sweitzerland/m5296.txt;
mx=m5296;
[eoh,eof,drft,sdgkt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);%2MIN
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

%Usa(CS)
ic=18
load multicountry0/data/usa/m5296.txt;
mx=m5296;
%This code take 2 min
[eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt);
Eoh(ic,:)=eoh;Eof(ic,1:3,1:11)=eof;
eoh(45)
eof(2,11)
eof(1,11)-eof(3,11)
nhly=1996;
[eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj);%Separate forecast
Eofs(ic,1:3,1:11)=eofs;
eofs(2,11)
eofs(1,11)-eofs(3,11)

save Eohf  Eoh Eof Eofs 						% save results.  XXX Eohf is empty!


%% Think following is not important, just atest for something from Li Nan
load multicountry0/data/bulgaria/m5296.txt;
mx=m5296;
[Rsq,a0,a1,sda0,sda1,z]=multisfactAR(Bx,Kt,mx)
load multicountry0/data/hungary/m5296.txt;
mx=m5296;
[Rsq,a0,a1,sda0,sda1,z]=multisfactAR(Bx,Kt,mx)
load multicountry0/data/russia/m7096.txt;
mx=m7096;
[Rsq,a0,a1,sda0,sda1,z]=multisfactAR(Bx,Kt,mx)

