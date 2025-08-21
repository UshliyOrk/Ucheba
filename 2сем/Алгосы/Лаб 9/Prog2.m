%ввод исходных данных
f = @(x) 0.1*x.^3 + 20*cos(x) + 10;
h = 0.1;
df = @(x) (f(x+h) - f(x-h))/(2*h);
iterlimit = 200;
ezplot(f);
grid on;
x0 = 10;

%поиск корня методом Ньютона
function [root, iter] = newton(f,df,x0,tol,iterlimit)
  iter = 1; % количество итераций
  old_root = x0; % старый корень - начальная точка
  root = x0 - f(x0)/df(x0); %найденный по формуле корень
  while iter <= iterlimit && abs(root - old_root)>tol
    old_root = root; % старый корень - корень с предыдущей итерации
    root = old_root - f(old_root)/df(old_root);
    iter = iter + 1;
    %если превышено число итераций
    if iter == iterlimit
      root = [];
      break
    endif
  endwhile
endfunction
for i = 0:6
  tol = 10^(-i);
  %вычисление корней
  tic;
  [root, iter] = newton(f, df, x0, tol, iterlimit);
  %преверяем, есть ли корни
  t = toc*1000;
  if ~isempty(root)
    %вывод результатов
    disp(["корень при x0 = ", num2str(x0)]);
    disp(["и при tol = ", num2str(tol)]);
    disp(["x = ", num2str(root)]);
    disp(["f(x) = ", num2str(f(root))]);
    disp(["количество итераций = ", num2str(iter)]);
    disp(["время выполнения = ", num2str(t), " ms"]);
  else
    disp("Превышено число итераций!");
  endif
endfor


