import collections

class VarPower:
    def __init__(self, var, power):
        assert type(var) == str
        assert not "," in var
        assert not "*" in var
        assert type(power) == int
        assert power >= 0
        self.var = var
        self.power = power

    def eval(self, x):
        return x ** self.power

    def __str__(self):
        return f"({self.var}**{self.power})"

class Term:
    def __init__(self, var_powers, coeff):
        assert type(var_powers) == list
        for var_power in var_powers:
            assert(type(var_power)) == VarPower
        assert type(coeff) == int
        self.var_powers = var_powers
        self.vars = [vp.var for vp in var_powers]
        assert self.vars == sorted(self.vars)
        assert len(self.vars) == len(set(self.vars))
        self.coeff = coeff

    def eval(self, vars):
        assert type(vars) == dict
        for var in vars:
            assert type(var) == str
            assert var in self.vars
        assert len(vars) == len(self.vars)
        product = self.coeff
        for vp in self.var_powers:
            product *= vp.eval(vars[vp.var])
        return product

    def __add__(self, other):
        assert type(other) == Term
        assert len(self.var_powers) == len(other.var_powers)
        assert self.sig() == other.sig()
        return Term(self.var_powers, self.coeff + other.coeff)

    def __rmul__(self, other):
        if type(other) == int:
            return Term(self.var_powers, self.coeff * other)
        elif type(other) == Term:
            return self.multiply_terms(other)
        else:
            assert False

    def __mul__(self, other):
        return self.__rmul__(other)

    def __neg__(self):
        return Term(self.var_powers, -1 * self.coeff)

    def __pow__(self, other):
        assert type(other) == int
        coeff = self.coeff ** other
        vps = [VarPower(vp.var, vp.power * other) for vp in self.var_powers]
        return Term(vps, coeff)

    def multiply_terms(self, other):
        coeff = self.coeff * other.coeff
        powers = collections.defaultdict(int)
        for vp in self.var_powers:
            powers[vp.var] = vp.power
        for vp in other.var_powers:
            powers[vp.var] += vp.power
        parms = list(powers.items())
        parms.sort()
        vps = [VarPower(var, power) for var, power in parms]
        return Term(vps, coeff)

    def sig(self):
        return "*".join(str(vp) for vp in self.var_powers)

    def __str__(self):
        return str(self.coeff) + "*" + self.sig()

    @staticmethod
    def var(var):
        return Term([VarPower(var, 1)], 1)

    @staticmethod
    def constant(c):
        return Term([], c) 

    @staticmethod
    def vp(c, var, power):
        assert type(c) == int
        assert type(var) == str
        assert type(power) == int
        return Term([VarPower(var, power)], c)

vpn = VarPower("n", 5) 
assert str(vpn) == "(n**5)"
assert vpn.eval(2) == 32

vpx = VarPower("x", 3) 
assert str(vpx) == "(x**3)"
assert vpx.eval(2) == 8

term = Term([vpn, vpx], 3)
assert str(term) == "3*(n**5)*(x**3)"
assert term.eval(dict(n=2, x=4)) == 3 * (2 ** 5) * (4 ** 3)

term = Term.constant(17)
assert term.eval(dict()) == 17

term = Term.vp(5, "x", 2)
assert term.eval(dict(x=4)) == 80

term = 3 * Term.vp(2, "x", 1)
assert term.eval(dict(x=10)) == 60

term = Term.vp(2, "x", 1) * Term.vp(3, "y", 2) * Term.vp(10, "y", 20)
assert str(term) == "60*(x**1)*(y**22)"
assert term.sig() == "(x**1)*(y**22)"

term = Term.vp(3, "x", 4) ** 3
assert str(term) == "27*(x**12)"
assert str(-term) == "-27*(x**12)"

x = Term.var("x")
assert str(x**2 + 5*x**2) == "6*(x**2)"

t = Term.var("y") * Term.var("x") ** 2
assert str(t) == "1*(x**2)*(y**1)" 
