clear; clc;
S=0;
i=1;
A = [1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22];
while S<20 && i<20;
    S = S+A(i);
    i = i+1;
end;
disp('S = ')
disp(S)
disp('i = ')
disp(i)
