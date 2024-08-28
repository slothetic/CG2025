import copy
a =  set([1,2,3])
b = copy.copy(a)
a.add(4)
print(b)
