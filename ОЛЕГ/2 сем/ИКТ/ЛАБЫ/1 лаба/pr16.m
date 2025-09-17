%Определить какие из функций
%y1(x)= x*x-1 %y2(x)= sqrt(x) %y3(x)= cos(x)
% пересекаются на интервале [0.5;2]
clear;
close all;
clc;
x=0.5;
shethic=0; % счетчик корней
cross=0;
razn2=0;
 dx=2; % шаг менять нельзя!
while x <= 2
 razn1=cos(x)-sqrt(x); % корень уравнения cos(x)=sqrt(x)
 if razn2*razn1 <0
 shethic=shethic+1;
 end
 x=x+dx/100; % шаг цикла % что бы шаг стал меньше поделим его на 100
 razn2=razn1;
end
if shethic>0
 disp('cos(x) и sqrt(x) intersect ');
end
cross=cross+ shethic;
shethic=0;
razn2=0; % обнуляем переменные
x=0.5;
 while x <= 2
 razn1=cos(x)-x*x+1; % корень уравнения cos(x)=x*x+1
 if razn2*razn1 <0
 shethic=shethic+1;
 end
 x=x+dx/100;
 razn2=razn1;
 
 end
 
 if shethic>0
 disp('cos(x) и x*x-1 intersect ');
 end
cross=cross+ shethic;
shethic=0;
razn2=0;% обнуляем переменные
x=0.5;
while x <= 2
 razn1=sqrt(x)-x*x+1; % корень уравнения sqrt(x)=x*x+1
 if razn2*razn1 <0
 shethic=shethic+1;
 end
 x=x+dx/100;
 razn2=razn1;
 
 end
 
 if shethic>0
 disp('sqrt(x) и x*x-1 intersect ');
 end
cross=cross+ shethic;
disp('cross=');disp(cross);
 x = 0.5:0.0001:2; % шаг и интервал
y = cos(x);
y2 = pow2(x) -1;
y3 = sqrt(x);
plot(x,y,x,y2,x,y3)% функция построения графика
