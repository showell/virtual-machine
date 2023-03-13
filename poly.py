import collections


class VarPower:
    def __init__(self, var, power):
        assert type(var) == str
        for c in ",*+/-()":
            assert not c in var
        assert type(power) == int
        assert power >= 0
        self.var = var
        self.power = power

    def eval(self, x):
        return x**self.power

    def __str__(self):
        if self.power == 1:
            return self.var
        return f"({self.var}**{self.power})"


class Term:
    def __init__(self, var_powers, coeff):
        assert type(var_powers) == list
        for var_power in var_powers:
            assert (type(var_power)) == VarPower
        assert type(coeff) == int
        self.var_powers = var_powers
        self.vars = [vp.var for vp in var_powers]
        assert self.vars == sorted(self.vars)
        assert len(self.vars) == len(set(self.vars))
        self.coeff = coeff

    def eval(self, **vars):
        """
        If we get passed in vars that we don't know about,
        just ignore them.
        """
        for var in vars:
            assert type(var) == str
        assert set(vars) & set(self.vars) == set(self.vars)
        product = self.coeff
        for vp in self.var_powers:
            product *= vp.eval(vars[vp.var])
        return product

    def reduce(self, **vars):
        """
        If we get passed in vars that we don't know about,
        just ignore them.
        """
        for var in vars:
            assert type(var) == str
        new_coeff = self.coeff
        new_vps = []
        for vp in self.var_powers:
            if vp.var in vars:
                new_coeff *= vp.eval(vars[vp.var])
            else:
                new_vps.append(vp)
        return Term(new_vps, new_coeff)

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
        coeff = self.coeff**other
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
        if not self.var_powers:
            return str(self.coeff)
        if self.coeff == 1:
            return self.sig()
        return str(self.coeff) + "*" + self.sig()

    @staticmethod
    def sum(terms):
        # This is a helper for Poly.
        assert len(terms) >= 1
        if len(terms) == 1:
            return terms[0]

        term = terms[0]
        sig = term.sig()
        for other in terms[1:]:
            assert type(other) == Term
            assert other.sig() == sig
            term += other

        return term

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


class Poly:
    def __init__(self, terms):
        if type(terms) == Term:
            raise Exception("Pass in a list of Terms or use Poly's other constructors.")
        assert type(terms) == list
        for term in terms:
            assert type(term) == Term
        self.terms = terms
        self.simplify()

    def simplify(self):
        buckets = collections.defaultdict(list)
        for term in self.terms:
            sig = term.sig()
            buckets[sig].append(term)

        new_terms = []
        for sub_terms in buckets.values():
            term = Term.sum(sub_terms)
            if term.coeff != 0:
                new_terms.append(term)

        self.terms = new_terms

    def eval(self, **vars):
        return sum(term.eval(**vars) for term in self.terms)

    def reduce(self, **vars):
        return Poly([term.reduce(**vars) for term in self.terms])

    def __str__(self):
        return "+".join(str(term) for term in self.terms)

    def __add__(self, other):
        if type(other) == int:
            other = Poly.constant(other)
        assert type(other) == Poly
        return Poly(self.terms + other.terms)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __rmul__(self, other):
        if type(other) == int:
            return Poly([term * other for term in self.terms])
        else:
            assert False

    @staticmethod
    def constant(c):
        return Poly([Term.constant(c)])

    @staticmethod
    def var(label):
        return Poly([Term.var(label)])
