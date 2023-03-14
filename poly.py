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
        assert exponent >= 1
        if exponent == 1:
            return self
        return VarPower(self.var, self.power * exponent)

    def __str__(self):
        if self.power == 1:
            return self.var
        return f"({self.var}**{self.power})"

    def eval(self, x):
        return x**self.power


class Term:
    def __init__(self, coeff, var_powers):
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
        return Term(self.coeff + other.coeff, self.var_powers)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __neg__(self):
        return Term(-1 * self.coeff, self.var_powers)

    def __pow__(self, exponent):
        assert type(exponent) == int
        assert exponent >= 0
        if exponent == 0:
            return Term.one()

        if exponent == 1:
            return self

        coeff = self.coeff**exponent
        vps = [vp**exponent for vp in self.var_powers]
        return Term(coeff, vps)

    def __rmul__(self, other):
        if type(other) == int:
            if other == 0:
                return Term.zero()
            if other == 1:
                assert self
            return Term(self.coeff * other, self.var_powers)
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
        if not set(vars) & set(self.var_dict):
            return self
        new_coeff = self.coeff
        new_vps = []
        for vp in self.var_powers:
            if vp.var in vars:
                new_coeff *= vp.eval(vars[vp.var])
            else:
                new_vps.append(vp)
        return Term(new_coeff, new_vps)

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

    def factorize_on_var(self, excluded_var):
        var_powers = [vp for vp in self.var_powers if vp.var != excluded_var]
        coeff = self.coeff
        power_of_excluded_var = self.var_dict.get(excluded_var, 0)
        return (Term(coeff, var_powers), power_of_excluded_var)

    def is_one(self):
        return self.coeff == 1 and len(self.var_powers) == 0

    def key(self, var_list):
        return tuple(self.var_dict.get(var, 0) for var in var_list)

    def multiply_terms(self, other):
        if other.coeff == 0:
            return Term.zero()
        elif other.is_one():
            return self

        coeff = self.coeff * other.coeff
        powers = collections.defaultdict(int)
        for vp in self.var_powers:
            powers[vp.var] = vp.power
        for vp in other.var_powers:
            powers[vp.var] += vp.power
        parms = list(powers.items())
        parms.sort()
        vps = [VarPower(var, power) for var, power in parms]
        return Term(coeff, vps)

    def variables(self):
        return set(self.var_dict.keys())

    @staticmethod
    def constant(c):
        return Term(c, [])

    @staticmethod
    def one():
        return Term(1, [])

    @staticmethod
    def sum(terms):
        # This is a helper for Poly.
        assert len(terms) >= 1
        if len(terms) == 1:
            return terms[0]

        term = terms[0]
        sig = term.sig
        coeff = term.coeff
        var_powers = term.var_powers
        for other in terms[1:]:
            assert type(other) == Term
            assert other.sig == sig
            coeff += other.coeff

        return Term(coeff, var_powers)

    @staticmethod
    def var(var):
        return Term(1, [VarPower(var, 1)])

    @staticmethod
    def zero():
        return Term(0, [])


class Poly:
    def __init__(self, terms):
        if type(terms) == Term:
            raise Exception("Pass in a list of Terms or use Poly's other constructors.")
        assert type(terms) == list
        for term in terms:
            assert type(term) == Term
        self.terms = terms
        self.simplify()
        self.put_terms_in_order()

    def __add__(self, other):
        return self.__radd__(other)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __neg__(self):
        return self * (-1)

    def __pow__(self, exponent):
        assert exponent >= 0
        assert type(exponent) == int
        if exponent == 0:
            return Poly.one()
        if exponent == 1:
            return self
        return self * self ** (exponent - 1)

    def __radd__(self, other):
        if type(other) == int:
            if other == 0:
                return self
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
        if len(self.terms) == 0:
            return "0"
        return "+".join(str(term) for term in self.terms)

    def __sub__(self, other):
        if type(other) == int:
            return self + Poly.constant(-other)
        return self + other * (-1)

    def apply(self, **vars):
        """
        This does a partial application of a subset of variables to
        our polynomial. I perhaps could have called this "partial",
        but I wanted to avoid confusion with possible future extensions
        related to partial derivates.
        """
        for var, value in vars.items():
            if type(value) is Poly:
                raise ValueError("Use Poly.substitute instead")
            elif type(value) != int:
                raise ValueError("Improper type supplied")
        my_vars = self.variables()
        assert set(vars).issubset(my_vars)
        return Poly([term.apply(**vars) for term in self.terms])

    def eval(self, **vars):
        my_vars = self.variables()
        if len(set(vars)) < len(my_vars):
            raise Exception("Not enough variables supplied. Maybe use apply?")

        for var, value in vars.items():
            if type(value) not in (int, float):
                raise ValueError(
                    f"The value {value} for var {var} is neither int nor float."
                )
            assert type(value) in (int, float)
        return sum(term.eval(**vars) for term in self.terms)

    def put_terms_in_order(self):
        sorted_vars = sorted(self.variables())
        self.terms.sort(key=lambda term: term.key(sorted_vars), reverse=True)

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

    def substitute(self):
        assert False  # TODO

    def variables(self):
        vars = set()
        for term in self.terms:
            vars |= term.variables()
        return vars

    @staticmethod
    def constant(c):
        return Poly([Term.constant(c)])

    @staticmethod
    def one():
        return Poly.constant(1)

    @staticmethod
    def sum(poly_list):
        """
        You can use ordinary Python sum() on a list of polynomials,
        but this should be faster, since it avoids creating a bunch
        of intermediate partial polynomial sums for large lists.
        """
        for poly in poly_list:
            assert type(poly) == Poly

        if len(poly_list) == 0:
            return Poly.zero()

        if len(poly_list) == 1:
            return poly_list[0]

        terms = sum((p.terms for p in poly_list), start=[])
        return Poly(terms)

    @staticmethod
    def var(label):
        return Poly([Term.var(label)])

    @staticmethod
    def zero():
        return Poly([])
