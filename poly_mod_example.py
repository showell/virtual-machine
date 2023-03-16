# Show that modular arithmetic over polynomials behaves correctly.
# This is slightly hacky for now.
from poly import Integer, Value, Poly


def assert_str(p, s):
    if str(p) != s:
        raise AssertionError(f"You want {str(p)}")


def assert_equal(m, n):
    if m != n:
        raise AssertionError(f"{m} != {n}")


x = Poly.var("x")
y = Poly.var("y")
z = Poly.var("z")


def complicated_polynomial(*, x, y, z):
    assert type(x) == Poly
    assert type(y) == Poly
    assert type(z) == Poly
    return (
        (9 * (x**3)) * (z + 3)
        + 4 * ((y**6) ** 2) * 8 * (y**8)
        + 6 * (z**6) * 3
        + (x + 9) ** 2
    )


# Compute the polynomial over the space of integers.
p = complicated_polynomial(x=x, y=y, z=z)

assert_str(p, "9*(x**3)*z+27*(x**3)+(x**2)+18*x+32*(y**20)+18*(z**6)+81")

MODULUS = 10
mod = lambda n: n % MODULUS

# Create a function q that operates on smaller numbers
# with arithmetic relative to MODULUS.
q = p.transform_coefficients(mod)
assert_str(q, "9*(x**3)*z+7*(x**3)+(x**2)+8*x+2*(y**20)+8*(z**6)+1")

small_results = set()

# Show that p and q behave the same across their respective domains.
for x in range(MODULUS * 2):
    for y in range(MODULUS * 2):
        for z in range(MODULUS * 2):
            # Do a normal integer computation of the p polynomial.
            Value.eval_add = Integer.add
            Value.eval_mul = Integer.mul
            Value.eval_coeff_mul = Integer.mul

            big_result = p.eval(x=x, y=y, z=z)

            # Compute the q polynomial with modular arithmetic.
            Value.eval_add = lambda a, b: mod(a + b)
            Value.eval_mul = lambda a, b: mod(a * b)
            Value.eval_coeff_mul = lambda a, b: mod(a * b)

            small_result = q.eval(x=mod(x), y=mod(y), z=mod(z))

            # assert we are doing something non-trivial here
            assert big_result > MODULUS
            assert small_result < MODULUS

            # verify that mod(p(x,y,z)) == q(mod(x), mod(y), mod(z))
            assert_equal(mod(big_result), small_result)

            small_results.add(small_result)

# Make sure we found a bunch of interesting results.
assert set(small_results) == set(range(MODULUS))
