clear; clc
global cm;
cm=0;
n=10000000; %размер массива
nd=2; %разница между элементами
low=1; %нижняя граница массива
high=n; %соответственно верхняя граница
key=(n/2)+1; 
s=ones(1, n);
for i=1:n %цикл для заполнения массива нечетными числами
    s(i)=i*nd-1;
end
tic
Nq=binary_search(s, key, low, high); %вызов функции binary_search для нахождения ключа
toc
if Nq==-1
    disp("Данного элемента в массиве нет")
else
    disp("Данный элемент находится в массиве под индексом:")
    disp(Nq)
    disp("Кол-во вызовов функции:")
    disp(cm)
end

%функция binary_search
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

