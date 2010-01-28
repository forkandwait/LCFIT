% -*-matlab-*-
% Coherent for M & F Sweden, years 1950 - 2002

% Set up a few data structures
clear;
nc0=2;                                  % number of gender of sweden
nht=53;                                 % historical years
mxc=zeros(nc0,nht,24);                  % country-specific mx, until age 105--110
pxc=zeros(nc0,nht,18);                  % country-specific px

% Sweden data
load ./sweden/mxm5002.txt;
load ./sweden/mxf5002.txt;
load ./sweden/pxm5002.txt;
load ./sweden/pxf5002.txt;
mxc(1,1:nht,1:18)=mxm5002;pxc(1,1:nht,1:18)=pxm5002;
mxc(2,1:nht,1:18)=mxf5002;pxc(2,1:nht,1:18)=pxf5002;

% Following hold intermediate results for explantion ratios but they
% are just informational.  Look in "epr[1..3]" for the actual explanation ratios
epr_terms_1 = [nan nan]
epr_terms_2 = [nan nan nan]

% Coale-Guo the single populations
for ic=1:nc0							% Each population
  for i=1:nht							% Each historical time
    for j=1:18;						    % Each age
      drt(j)=mxc(ic,i,j);
    end     
    foo = CoaleGt(drt);
    mxc(ic,i,19:24) = foo(19:24);        % mxcg=CoaleGt(drt); mxcg(19:24);
  end
end

% Making mx for total group.  Add up mx and pop, then average mx weigted by pop
for i=1:nht         
  for j=1:18
    p=0;                                % running total of pop
    d=0;                                % running total of mx, weighted by pop for that item
    for ic=1:nc0    
      p = p+pxc(ic,i,j);
      d = d+pxc(ic,i,j)*mxc(ic,i,j);
    end
    drt(j) = d/p;     
  end
  mxcg = CoaleGt(drt);
  mx(i,1:24) = mxcg;
end

% LC for total group
lnmx = log(mx);
Ax = mean(lnmx);
for ix = 1:nht,
  lnmx1(ix,:) = lnmx(ix,:) - Ax;
end

[U S V] = svd(lnmx1,0);
Bx = bx_normalize(V(:,1));
K = S(1,1) * U(:,1) * sum(V(:,1));
epcr(1) = S(1,1)^2/trace(S'*S);

% Fit eo
for i=1:nht
  kt = K(i); 
  mx1 = mx(i,:);
  [Kt(i)] = fiteo(Ax,Bx,kt,mx1);    
end

% Do everything, for each sex (ic is index 1 for M, and 2 for F)
for ic=1:nc0
  % Make log mx
  for i=1:nht
    for j=1:24
      lnmxc(i,j) = log(mxc(ic,i,j));
    end
  end
  
  % Make ax for each group
  for j=1:24
    xx = 0;
    for i=1:nht 
      xx = xx + log(mxc(ic,i,j));
    end
    ax(ic,j) = xx/nht;
  end
  
  % Make the normed lnmx and residuals between predicted from group mx versus empirical from single
  % group mx
  for i=1:nht
    for j=1:24
      lnmxc1(i,j) = log(mxc(ic,i,j))-ax(ic,j);
      lnmxc2(i,j) = log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i);       
    end
    % The following would also work for the above for the whole matrix (yes, I tested it):
    % log(squeeze(mxc(2,:,:)))) - repmat(ax(2,:),53,1) - Kt'*Bx'
  end

  % SVD single country mx (minus its own ax, i.e. the normalized mx)
  [U S V] = svd(lnmxc1,0);
  k(ic,:) = (S(1,1) * U(:,1) * sum(V(:,1)))';
  bxo = bx_normalize(V(:,1)); 
  for i=1:nht
    kt = k(ic,i);
    mx1(1:24) = mxc(ic,i,1:24);
    [kto(i)] = fiteo(ax(ic,:),bxo,kt,mx1); % Note -- this is just the regular SVD
  end

  % Explanation ratio from residuals above
  xx1=0; xx2=0;
  for i=1:nht
    for j=1:24
      lnmxc(i,j) = log(mxc(ic,i,j));
      xx1 = xx1 + (log(mxc(ic,i,j)) - ax(ic,j))^2;
      xx2 = xx2 + (log(mxc(ic,i,j)) - ax(ic,j) - bxo(j)*kto(i)) ^ 2;
    end
  end
  epr(ic,1) = 1 - xx2/xx1; 
  epr_terms_1(ic,:) = [xx1 xx2]

  % SVD of residuals of each subpop from its particular LC
  [U S V] = svd(lnmxc2,0);
  kc(ic,:) = (S(1,1) * U(:,1) * sum(V(:,1)))';
  bxc = bx_normalize(V(:,1));
  xx1=0; xx2=0; xx3=0;
  for i=1:nht
    for j=1:24
      lnmxc(i,j) = log(mxc(ic,i,j));
      xx1 = xx1+(log(mxc(ic,i,j))-ax(ic,j))^2;
      xx2 = xx2+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i))^2;
      xx3 = xx3+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i)-bxc(j)*kc(ic,i))^2;
    end
  end
  epr(ic,2) = 1-xx2/xx1; % Explanation ratio of common factor, goog enough, don't need specific factor 
  epr(ic,3) = 1-xx3/xx1; % Explanation ratio with common and specific factors
  bxC(ic,:) = bxc';
  epr_terms_2(ic,:) = [xx1 xx2 xx3]

  %AR(1) coef.
  for i=1:nht-1
    X(i,2)=kc(ic,i);
    X(i,1)=1;
    y(i)=kc(ic,i+1);    
  end
  %OLS  
  b(1)=sum(y);b(2)=y*X(:,2);
  a(1,1)=nht-1;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
  xxx=(a^-1)*b';
  a0=xxx(1);a1=xxx(2);a00=mean(y);
  ar(ic)=a1;
  Ktc(ic,1)=kc(ic,1);
  for i=2:nht
    Ktc(ic,i)=a0+a1*kc(ic,i-1);
  end
  for i=1:nht
    %e(i)=y(i)-a0-a1*X(i,2);
    e(i)=kc(ic,i)-Ktc(ic,i);   
  end

  e0=diff(kc(ic,:));
  sdckt=sqrt(cov(e));
  RsqRW(ic)=1 - e0*e0'/cov(kc(ic,:));%R^2 for RW
  Rsq(ic)=1 - cov(e)/cov(kc(ic,:));%R^2 of AR(1), not good enough      
  ic   
end
save ./sweden/BxKt Bx Kt

%1950-2002
%R^2    S          C       CS     C good enough
%M    0.8572    0.8834    0.9323
%F    0.9317    0.8946    0.9271

%R^2 RW(worse than i.i.d.)  AR(1) < R^2(C)for M 
%M  -5.4624                 0.8804        
%F  -6.8051                 0.8763

%1900-2002
%R^2    S          C       CS     C good enough, but Kt not linear
%M    0.9488    0.9290    0.9775
%F    0.9434    0.9409    0.9796

%R^2 AR(1)   No better 
%M   0.9386        
%F   0.9462

clf;plot(kc(ic,:));hold;plot(Ktc(ic,:),'r')%does not look like RW
