clc;clear;
n=10000;
mt=1; %вспомогательная переменная
mc=1; %кол-во значений в последовательности моды
im=1; %индекс начала значений моды
i=1;
S=fix(50*rand([1 n]));
S=quicksort(S);
tic
while i < n-1
    j=i;
    while j < n && S(j) == S(j+1) %если мода в массиве есть, то считаем кол-во элементов моды
        mt=mt+1;
        j=j+1;
    end
    i=i+mt;
    if mt > mc %если найденная мода больше предыдущей
        mc=mt;
        im=i-mt;
    end
    mt=1;
end
if mc > 1 %если мода в массиве наблюдается, то выводим ее
   disp("в массиве наблюдается мода элемента:")
   disp(S(im))
   disp("мода начинается с индекса:")
   disp(im)
   disp("Продолжительность моды:")
   disp(mc)
else
    disp("В массиве мода не наблюдается")
end
toc

function vector = quicksort(vector) %объявляем функцию
if numel(vector) >= 1 %если кол-во элементов в векторе не меньше 1
   global cm;
   cm = cm + 1; %считаем кол-во вызовов функции quicksort
   pivot = vector(1); %выберем 1-ый элемент вектора для сравения
         A1 = quicksort(vector(vector < pivot)); %сравниваем первый элемент с остальными
         A2 = vector(vector == pivot);
         A3 = quicksort(vector(vector > pivot));
    vector = [A1 A2 A3]; 
end
end