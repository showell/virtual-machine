from poly import Poly


def assert_str(p, s):
    if str(p) != s:
        raise AssertionError(f"You want {str(p)}")


def assert_equal(m, n):
    if m != n:
        raise AssertionError(f"{m} != {n}")


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
a = 2 * x + 3 * z + y
b = 4 * z + y + x
assert_equal(str(a * a), str(a**2))
assert_equal(str(a + a), str(2 * a))
assert_equal(str(b + b), str(2 * b))
assert_equal(str(a + b), str(b + a))
assert_equal(str(a * b), str(b * a))

# We allow "==" between Poly objects, and equality means that
# the two polynomials use the same variable names and compute
# values in an identical fashion.
assert a != b
assert a**2 != b**2

assert a != a + 1
assert a != a - 3
assert a * 3 != a * 2
assert a**4 != a**3

assert one == zero + 1
assert two == one + 1
assert three == two + 1

assert 0 * a == a * 0
assert 1 * a == a * 1
assert 2 * a == a + a
assert 3 * a == a + a + a
assert a - a == zero
assert 2 * a - a - a == zero
assert zero + a == a + 0
assert one + a == a + 1
assert 2 * one + a == a + 2
assert three * a == a + a + a
assert a * a == a**2
assert a + a == two * a
assert b + b == 2 * b
assert a + b == b + a
assert a * b == b * a
assert (a + 3) ** 2 == a**2 + 6 * a + 9
