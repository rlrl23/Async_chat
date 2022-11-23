def fizzbuzz(fizz, buzz):
    i=1
    while 1:
        if i%fizz==0:
            result='fizz'
        elif i%buzz==0:
            result='buzz'
        else:
            result=i
        i+=1
        yield(result)

class FizzBuzz():
    def __init__(self, fizz, buzz):
        self.i=1
        self.fizz=fizz
        self.buzz=buzz

    def __iter__(self):
        return self
    def __next__(self):
        if self.i % self.fizz == 0:
            result = 'fizz'
        elif self.i % self.buzz == 0:
            result = 'buzz'
        else:
            result =self.i
        self.i+=1
        return result

b= FizzBuzz(3,5)
# print(type(b))
# print(b.__next__())
# print(b.__next__())
# print(b.__next__())
# print(b.__next__())
# print(b.__next__())
# print(b.__next__())
# print(b.__next__())
# print(b.__next__())
# print(b.__next__())
# print(b.__next__())
a= fizzbuzz(3,5)
# print(type(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# for i in a:
#     print(i)
for i in b:
    print(i)