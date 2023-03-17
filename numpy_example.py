from numpy.polynomial.polynomial import Polynomial
from poly import Poly

def numpy_eval(vector, *, x):
    return int(Polynomial(vector)(x))

x = Poly.var("x")
p = (2*x + 1) * (2*x - 1)
vector = p.numpy_vector()
assert vector == [-1, 0, 4]

assert p.eval(x=7) == 195
assert numpy_eval(vector, x=7) == 195

for i in range(1000):
    assert p.eval(x=i) == numpy_eval(vector, x=i)
