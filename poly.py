import collections

"""
The Poly class works purely with integer poynomials.

It assumes the coefficients of the polynomials are integers,
as well as the powers, and it assumes that you plug in integer/float
values for the variables once you are ready to compute a value
of the polynomial.

It also assumes the powers of terms are non-negative.

It supports an arbitrary combination of variables, and for
convenience sake, it prevents you from having punctuation
characters in variables that would conflict with operators
like +, -, *, etc.
"""


class VarPower:
    def __init__(self, var, power):
        assert type(var) == str
        for c in ",*+/-()":
            assert not c in var
        assert type(power) == int
        assert power >= 0
        self.var = var
        self.power = power

    def __pow__(self, exponent):
        return VarPower(self.var, self.power * exponent)

    def __str__(self):
        if self.power == 1:
            return self.var
        return f"({self.var}**{self.power})"

    def eval(self, x):
        return x**self.power


class Term:
    def __init__(self, var_powers, coeff):
        assert type(var_powers) == list
        for var_power in var_powers:
            assert (type(var_power)) == VarPower
        assert type(coeff) == int
        vars = [vp.var for vp in var_powers]
        assert vars == sorted(vars)
        assert len(vars) == len(set(vars))

        sig = "*".join(str(vp) for vp in var_powers)
        self.var_powers = var_powers
        self.coeff = coeff
        self.var_dict = {vp.var: vp.power for vp in var_powers}
        self.sig = sig

    def __add__(self, other):
        assert type(other) == Term
        assert len(self.var_powers) == len(other.var_powers)
        assert self.sig == other.sig
        return Term(self.var_powers, self.coeff + other.coeff)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __neg__(self):
        return Term(self.var_powers, -1 * self.coeff)

    def __pow__(self, exponent):
        assert type(exponent) == int
        coeff = self.coeff**exponent
        vps = [vp**exponent for vp in self.var_powers]
        return Term(vps, coeff)

    def __rmul__(self, other):
        if type(other) == int:
            return Term(self.var_powers, self.coeff * other)
        elif type(other) == Term:
            return self.multiply_terms(other)
        else:
            assert False

    def __str__(self):
        c = self.coeff
        c_str = str(c) if c > 0 else f"({c})"
        if not self.var_powers:
            return c_str
        if self.coeff == 1:
            return self.sig
        return c_str + "*" + self.sig

    def apply(self, **vars):
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

    def eval(self, **vars):
        """
        If we get passed in vars that we don't know about,
        just ignore them.
        """
        for var in vars:
            assert type(var) == str
        assert self.variables().issubset(vars)
        product = self.coeff
        for vp in self.var_powers:
            product *= vp.eval(vars[vp.var])
        return product

    def key(self, var_list):
        return tuple(self.var_dict.get(var, 0) for var in var_list)

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

    def variables(self):
        return set(self.var_dict.keys())

    @staticmethod
    def constant(c):
        return Term([], c)

    @staticmethod
    def sum(terms):
        # This is a helper for Poly.
        assert len(terms) >= 1
        if len(terms) == 1:
            return terms[0]

        term = terms[0]
        sig = term.sig
        for other in terms[1:]:
            assert type(other) == Term
            assert other.sig == sig
            term += other

        return term

    @staticmethod
    def var(var):
        return Term([VarPower(var, 1)], 1)

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

    def __add__(self, other):
        return self.__radd__(other)

    def __sub__(self, other):
        return self + other * (-1)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __neg__(self):
        return self * (-1)

    def __pow__(self, exponent):
        assert exponent >= 0
        assert type(exponent) == int
        if exponent == 0:
            return Poly.constant(1)
        if exponent == 1:
            return self
        return self * self ** (exponent - 1)

    def __radd__(self, other):
        if type(other) == int:
            other = Poly.constant(other)
        assert type(other) == Poly
        return Poly(self.terms + other.terms)

    def __rmul__(self, other):
        if type(other) == int:
            return Poly([term * other for term in self.terms])
        elif type(other) == Term:
            raise Exception("Use Poly contructors to build up terms.")
        assert type(other) == Poly
        terms = [t1 * t2 for t1 in self.terms for t2 in other.terms]
        return Poly(terms)

    def __rsub__(self, other):
        if type(other) == int:
            other = Poly.constant(other)
        assert type(other) == Poly
        return -self + other

    def __str__(self):
        return "+".join(str(term) for term in self.terms)

    def apply(self, **vars):
        """
        This does a partial application of a subset of variables to
        our polynomial. I perhaps could have called this "partial",
        but I wanted to avoid confusion with possible future extensions
        related to partial derivates.
        """
        int_vars = {}
        poly = self
        for var, value in vars.items():
            if type(value) == int:
                int_vars[var] = value
            elif type(value) is Poly:
                assert False  # TODO
            else:
                raise ValueError("Improper type supplied")
        return poly.apply_int_vars(**int_vars)

    def apply_int_vars(self, **vars):
        my_vars = self.variables()
        assert set(vars).issubset(my_vars)
        for value in vars.values():
            assert type(value) == int
        return Poly([term.apply(**vars) for term in self.terms])

    def eval(self, **vars):
        my_vars = self.variables()
        if len(set(vars)) < len(my_vars):
            raise Exception("Not enough variables supplied. Maybe use apply?")

        for var, value in vars.items():
            if type(value) not in (int, float):
                raise ValueError(f"The value {value} for var {var} is neither int nor float.")
            assert type(value) in (int, float)
        return sum(term.eval(**vars) for term in self.terms)

    def simplify(self):
        buckets = collections.defaultdict(list)
        for term in self.terms:
            sig = term.sig
            buckets[sig].append(term)

        new_terms = []
        for sub_terms in buckets.values():
            term = Term.sum(sub_terms)
            if term.coeff != 0:
                new_terms.append(term)

        self.terms = new_terms
        sorted_vars = sorted(self.variables())
        self.terms.sort(key=lambda term: term.key(sorted_vars), reverse=True)

    def variables(self):
        vars = set()
        for term in self.terms:
            vars |= term.variables()
        return vars

    @staticmethod
    def constant(c):
        return Poly([Term.constant(c)])

    @staticmethod
    def var(label):
        return Poly([Term.var(label)])
