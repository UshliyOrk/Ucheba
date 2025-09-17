clear; clc;
A=[3 6 5 3];
X=A(1);
a=0;
n=0;
for i=1:4
    if A(i)>a
        a=A(i);
        n=i;
    end
end
disp('naibolschii element = ')
disp(a)
disp('nomer naibolschego elementa = ')
disp(n)
