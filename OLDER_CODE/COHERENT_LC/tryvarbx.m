

%For 1952--96 (Germany)

%US
clear
load d:\linan1\mike\nmx.3396.asc;
mxo=nmx;
nhts=1933;nht=64;nht1=32;
[bx,cx] = tryvarbx1(nhts,nht1,nht,mxo);
gtext('Figure 1. Results of US using data in 1933-1996')
print rotationbx1 -dmeta


%Austria
clear
load d:\multicountry\data\austria\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%Canada
load d:\multicountry\data\canada\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%denmark
load d:\multicountry\data\denmark\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%england
load d:\multicountry\data\england\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%finland
load d:\multicountry\data\finland\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%france
clear
load d:\multicountry\data\france\m5296.txt;
mxo=m5296;
nhts=1952;nht=45;nht1=23;
[bx,cx] = tryvarbx1(nhts,nht1,nht,mxo);
gtext('Figure 3. Results of France using data in 1952-1996')
print rotationbx3 -dmeta

%germanyw
load d:\multicountry\data\germanyw\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%italy
load d:\multicountry\data\italy\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%Japan
clear
load d:\multicountry\data\japan\m5296.txt;
mxo=m5296;
nhts=1952;nht=45;nht1=23;
[bx,cx] = tryvarbx1(nhts,nht1,nht,mxo);
gtext('Figure 2. Results of Japan using data in 1952-1996')
print rotationbx2 -dmeta

%netherland
load d:\multicountry\data\netherland\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%norway
load d:\multicountry\data\norway\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);


%sweden
load d:\multicountry\data\sweden\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%sweitzerland
load d:\multicountry\data\sweitzerland\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);

%usa
clear
load d:\multicountry\data\usa\m5296.txt;
mxo=m5296;
nht=45;nht1=23;
[bx,cx] = tryvarbx1(nht1,nht,mxo);
