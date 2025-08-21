% Ввод исходных данных
f = @(x) 0.1*x.^3 + 20*cos(x) + 10;
h = 0.1;
df = @(x) (f(x+h) - f(x-h))/(2*h);
tol = 1e-6;
iterlimit = 200;
x0 = -1;

% Построение графика функции
figure;
ezplot(f, [-10, 10]);
grid on;
hold on;

% Функция для построения касательной в точке x0
function plot_tangent(f, df, x0)
    x_range = linspace(x0-2, x0+2, 100);
    tangent = f(x0) + df(x0)*(x_range - x0);
    plot(x_range, tangent, 'r--');
    plot(x0, f(x0), 'ro'); % Точка касания
end

% Модифицированный метод Ньютона с визуализацией
function [root, iter] = newton_with_plot(f, df, x0, tol, iterlimit)
    iter = 1;
    old_root = x0;
    root = x0 - f(x0)/df(x0);

    % Построение начальной касательной
    plot_tangent(f, df, x0);
    pause(1); % Пауза для визуализации

    while iter <= iterlimit && abs(root - old_root) > tol
        old_root = root;
        root = old_root - f(old_root)/df(old_root);

        % Построение касательной на текущей итерации
        plot_tangent(f, df, old_root);
        pause(1); % Пауза для визуализации

        iter = iter + 1;

        if iter == iterlimit
            root = [];
            break;
        endif
    endwhile
endfunction

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
    [root, iter] = newton(f, df, x0, tol, iterlimit);
    root = round(root/tol)*tol; % округление
    %преверяем, есть ли корни
    if ~isempty(root)&&~any(rts == root) % проверяем был ли такой корень найден до того
      rts = [rts, root];
      newton_with_plot(f,df,x0,tol,iterlimit);
      %вывод результатов
      disp(["корень при x0 = ", num2str(x0)]);
      disp(["и при tol = ", num2str(tol)]);
      disp(["x = ", num2str(root)]);
      disp(["f(x) = ", num2str(f(root))]);
      disp(["количество итераций = ", num2str(iter)]);
    endif
  endif
endfor
rts
hold off;
