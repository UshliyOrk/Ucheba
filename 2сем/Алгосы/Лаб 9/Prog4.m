%ввод исходных данных
f = @(x) 0.1*x.^3 + 20*cos(x) + 10;
fy = 0.1*x.^3 + 20*cos(x) + 10;
h = 0.1;
df = @(x) (f(x+h) - f(x-h))/(2*h);
tol = 1e-6;
iterlimit = 1000;
x = -10:h:10;
hold on;
p1 = plot(x, fy);
grid on;
x0 = 2.5;

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
rts = [];

%проходим по промежутку, где находятся корни
for i = -10:10
  %записываем разность модулей значения функции в точках отстоящих от x = i на h
  d = abs(f(i-h))-abs(f(h+i));
  %фиксируем пересечение
  if abs(d)<=f(h)
    x0 = i;
    %вычисление корней
    tic;
    [root, iter] = newton(f, df, x0, tol, iterlimit);
    root = round(root/tol)*tol; % округление
    %преверяем, есть ли корни
    t = toc*1000;
    if ~isempty(root)&&~any(rts == root) % проверяем был ли такой корень найден до того
      rts = [rts, root];
      %вывод результатов
      disp(["корень при x0 = ", num2str(x0)]);
      disp(["и при tol = ", num2str(tol)]);
      disp(["x = ", num2str(root)]);
      disp(["f(x) = ", num2str(f(root))]);
      disp(["количество итераций = ", num2str(iter)]);
      disp(["время выполнения = ", num2str(t), " ms"]);
    endif
  endif
endfor
rts

set(p1, "Color", "red", "LineWidth", 2);
hold off;
