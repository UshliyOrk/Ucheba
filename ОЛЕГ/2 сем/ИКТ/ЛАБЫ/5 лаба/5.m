clear all; clc
global cm;
cm=0;
n=10; nd=2;
low=1; high=n; key=n/2; 
s=ones(1, n);
for i=1:n
    s(i)=i*nd-1;
end
tic
Nq=binary_search(s, key, low, high);
toc
if Nq==-1
    disp("Данного элемента в массиве нет")
else
    disp("Данный элемент находится в массиве под индексом:")
    disp(Nq)
    disp("Кол-во вызовов функции:")
    disp(cm)
end


function [M]=binary_search(s, key, low, high)
global cm;
cm=cm+1; %счетчик вызова функции binary_search
M = fix((low+high)/2);
if (low > high)
    M=-1;
    return;
end
if(s(M) == key)
    return;
end
if (s(M)>key)
    M=binary_search(s, key, low, M-1);
else
    M=binary_search(s, key, M+1, high);
end
end

