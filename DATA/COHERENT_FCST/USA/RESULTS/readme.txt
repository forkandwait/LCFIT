There are three files -- simulated mx_comb.txt, mx_fem.txt, mx_male.txt.

Each of these files is organized into 1000 simulation blocks separated by double
newlines; each block is a simulation run, with years as the row, age (0-1, 1-4, 5-9 etc)
as columns.  So in any block, x(3,3) would refer to year 2010 and age 5-9; x(4,3) would
be year 2011 and age 5-9, etc.  (Jump off year is 2008.)  I will let you do whatever
array manipulation you want to make 4 dimensional slicing and graphing possible...

I got these data by reading the "object dump" from the LCFIT run, and using a text
editor to find mx_comb, mx_indiv sections and pull them out (emacs is frigging
AMAZING!).  I will try to work on a script to make this easier, but it was easiest to do
it one off like this for now.

I will also follow with parameter estimates, but for now I popped the runs into "boe".
Login as "boe", password = foobar, and click "List all forecasts" and you will see them,
for better or worse (I am nowhere near as confident about the coherent code than I am
with the simple code...).
