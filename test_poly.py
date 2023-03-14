from poly import VarPower, Term, Poly

vpn = VarPower("n", 5)
assert str(vpn) == "(n**5)"
assert vpn.eval(2) == 32

vpx = VarPower("x", 3)
assert str(vpx) == "(x**3)"
assert vpx.eval(2) == 8

term = Term([vpn, vpx], 3)
assert str(term) == "3*(n**5)*(x**3)"
assert term.eval(n=2, x=4) == 3 * (2**5) * (4**3)

term = Term.constant(17)
assert term.eval() == 17

term = Term.vp(5, "x", 2)
assert term.eval(x=4) == 80

term = 3 * Term.vp(2, "x", 1)
assert term.eval(x=10) == 60

term = Term.vp(2, "x", 1) * Term.vp(3, "y", 2) * Term.vp(10, "y", 20)
assert str(term) == "60*x*(y**22)"
assert term.sig == "x*(y**22)"

term = Term.vp(3, "x", 4) ** 3
assert str(term) == "27*(x**12)"
assert str(-term) == "(-27)*(x**12)"

x = Term.var("x")
assert str(x**2 + 5 * x**2) == "6*(x**2)"

t = Term.var("y") * Term.var("x") ** 2
assert str(t) == "(x**2)*y"
assert t.variables() == {"x", "y"}

x = Term.var("x")
y = Term.var("y")
t = 3 * (x**99) * (y**3)
t = t.apply(y=2)
assert str(t) == "24*(x**99)"
t = t.apply(x=1)
assert str(t) == "24"

# POLY TESTS


x = Term.var("x")
y = Term.var("y")
p = Poly([x, y])
assert str(p) == "x+y"
assert p.eval(x=5, y=2) == 7
assert str(p.apply(x=8)) == "y+8"

h = Poly.var("height")
assert str(h) == "height"

n = Poly.var("n")
assert str(n + 2) == "n+2"

x = Poly.var("x")
y = Poly.var("y")
z = Poly.var("z")
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
