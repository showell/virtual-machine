class Modulus:
    def __init__(self, modulus):
        assert modulus > 0
        assert type(modulus) == int
        self.zero = 0
        self.one = 1
        self.value_type = int
        self.modulus = modulus

    def add(self, a, b):
        self.check(a)
        self.check(b)
        return (a + b) % self.modulus

    def check(self, x):
        assert type(x) == int
        assert 0 <= x
        assert x < self.modulus

    def mul(self, a, b):
        self.check(a)
        self.check(b)
        return (a * b) % self.modulus

    def negate(self, n):
        self.check(n)
        return self.modulus - n

    def power(self, n, exponent):
        self.check(n)
        assert type(exponent) == int
        assert exponent >= 0

        def repeated_multiply(exp):
            if exp == 0:
                return 1
            return self.mul(n, repeated_multiply(exp - 1))

        return repeated_multiply(exponent)
