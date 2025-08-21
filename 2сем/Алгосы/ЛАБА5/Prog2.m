%алгоритм поиска моды%
N = 0;
function retval = ModeSearch(S, N)
  mt = 1;
  mc = 1;
  im = 1;
  i = 1;
  while i<N-1
    j=i;
    while (j<N && S(j)==S(j+1))
      mt = mt+1;
      j = j+1;
    endwhile
    i = i+mt;
    if mt>mc
      mc = mt;
      im = i-mt;
    endif
    mt = 1;
  endwhile
  if mc > 1
    retval = [im mc];
  else
    retval = 0;
  endif
endfunction

function sortedArray = quicksort(arr)
    if numel(arr) <= 1
        sortedArray = arr;
        return;
    endif

    pivot = arr(1);
    less = arr(arr < pivot);
    equal = arr(arr == pivot);
    greater = arr(arr > pivot);

    sortedArray = [quicksort(less), equal, quicksort(greater)];
endfunction

for i =4:7
  N = 10^i;
  s = fix(50*rand([1 N]));
  s = quicksort(s);
  tic;
  M = ModeSearch(s, N)
  t = toc
  disp("---------------------------");
endfor



