from poly import VarPower, Term, Poly

vpn = VarPower("n", 5)
assert str(vpn) == "(n**5)"
assert vpn.eval(2) == 32

vpx = VarPower("x", 3)
assert str(vpx) == "(x**3)"
assert vpx.eval(2) == 8

assert str(vpx**1) == "(x**3)"
assert str(vpx**4) == "(x**12)"

## Term tests

x = Term.var("x")
y = Term.var("y")

assert (x * 0).eval() == 0
assert (x * 1).eval(x=7) == 7

term = Term(3, [vpn, vpx])
assert str(term) == "3*(n**5)*(x**3)"
assert str(term**0) == "1"
assert str(term**1) == "3*(n**5)*(x**3)"
assert term.eval(n=2, x=4) == 3 * (2**5) * (4**3)

term = Term.constant(17)
assert term.eval() == 17

term = 5 * x**2
assert term.eval(x=4) == 80

term = 3 * 2 * x
assert term.eval(x=10) == 60

term = 2 * x * 3 * (y**2) * 10 * (y**20)
assert str(term) == "60*x*(y**22)"
assert term.sig == "x*(y**22)"

term = (3 * (x**4)) ** 3
assert str(term) == "27*(x**12)"
assert str(-term) == "(-27)*(x**12)"

assert str(x**2 + 5 * x**2) == "6*(x**2)"

t = y * x**2
assert str(t) == "(x**2)*y"
assert t.variables() == {"x", "y"}

t = 3 * (x**99) * (y**3)
t = t.apply(y=2)
assert str(t) == "24*(x**99)"
t = t.apply(x=1)
assert str(t) == "24"

p = 5 * (x**2) * (y**3)
term, power = p.factorize_on_var("x")
assert str(term) == "5*(y**3)"
assert power == 2

term, power = p.factorize_on_var("y")
assert str(term) == "5*(x**2)"
assert power == 3

term, power = p.factorize_on_var("z")
assert str(term) == str(p)
assert power == 0

# POLY TESTS


x = Poly.var("x")
y = Poly.var("y")
z = Poly.var("z")
h = Poly.var("height")
n = Poly.var("n")
zero = Poly.zero()

p = x + y
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

p = 10 * x + 10 * y
f = p.eval(x=1.1, y=2.2)
assert f == 33

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
