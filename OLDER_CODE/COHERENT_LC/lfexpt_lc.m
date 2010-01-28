function e0_calc = lfexpt_lc(ax, bx, kt_scalar)
% INPUT mx, ax, bx, kt
%
% Returns the difference of lfexpt(mx) and lfexpt_lc
if size (bx) ~= size(ax)
  bx = bx';
end
e0_calc = lfexpt(exp(ax + bx * kt_scalar))
