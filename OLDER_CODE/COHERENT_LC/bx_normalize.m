function [bx]=bx_normalize(V)

  bxNormalizer = sign(sum(V)) * (sum(abs(V)));
  bx = V / bxNormalizer;