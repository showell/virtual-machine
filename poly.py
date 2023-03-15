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


class _VarPower:
    """
    This helper class represents a simple power of a variable
    such as "(x**4)", with no coefficient.

    A variable is a simple Python string--there is no need
    to wrap it any sort of Symbol class.

    You never want to use this class directly; go through Poly
    instead.
    """

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
        return _VarPower(self.var, self.power * exponent)

    def __str__(self):
        if self.power == 1:
            return self.var
        return f"({self.var}**{self.power})"

    def eval(self, x):
        return x**self.power


class _Term:
    """
    This helper class represents a single term of a polynomial,
    and it's really only intended as a helper for Poly, despite
    it having significant functionality.

    A term would be something like 2*(x**3)*(y**3), but you can
    also have constant terms.  For constants, see the methods
    for "zero", "one", and "constant".

    Our basic data structure simply stores an integer coefficient
    (abbreviated as "coeff") and a list of VarPowers.

    We also keep a dictionary keyed on var names for quick lookups,
    as well as a "sig" that represents the signature of our term.
    Two terms can only be combined if they have the same sig.
    """

    def __init__(self, coeff, var_powers):
        assert type(var_powers) == list
        for var_power in var_powers:
            assert (type(var_power)) == _VarPower
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
        """
        We rely heavily on the Poly class to only invoke term
        addtion when the terms have the same signature.
        """
        assert type(other) == _Term
        assert len(self.var_powers) == len(other.var_powers)
        assert self.sig == other.sig
        return _Term(self.coeff + other.coeff, self.var_powers)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __neg__(self):
        return _Term(-1 * self.coeff, self.var_powers)

    def __pow__(self, exponent):
        assert type(exponent) == int
        assert exponent >= 0
        if exponent == 0:
            return _Term.one()

        if exponent == 1:
            return self

        coeff = self.coeff**exponent
        vps = [vp**exponent for vp in self.var_powers]
        return _Term(coeff, vps)

    def __rmul__(self, other):
        """
        if term == x**2, it is more natural for people to
        write something like 5*(x**2) than (x**2)*5, so we
        support the __rmul__ protocol.
        """
        if type(other) == int:
            if other == 0:
                return _Term.zero()
            if other == 1:
                assert self
            return _Term(self.coeff * other, self.var_powers)
        elif type(other) == _Term:
            return self.multiply_terms(other)
        else:
            assert False

    def __str__(self):
        """
        An example string is "60*x*(y**22)".
        """
        c = self.coeff
        c_str = str(c) if c > 0 else f"({c})"
        if not self.var_powers:
            return c_str
        if self.coeff == 1:
            return self.sig
        return c_str + "*" + self.sig

    def __sub__(self, other):
        """
        You should never try to substract terms.  Let the Poly
        class handle substraction.
        """
        raise NotImplementedError

    def apply(self, **vars):
        """
        This substitutes variables in our term with actual
        integers, producing a simpler Term.

        If we get passed in vars that we don't know about,
        just ignore them.

        If none of the vars are in our term, then we just
        return ourself.  See Poly.apply for more context.
        """
        for var, value in vars.items():
            assert type(var) == str
            assert type(value) == int
        if not set(vars) & set(self.var_dict):
            return self
        new_coeff = self.coeff
        new_vps = []
        for vp in self.var_powers:
            if vp.var in vars:
                value = vars[vp.var]
                new_coeff *= vp.eval(value)
            else:
                new_vps.append(vp)
        return _Term(new_coeff, new_vps)

    def eval(self, **vars):
        """
        This function returns the actual numerical value of
        our term given values for all its variables.

        If we get passed in vars that we don't know about,
        just ignore them. (That relieves Poly from having
        to check each of its terms to see which variables
        are used.)
        """
        for var, value in vars.items():
            assert type(var) == str
            assert type(value) in [int, float]
        assert self.variables().issubset(vars)
        product = self.coeff
        for vp in self.var_powers:
            product *= vp.eval(vars[vp.var])
        return product

    def factorize_on_var(self, substituted_var):
        """
        This method is used by Poly when you are trying to substitute
        a variable with some polynomial expression.  The _Term here
        basically splits out the non-substituted portion of the term,
        and reports the power of the substituted variable.
        """
        if substituted_var not in self.var_dict:
            return (self, 0)

        var_powers = [vp for vp in self.var_powers if vp.var != substituted_var]
        power_of_substituted_var = self.var_dict[substituted_var]
        return (_Term(self.coeff, var_powers), power_of_substituted_var)

    def is_one(self):
        return self.coeff == 1 and len(self.var_powers) == 0

    def multiply_terms(self, other):
        """
        It is always possible to multiply two terms together, whether
        they have the same exact variables, disjoint variables, or some
        common subset of overlapping variables.

        The coefficient is trivial--just multiply the two coefficients.

        For the VarPower pieces, we use a defaultdict to collect common
        variables.
        """
        if other.coeff == 0:
            return _Term.zero()
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
        vps = [_VarPower(var, power) for var, power in parms]
        return _Term(coeff, vps)

    def variables(self):
        """
        If self represents something like 5*a*b*c, this method
        returns {"a", "b", "c"}.  This helps Poly determine the
        set of variables across all terms.
        """
        return set(self.var_dict.keys())

    @staticmethod
    def constant(c):
        return _Term(c, [])

    @staticmethod
    def one():
        return _Term(1, [])

    @staticmethod
    def sum(terms):
        """
        This is a helper for Poly.
        It will only call us with terms that have the same sig.

        It essentially just adds up coefficients.

        We also special-case the situation where there is only
        one term in the sum, since there is no need to create
        new objects in that case, as _Term objects are immutable.
        """
        assert len(terms) >= 1
        if len(terms) == 1:
            return terms[0]

        term = terms[0]
        sig = term.sig
        coeff = term.coeff
        var_powers = term.var_powers
        for other in terms[1:]:
            assert type(other) == _Term
            assert other.sig == sig
            coeff += other.coeff

        return _Term(coeff, var_powers)

    def sort_key(self, var_list):
        """
        This is used by Poly to sort terms in the normal high
        school algebra format.
        """
        return tuple(self.var_dict.get(var, 0) for var in var_list)

    @staticmethod
    def var(var):
        assert type(var) == str
        return _Term(1, [_VarPower(var, 1)])

    @staticmethod
    def zero():
        return _Term(0, [])


class Poly:
    def __init__(self, terms):
        if type(terms) == _Term:
            raise ValueError(
                "Pass in a list of _Terms or use Poly's other constructors."
            )
        assert type(terms) == list
        for term in terms:
            assert type(term) == _Term
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
        assert type(exponent) == int
        assert exponent >= 0
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
        elif type(other) == _Term:
            raise ValueError("Use Poly contructors to build up terms.")
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
            raise ValueError("Not enough variables supplied. Maybe use apply?")

        for var, value in vars.items():
            if type(value) not in (int, float):
                raise ValueError(
                    f"The value {value} for var {var} is neither int nor float."
                )
            assert type(value) in (int, float)
        return sum(term.eval(**vars) for term in self.terms)

    def put_terms_in_order(self):
        if len(self.terms) <= 1:
            return
        sorted_vars = sorted(self.variables())
        self.terms.sort(key=lambda term: term.sort_key(sorted_vars), reverse=True)

    def simplify(self):
        terms = self.terms
        if len(terms) == 0:
            return
        if len(terms) == 1:
            if terms[0].coeff == 0:
                self.terms = []
            return
        buckets = collections.defaultdict(list)
        for term in terms:
            sig = term.sig
            buckets[sig].append(term)

        new_terms = []
        for sub_terms in buckets.values():
            term = _Term.sum(sub_terms)
            if term.coeff != 0:
                new_terms.append(term)

        self.terms = new_terms

    def substitute(self, var, poly):
        assert type(var) == str
        assert type(poly) == Poly
        assert var in self.variables()
        new_polys = []
        for term in self.terms:
            smaller_term, power = term.factorize_on_var(var)
            if power == 0:
                new_poly = Poly([smaller_term])
            else:
                new_poly = Poly([smaller_term]) * (poly**power)
            new_polys.append(new_poly)
        return Poly.sum(new_polys)

    def variables(self):
        vars = set()
        for term in self.terms:
            vars |= term.variables()
        return vars

    @staticmethod
    def constant(c):
        return Poly([_Term.constant(c)])

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
        return Poly([_Term.var(label)])

    @staticmethod
    def zero():
        return Poly([])
