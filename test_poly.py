from poly import Poly

"""
These are very raw tests that I built up while developing the 
library.

For more polished examples see poly_example.py
"""

x = Poly.var("x")
y = Poly.var("y")
z = Poly.var("z")
h = Poly.var("height")
n = Poly.var("n")
zero = Poly.zero()
one = Poly.one()

assert zero.is_zero()
assert one.is_one()
assert not zero.is_one()
assert not one.is_zero()

assert (x - x).is_zero()
assert x.apply(x=1).is_one()

p = x + y
assert not p.is_zero()
assert not p.is_one()

assert str(p) == "x+y"
assert p.eval(x=5, y=2) == 7
assert str(p.apply(x=8)) == "y+8"

assert str(h) == "height"

assert str(n + 2) == "n+2"

assert str(x + y + z) == "x+y+z"

assert str(2 * (x + y)) == "2*x+2*y"

p = 3 * x + y
assert str(p.apply(y=4)) == "3*x+4"

assert str(x + x) == "2*x"

assert str(-(x + x)) == "(-2)*x"

assert str(x + y + z - y) == "x+z"

diff_squares = (x + y) * (x - y)
assert str(diff_squares) == "(x**2)+(-1)*(y**2)"
assert str(diff_squares.apply(x=16)) == "(-1)*(y**2)+256"

p = (x + 4) * (x - 4)
assert str(p) == "(x**2)+(-16)"

assert str(x**0) == "1"
assert str((x + y) ** 1) == "x+y"
assert str(x**2) == "(x**2)"
p = (x + y) ** 2
assert str(p) == "(x**2)+2*x*y+(y**2)"
p = (x**2 + y) ** 3
assert str(p) == "(x**6)+3*(x**4)*y+3*(x**2)*(y**2)+(y**3)"
assert str(p.apply(y=1)) == "(x**6)+3*(x**4)+3*(x**2)+1"


assert str(1 + x) == "x+1"
assert str((1 + x) ** 2) == "(x**2)+2*x+1"

assert (x**2 + y + z).variables() == {"x", "y", "z"}

assert str(1 - x) == "(-1)*x+1"

assert str(x + 0) == "x"
assert str(x - 2) == "x+(-2)"
assert str(x - x) == "0"
assert str(x - x + y) == "y"

assert str(sum([])) == "0"
assert str(sum([x])) == "x"
assert str(sum([y, x, z**2])) == "x+y+(z**2)"

assert str(Poly.sum([])) == "0"
assert str(Poly.sum([x])) == "x"
assert str(Poly.sum([y, x, z**2])) == "x+y+(z**2)"

assert str(zero) == "0"
assert zero.eval() == 0
assert str(0 - x) == "(-1)*x"
assert str(zero - x) == "(-1)*x"

p = (x**2 + 1).substitute("x", y + 1)
assert str(p) == "(y**2)+2*y+2"

p = (x**2 + 5).substitute("x", x + 1)
assert str(p) == "(x**2)+2*x+6"

p = (x**2 + 5 * x).substitute("x", x**2)
assert str(p) == "(x**4)+5*(x**2)"

p = (x**2 + 5 * z).substitute("x", y**2)
assert str(p) == "(y**4)+5*z"

p = (x**2 + 5 * z).substitute("x", 100 * y**2 + 3)
assert str(p) == "10000*(y**4)+600*(y**2)+5*z+9"


assert (0 * p) == zero
assert (p * 0) == zero
assert (p * 1) == p
assert (1 * p) == p
assert (p + 0) == p
assert (0 + p) == p
assert (p - 0) == p
assert (0 - p) == p.negated() == -p
assert Poly.add_polys(p, zero) == p
assert Poly.add_polys(zero, p) == p
assert Poly.multiply_polys(zero, p) == zero
assert Poly.multiply_polys(p, zero) == zero
assert Poly.multiply_polys(one, p) == p
assert Poly.multiply_polys(p, one) == p
