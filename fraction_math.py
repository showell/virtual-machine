from fractions import Fraction


class FractionMath:
    zero = Fraction(0)
    one = Fraction(1)
    value_type = Fraction

    @staticmethod
    def add(a, b):
        assert type(a) == Fraction
        assert type(b) == Fraction
        return a + b

    @staticmethod
    def mul(a, b):
        assert type(a) == Fraction
        assert type(b) == Fraction
        return a * b

    @staticmethod
    def negate(n):
        assert type(n) == Fraction
        return -n

    @staticmethod
    def power(n, exp):
        assert type(n) == Fraction
        assert type(exp) == int
        return n**exp
