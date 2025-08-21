import math
b = a = 0.3
h = 0.058333
S = ((0.004735+0.00677320)/2)*h
def f(x):
    y = math.sin(x)/((3*x+7)**2)
    return y
for i in range(1,24):
    b = a+h*i
    S+= h*f(b)

print(S)
print(b)