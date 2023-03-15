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

# Show that modular arithmetic over polynomials behaves correctly.
# This is slightly hacky for now.
from poly import Value

# Compute the polynomial over the space of integers.
p = 23 * (x**3) + 41 * (y**5) + 17 * (z ** 7) + 37
assert_str(p, "23*(x**3)+41*(y**5)+17*(z**7)+37")

MODULUS = 11
mod = lambda n: n % MODULUS

# Create a function q that operates on smaller numbers
# with arithmetic relative to MODULUS.
q = p.transform_coefficients(mod)
assert_str(q, "(x**3)+8*(y**5)+6*(z**7)+4")

# Show that p and q behave the same across their respective domains.
for x in range(MODULUS * 2):
    for y in range(MODULUS * 2):
        for z in range(MODULUS * 2):
            # Do a normal integer computation of the p polynomial.
            Value.eval_add = Value.add
            Value.eval_mul = Value.mul
            Value.eval_power = Value.power
            Value.eval_coeff_mul = Value.mul

            big_result = p.eval(x=x, y=y, z=z)

            # Compute the q polynomial with modular arithmetic.
            Value.eval_add = lambda a, b: mod(a + b)
            Value.eval_mul = lambda a, b: mod(a * b)
            Value.eval_power = lambda n, exp: mod(n ** exp)
            Value.eval_coeff_mul = lambda a, b: mod(a * b)

            small_result = q.eval(x=mod(x), y=mod(y), z=mod(z))

            # assert we are doing something non-trivial here
            assert small_result != big_result

            # verify that mod(p(x,y,z)) == q(mod(x), mod(y), mod(z)) 
            assert_equal(mod(big_result), small_result)