class Integer:
    zero = 0
    one = 1
    value_type = int

    @staticmethod
    def add(a, b):
        assert type(a) == int
        assert type(b) == int
        return a + b

    @staticmethod
    def mul(a, b):
        assert type(a) == int
        assert type(b) == int
        return a * b

    @staticmethod
    def negate(n):
        assert type(n) == int
        return -n

    @staticmethod
    def power(n, exp):
        assert type(n) == int
        assert type(exp) == int
        return n**exp
