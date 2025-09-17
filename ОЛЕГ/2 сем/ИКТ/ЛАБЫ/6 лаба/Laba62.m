clear
clc
n = 4000;
a = rand(n);
tic
da1 = det_Gauss(a,n);
line1 = toc;
disp('Значение определителя методом Гаусса:')
disp(da1)
disp('Время выполнения методом Гаусса:')
disp(line1)
tic
da2 = det(a);
line2 = toc;
disp('Значение определителя библиотечной функции Matlab:')
disp(da2)
disp('Время выполнения библиотечной функции Matlab:')
disp(line2)
function det = det_Gauss(a,n)
for k = 1:n - 1
    for i = k + 1:n
        for j = k:n
            if j == k
                aik = a(i, k);
            end
            a(i, j) = a(i, j) - aik * a(k, j) / a(k, k);
        end
    end
end
disp(a)
det = 1;
for i = 1:n
    det = det * a(i, i);
end
end