import z3

array = [False, False, True, False, True, False]

idd = z3.Int("idd")

s = z3.Solver()

imps = [z3.And(array[i], idd == i) for i in range(len(array))]
print imps
haha = z3.Or(*imps)
print haha
s.add(haha)

s.add(idd != 2)

s.check()
print s.model()


