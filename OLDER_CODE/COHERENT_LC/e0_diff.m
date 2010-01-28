function ret = e0_diff(mx, ax, bx, kt_scalar)
% INPUT mx, ax, bx, kt
%
% Returns the difference of lfexpt(mx) and lfexp
if size (bx) ~= size(ax)
  bx = bx';
end
e0_calc = lfexpt(exp(ax + bx * kt_scalar));
e0_emp = lfexpt(mx);
ret = abs(e0_emp - e0_calc);