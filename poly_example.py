from poly import Poly


def assert_str(p, s):
    if str(p) != s:
        raise AssertionError(f"You want {str(p)}")


def assert_equal(m, n):
    if m != n:
        raise AssertionError(f"{m} != {n}")


u = Poly.var("u")
x = Poly.var("x")
y = Poly.var("y")
z = Poly.var("z")
zero = Poly.zero()
one = Poly.one()
two = Poly.constant(2)
three = Poly.constant(3)

# Poly supports symbolic manipulation.
assert_str((x + 1) * (x - 1), "(x**2)+(-1)")
assert_str((x + 2) * (x + 3), "(x**2)+5*x+6")
assert_str((x + 2) ** 3, "(x**3)+6*(x**2)+12*x+8")
assert_str((3 * x + 1) ** 4, "81*(x**4)+108*(x**3)+54*(x**2)+12*x+1")

# You can use multiple variables.
assert_str(x + y + z - y, "x+z")
assert_str((x + y) * (z + y), "x*y+x*z+(y**2)+y*z")

# You can easily get binomial expansions.
assert_str(
    (x + y) ** 6,
    "(x**6)+6*(x**5)*y+15*(x**4)*(y**2)+20*(x**3)*(y**3)+15*(x**2)*(y**4)+6*x*(y**5)+(y**6)",
)

# You can evaluate polynomials.
h = Poly.var("height")
w = Poly.var("width")
a = w * h
assert_str(a, "height*width")
assert_equal(a.eval(width=10, height=5), 50)

p = (3 * x + 1) * (4 * y**2 + 3 * y + 5)
assert_equal(p.eval(x=10, y=10), 31 * 435)
assert_equal(p.eval(x=1000, y=10), 3001 * 435)
assert_equal(p.eval(x=1000, y=100), 3001 * 40305)

# Polynomials get simplified and stringifed in a consistent manner.
p = 2 * x + 3 * z + y
q = 4 * z + y + x
assert_equal(str(p * p), str(p**2))
assert_equal(str(p + p), str(2 * p))
assert_equal(str(q + q), str(2 * q))
assert_equal(str(p + q), str(q + p))
assert_equal(str(p * q), str(q * p))

# We allow "==" between Poly objects, and equality means that
# the two polynomials use the same variable names and compute
# values in an identical fashion.
assert zero != one
assert one != zero
assert x != y
assert y != z
assert z != x

assert x == x

assert one == zero + 1
assert two == one + 1
assert three == two + 1

assert one * 1 == one
assert two * 1 == two
assert three * 1 == three

assert one - 1 == zero
assert two - 1 == one
assert three - 1 == two

p = 12 * x + 39 * (z**4)
q = z + 111 * y + x - 2

assert p != q
assert p**2 != q**2

assert p != p + 1
assert p != p - 3
assert p * 3 != p * 2
assert p**4 != p**3

assert 0 * p == p * 0
assert 1 * p == p * 1
assert 2 * p == p + p
assert 3 * p == p + p + p
assert p - p == zero
assert 2 * p - p - p == zero
assert zero + p == p + 0
assert one + p == p + 1
assert 2 * one + p == p + 2
assert three * p == p + p + p
assert p * p == p**2
assert p + p == two * p
assert q + q == 2 * q
assert p + q == q + p
assert p * q == q * p
assert 2 * p + q == p + p + q
assert (p + 3) ** 2 == p**2 + 6 * p + 9

# You can do partial application of variable assignments on polynomials.
assert (x + y**2).apply(y=2) == x + 4
assert (x + y**2 + z).apply(y=3) == x + 9 + z
assert (x + y + z + 4).apply(x=1000, y=200, z=30) == Poly.constant(1234)
assert (x + y + z + 4).apply(x=1000, y=200, z=30).eval() == 1234
assert (x + y + z + 4).apply(x=1000, y=200) == z + 1204
assert (x + y + z + 4).apply(x=1000, y=200).eval(z=30) == 1234

# Partial application always returns a new polynomial.
p = (x + 43) * (y - 37) * (z + 2)
assert_equal(p.variables(), {"x", "y", "z"})
assert type(p.apply(x=5, y=2, z=44)) == Poly
assert type(p.apply(x=9, y=8)) == Poly
assert type(p.apply(x=5, z=22)) == Poly

# Each partial application of a variable results in a polynomial with
# a subset of variables from the original one.
assert_equal(p.apply(x=5, z=22).variables(), {"y"})

# We allow silly calls to apply that do nothing.
assert p.apply() == p

# Compose functions
f = x + 1
g = y**2 + 3
gf = g.substitute("y", f)
assert gf == (x + 1) ** 2 + 3
assert gf == x**2 + 2 * x + 4

# For multi-variable fuctions, you can substitute variables as well.
# (This is function composition in disguise.)

assert (2 * x + 1).substitute("x", u + 3) == 2 * u + 7

p = (2 * x + 1) * (2 * y + 1) * z
assert_equal(p.variables(), {"x", "y", "z"})
q = p.substitute("x", u + 3)
assert_equal(q, (2 * u + 7) * (2 * y + 1) * z)
assert_str(q, "4*u*y*z+2*u*z+14*y*z+7*z")
assert_equal(q.variables(), {"u", "y", "z"})

# If you have a large polynomial that you will need to evaluate
# many times, then you can take advantage of the fact that the
# polynomial strings are valid Python, and you can have Python
# compile the expression on the fly.  For safety reasons I do not
# provide a convenient way to do that from Poly itself, but the
# pattern is pretty easy and provided below.
p = (x + 5) * (y - 2) ** 3 + x ** 3 - y ** 4
assert_str(p, "(x**3)+x*(y**3)+(-6)*x*(y**2)+12*x*y+(-8)*x+(-1)*(y**4)+5*(y**3)+(-30)*(y**2)+60*y+(-40)")
p_code_object = compile(str(p), "p", "eval")
evaled_value = eval(p_code_object, dict(x=152345, y=792))
assert_equal(evaled_value, p.eval(x=152345, y=792))
assert_equal(evaled_value, 3610495987987929)

# See also poly_mod_example.py
