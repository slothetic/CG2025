import math


class MyNum:
    # def __new__(cls, num, den=1):
    #     # print(cls)
    #     # print(args)
    #     if isinstance(num, MyNum):
    #         num, den = num.num, num.den
    #     return tuple.__new__(cls, (num, den))
    # @property
    # def num(self):
    #     return tuple.__getitem__(self, 0)
    # @property
    # def den(self):
    #     return tuple.__getitem__(self, 1)
    # def __setattr__(self, name, args):
    #     # print(name)
    #     if name=="num":
    #         self = tuple.__new__(MyNum, (args, self.den))
    #     if name=="den":
    #         self = tuple.__new__(MyNum, (self.num, args))
    def __init__(self, num, den = 1):
        if den==0:
            raise Exception("denominator cannot be 0!")
        if type(num)==int:
            self.num = num
            self.den = den
            self.abbr()
        elif type(num)==MyNum:
            self.num = num.num
            self.den = num.den
            self.abbr()
        elif type(num)==float:
            self.num, self.den = num.as_integer_ratio()

    def __hash__(self):
        return hash((self.num, self.den))

    def __add__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        nnum = self.num*n.den+self.den*n.num
        nden = self.den*n.den
        return MyNum(nnum, nden)

    def __iadd__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        nnum = self.num*n.den+self.den*n.num
        nden = self.den*n.den
        self.num = nnum
        self.den = nden
        self.abbr()
        return self
    
    def __sub__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        nnum = self.num*n.den-self.den*n.num
        nden = self.den*n.den
        return MyNum(nnum, nden)

    def __isub__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        nnum = self.num*n.den-self.den*n.num
        nden = self.den*n.den
        self.num = nnum
        self.den = nden
        self.abbr()
        return self
    
    def __mul__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        nnum = self.num*n.num
        nden = self.den*n.den
        return MyNum(nnum, nden)

    def __imul__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        nnum = self.num*n.num
        nden = self.den*n.den
        self.num = nnum
        self.den = nden
        self.abbr()
        return self
    
    def __truediv__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        if n==MyNum(0):
            raise Exception("MyNum cannot be divided by 0!")
        nnum = self.num*n.den
        nden = self.den*n.num
        return MyNum(nnum, nden)

    def __itruediv__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        if n==MyNum(0):
            raise Exception("MyNum cannot be divided by 0!")
        nnum = self.num*n.den
        nden = self.den*n.num
        self.num = nnum
        self.den = nden
        self.abbr()
        return self

    def __neg__(self):
        return MyNum(-self.num, self.den)

    def __lt__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        return self.num*n.den<self.den*n.num
    
    def __le__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        return self.num*n.den<=self.den*n.num
    
    def __gt__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        return self.num*n.den>self.den*n.num
    
    def __ge__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        return self.num*n.den>=self.den*n.num
    
    def __eq__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        return self.den == n.den and self.num == n.num
            
    def __ne__(self, n):
        if type(n)!=MyNum:
            n = MyNum(n)
        return self.den != n.den or self.num != n.num
    
    def __str__(self):
        if self.den ==1:
            return str(self.num)
        else:
            return "\""+str(self.num)+"/"+str(self.den)+"\""
        
    def __float__(self):
        return self.num/self.den
    
    def __abs__(self):
        return MyNum(abs(self.num), abs(self.den))
    
    def __int__(self):
        return int(self.num/self.den)
        
    
    def abbr(self):
        if self.num == 0:
            self.den = 1
        else:
            gcd_val = math.gcd(abs(self.num), abs(self.den))
            sgn = (self.num>0 and self.den>0) or (self.num<0 and self.den < 0)
            self.num = abs(self.num)//gcd_val
            self.den = abs(self.den)//gcd_val
            if not sgn:
                self.num = -self.num

    def toFloat(self):
        return self.num/self.den
    
    def toString(self):
        if self.den ==1:
            return self.num
        else:
            return str(self.num)+"/"+str(self.den)



# a = MyNum(1,2)
# b = a
# c = MyNum(3,2)
# a+=1
# print(a,b)
# print(a==MyNum(3,2))
# print(a==c)
# C = set([a,b])
# C = set([1,2])
# print(C)

# C.add(c)
# print(C)
# print(MyNum(1,2) is MyNum(1,2))