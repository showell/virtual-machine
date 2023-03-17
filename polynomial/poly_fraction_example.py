from poly import Poly, set_math
from fraction_math import FractionMath
from fractions import Fraction

set_math(FractionMath)


def assert_str(p, s):
    if str(p) != s:
        raise AssertionError(f"You want {str(p)}")


def assert_equal(m, n):
    if m != n:
        raise AssertionError(f"{m} != {n}")


x = Poly.var("x")
y = Poly.var("y")
z = Poly.var("z")
a = Fraction(1, 3)
b = Fraction(2, 7)
c = Fraction(11, 4)
d = Fraction(5, 9)
one = FractionMath.one
zero = FractionMath.zero

p = (x + a) ** 4 + (y - b * z) * (x + c * y) + d * (z**7) * (b - x)

assert_str(
    p,
    "(x**4)+4/3*(x**3)+2/3*(x**2)+x*y+(-5/9)*x*(z**7)+(-2/7)*x*z+4/27*x+11/4*(y**2)+(-11/14)*y*z+10/63*(z**7)+1/81",
)

assert_str(p.apply(x=one, y=zero), "(-25/63)*(z**7)+(-2/7)*z+256/81")
assert_equal(p.eval(x=one, y=one, z=Fraction(1, 2)), Fraction(462431, 72576))

p = (x + Fraction(1, 2)) * (x - Fraction(1, 2))
assert_str(p, "(x**2)+(-1/4)")

q = x**2 - Fraction(1, 4)
assert_equal(p, q)
