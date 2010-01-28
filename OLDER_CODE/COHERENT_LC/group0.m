% I think this is an example of coherent done on the norwegian countries.

%For 1950--00 

nc0=3;%number of initial countries
nht=51;%historical years
 
%nc=5;%number of countries
mxc=zeros(nc0,nht,24);%country-specific mx, until age 105--110
pxc=zeros(nc0,nht,18);%country-specific px

%denmark
load c:\limpi\multicountry1\data\denmark\mx5000.txt;
load c:\limpi\multicountry1\data\denmark\px5000.txt
mxc(1,1:nht,1:18)=mx5000;;pxc(1,1:nht,1:18)=px5000;

%norway
load c:\limpi\multicountry1\data\norway\mx5000.txt;
load c:\limpi\multicountry1\data\norway\px5000.txt
mxc(2,1:nht,1:18)=mx5000;;pxc(2,1:nht,1:18)=px5000;

%sweden
load c:\limpi\multicountry1\data\sweden\mx5000.txt;
load c:\limpi\multicountry1\data\sweden\px5000.txt
mxc(3,1:nht,1:18)=mx5000;;pxc(3,1:nht,1:18)=px5000;

%Caole-Guo all of the data read in above
for ic=1:nc0
  for i=1:nht
	for j=1:18;
	  drt(j)=mxc(ic,i,j);
	end     
	mxcg=CoaleGt(drt);
	mxc(ic,i,19:24)=mxcg(19:24);
  end
end

%Making mx for total group by combining death rates based on population. "mx" is combined.
for i=1:nht
  for j=1:18
	p=0;d=0;
	for ic=1:nc0
	  p=p+pxc(ic,i,j);
	  d=d+pxc(ic,i,j)*mxc(ic,i,j);
	end
	drt(j)=d/p;%mx for nc0
  end
  mxcg=CoaleGt(drt);%Caole-Guo
  mx(i,1:24)=mxcg;
end

% Adjust combined death rates of combined mx
lnmx = log(mx);
Ax = mean(lnmx);
for ix = 1:nht,
  lnmx1(ix,:) = lnmx(ix,:)-Ax;
end

% SVD on combined 
[U S V] = svd(lnmx1,0);
Bx = V(:,1)/sum(V(:,1));
K = S(1,1)*U(:,1)*sum(V(:,1));
epcr(1)=S(1,1)^2/trace(S'*S); 
for i=1:nht 							% Create "Kt" by fitting combined K to e0
  kt=K(i);mx1=mx(i,:);
  [Kt(i)]=fiteo(Ax,Bx,kt,mx1);    
end

%SVD for single country
for ic=1:nc0							% "nc0" is number of countries

  % Convert everything to log death rates 
  % CHECK
  for i=1:nht							% "nht" is number of years of data
	for j=1:24							% number of age-classes is 24
	  lnmxc(i,j) = log(mxc(ic,i,j));	% "mxc" holds data for each country
	end
  end
  
  % store ax from above in data matrix (countries by  ages) for given country 
  % DONE
  for j=1:24
	xx=0;
	for i=1:nht 
	  xx=xx+log(mxc(ic,i,j));
	end
	ax(ic,j)=xx/nht;
  end
  
  % create two more matrices, first one a centering adjustment from ax only, second one a centering
  % adjustment from individual ax with common Bx and Kt.  I do this with all matrix multiplication, so no
  % loops
  % DONE
  for i=1:nht
	for j=1:24
	  lnmxc1(i,j)=log(mxc(ic,i,j))-ax(ic,j);
	  lnmxc2(i,j)=log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i); % 
	end
  end

  %%%%% Non-coherent part

  % LC on separate (non-coherent) 
  % First, calculate bx and e0 fitted kt ...
  % DONE
  [U S V] = svd(lnmxc1,0);
  k(ic,:)= (S(1,1)*U(:,1)*sum(V(:,1)))';
  bxo=(V(:,1)/sum(V(:,1)));
  for i=1:nht
	kt=k(ic,i);
	mx1(1:24)=mxc(ic,i,1:24);
	kto(i)=fiteo(ax(ic,:),bxo,kt,mx1);    
  end

  % ... second, calculate a  measure of fit.  (For each year and age, calculate difference against two
  % models -- ax only, ax w/ bx and kt. Remember that ax is the average log ASDR.)
  % Bx,Kt are combined; bxo,kto are individual standard; bxc,kc are individual residual
  % DONE
  xx1=0;xx2=0;							% collector variables
  for i=1:nht							% historical years
	for j=1:24							% ages
	  lnmxc(i,j) = log(mxc(ic,i,j));	% XXX REDUNDANT empirical log mx for this country
	  xx1=xx1+(log(mxc(ic,i,j))-ax(ic,j))^2;% how far off from average
	  xx2=xx2+(log(mxc(ic,i,j))-ax(ic,j)-bxo(j)*kto(i))^2; % how far off from average with modeled yearly change
	end
  end                    % I use 3 lists, each of single numbers: self.epr1, self.epr2, self.epr3
  epr(ic,1)=1-xx2/xx1;   % Save ratio of these two measures for each country.  "epr" means something from paper
  
  %%%%%  Coherent part

  % DONE
  % LC on residual mx (see above lnmxc2, which lnmx centered by ax and
  % also with Ax Bx subtracted from it).  Note that we are NOT fitting
  % kt based on e0.  step 1...

  [U S V] = svd(lnmxc2,0);
  kc(ic,:)= (S(1,1)*U(:,1)*sum(V(:,1)))';
  bxc=(V(:,1)/sum(V(:,1)));

  % step 2 ... calculate measures of fit over time and age
  xx1=0;xx2=0;xx3=0;					% collectors
  for i=1:nht
	for j=1:24
	  lnmxc(i,j) = log(mxc(ic,i,j));	% XXX Redundant 
      % Bx,Kt are combined; bxo,kto are individual standard; bxc,kc are individual residual
	  xx1=xx1+(log(mxc(ic,i,j))-ax(ic,j))^2; 
	  xx2=xx2+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i))^2;   
	  xx3=xx3+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i)-bxc(j)*kc(ic,i))^2;
	end
  end
  epr(ic,2)=1-xx2/xx1;
  epr(ic,3)=1-xx3/xx1;
  bxC(ic,:)=bxc';
  
  %%%% Calculate AR(1) coef for kt of residual ("kc") 
  
  % set up lag matrix
  for i=1:nht-1
	X(i,2)=kc(ic,i);
	X(i,1)=1;
	y(i)=kc(ic,i+1);    
  end
  
  %OLS on lag matrix get coefficients (a0 and a1)
  b(1)=sum(y); 
  b(2)=y*X(:,2);
  a(1,1)=nht-1; 
  a(1,2)=sum(X(:,2)); a(2,1)=a(1,2); a(2,2)=X(:,2)'*X(:,2);
  xxx=(a^-1)*b';
  a0=xxx(1); 
  a1=xxx(2); 
  a00=mean(y);
  ar(ic)=a1;							% Save for later

  % Use AR(1) coefficients to get innovations sans errors in a new TS
  % with the starting point of kc and see how it compares to Ktc
  Ktc(ic,1)=kc(ic,1);
  for i=2:nht
	Ktc(ic,i)=a0+a1*kc(ic,i-1);
  end

  % Calculate errors from the innovations and the real thing
  for i=1:nht
	e(i)=kc(ic,i)-Ktc(ic,i);    % empirical residual kt minus simulated residual kt 
	e0(i)=kc(ic,i)-mean(kc(ic,:));  % empirical residual kt minus its mean
  end
  sdckt=sqrt(cov(e));  % Redundant
  Rsq(ic)=1-cov(e)/cov(e0);%R^2
  
end

save c:\limpi\multicountry1\data\BxKt Bx Kt

%R^2    S          C       CS        R^2 AR(1)
%D    0.8463    0.7882    0.8721      0.8832
%N    0.8867    0.8872    0.9190      0.7820
%S    0.9345    0.9095    0.9464      0.9133

%R^2(C) for Denmark is not OK, R^2AR(1) is OK

clf;plot(kc(ic,:));hold;plot(Ktc(ic,:),'r')