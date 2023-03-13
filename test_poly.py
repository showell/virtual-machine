from poly import VarPower, Term, Poly

vpn = VarPower("n", 5) 
assert str(vpn) == "(n**5)"
assert vpn.eval(2) == 32

vpx = VarPower("x", 3) 
assert str(vpx) == "(x**3)"
assert vpx.eval(2) == 8

term = Term([vpn, vpx], 3)
assert str(term) == "3*(n**5)*(x**3)"
assert term.eval(n=2, x=4) == 3 * (2 ** 5) * (4 ** 3)

term = Term.constant(17)
assert term.eval() == 17

term = Term.vp(5, "x", 2)
assert term.eval(x=4) == 80

term = 3 * Term.vp(2, "x", 1)
assert term.eval(x=10) == 60

term = Term.vp(2, "x", 1) * Term.vp(3, "y", 2) * Term.vp(10, "y", 20)
assert str(term) == "60*x*(y**22)"
assert term.sig() == "x*(y**22)"

term = Term.vp(3, "x", 4) ** 3
assert str(term) == "27*(x**12)"
assert str(-term) == "-27*(x**12)"

x = Term.var("x")
assert str(x**2 + 5*x**2) == "6*(x**2)"

t = Term.var("y") * Term.var("x") ** 2
assert str(t) == "(x**2)*y" 
    
x = Term.var("x")
y = Term.var("y")
t = 3 * (x ** 99) * (y ** 3)
t = t.reduce(y=2)
assert str(t) == "24*(x**99)"
t = t.reduce(x=1)
assert str(t) == "24"

# POLY TESTS


x = Term.var("x")
y = Term.var("y")
p = Poly([x, y])
assert str(p) == "x+y"
assert p.eval(x=5, y=2) == 7
assert str(p.reduce(x=8)) == "8+y"

x = Poly.var("height")
assert str(x) == "height"

n = Poly.var("n")
assert str(n+2) == "n+2"

x = Poly.var("x")
y = Poly.var("y")
z = Poly.var("z")
assert str(x+y+z) == "x+y+z"
assert str(2*(x+y)) == "2*x+2*y"

p = 3*x + y
assert str(p.reduce(y=4)) == "3*x+4"

assert str(x+x) == "2*x"



