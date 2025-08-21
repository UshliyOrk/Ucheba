%исходные данные%
N = 8;
s1 = [4 4 4 7 7 7 7 7];
s2 = [4 4 4 4 4 7 7 7];
s3 = [1 2 3 4 5 6 7 8];
%алгоритм поиска моды%
function retval = ModeSearch(S, N)
  mt = 1; %счетчик повторений
  mc = 1;% переменная для хранения количества максимальных повторов
  im = 1;% индекс начала моды
  i = 1;% вспомогательная переменная итератор
  %обход массива
  while i<N-1
    j=i;
    %поиск повторов
    while (j<N && S(j)==S(j+1))
      mt = mt+1;
      j = j+1;
    endwhile
    i = i+mt;
    %сохранение макс числа повторяющихся элементов
    if mt>mc
      mc = mt;
      im = i-mt;
    endif
    mt = 1;
  endwhile
  %вывод результатов
  if mc > 1
    retval = [im mc];
  else
    retval = 0;
  endif
endfunction

Mode1 = ModeSearch(s1,N)
s1(Mode1(1))
Mode2 = ModeSearch(s2,N)
s2(Mode2(1))
Mode3 = ModeSearch(s3,N)
if Mode3
  s3(Mode3(1))
else
  disp("No Mode");
endif

