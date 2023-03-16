import collections
import integer

"""
The Poly class allows you to create polynomial expressions
where each term includes a coefficient (which is integer
by default) and then some subset of variables each raised
to an integer power.

The key feature of this class is that it allows you to
symbolically manipulate polynomials.

You can add/multiply instances of Poly with either (a) other
Poly objects or (b) constant values (again, integer by default).
You can also exponentiate Poly objects to create new Poly objects.
All Poly objects are immutable.

You can do things like composing polynomials from other polynomials,
and all these operations happen at the symbolic level until you
provide actual value assignments for the variables.

Very importantly, the Poly class assumes that its values form a
"commutative ring."  You don't need to understand that terminology
in a deep sense, as long as you are playing with integers.
Basically we assume that multiplication and addition conform
to our standard intuitive notions of how numbers work.

The Poly class supports an arbitrary combination of variables, and
for convenience sake, it prevents variables from having punctuation
characters that would conflict with operators like +, -, *, etc.

I believe this project could be pretty easily modified to work
with any commutative ring, but I have mostly tested with normal
integers and a Modulus class.

I try to set up the structure here to allow for future extensions.

ABOUT EXPONENTS (important):

    Note that even over a non-integer-based set of values, we would still
    have to enforce non-negative integer exponents to support
    the "substitution" operation on polynomials.  Think of exponentiation
    as just a shorthand for repeated multiplication, so for our purposes
    exponents will always be actual positive integers.  We also allow
    exponents of zero, but they essentially get simplified away in Poly.

Useful references:
    * https://docs.python.org/3/library/operator.html
    * https://en.wikipedia.org/wiki/Polynomial
    * https://en.wikipedia.org/wiki/Modular_arithmetic
    * https://en.wikipedia.org/wiki/Commutative_ring

"""

Value = integer.Integer


def set_value_handler(handler):
    """
    Allow us to build up polynomials with a Value type that isn't
    necessarily based on integers.  We rely on the caller to provide
    a handler that behaves like integers in terms of algebraic structure.
    See integer.py for the most obvious implementation of a handler.

    Multiplication and addition should both be commutative and associative.

    Addition should have a zero-like value such that a + Value.zero == a.

    Multiplication should have a one-like value such a * Value.one == a.

    Multiplication should also be distributive with respect to addition.
    """
    global Value
    Value = handler


def enforce_type(var, _type):
    if type(var) != _type:
        raise TypeError(f"{var} is not type {_type}")


def enforce_legal_variable_name(var_name):
    for c in ",*+/-()":
        if c in var_name:
            raise ValueError(f"Do not use variable names that include {c}.")


class _VarPower:
    """
    This helper class represents a simple power of a variable
    such as "(x**4)", with no coefficient.

    A variable is a simple Python string--there is no need
    to wrap it any sort of Symbol class.

    You never want to use this class directly; go through Poly
    instead.
    """

    def __init__(self, var_name, exponent):
        enforce_type(var_name, str)
        enforce_legal_variable_name(var_name)
        # We only handle positive powers of variables.
        # Constant values are handled by _Term.
        enforce_type(exponent, int)
        if exponent <= 0:
            raise ValueError("{exponent} is not positive")

        self.var = var_name
        self.exponent = exponent

    def __str__(self):
        if self.exponent == Value.one:
            return self.var
        return f"({self.var}**{self.exponent})"

    def compute_power(self, x):
        enforce_type(x, Value.value_type)
        return Value.power(x, self.exponent)


class _Term:
    """
    This helper class represents a single term of a polynomial,
    and it's really only intended as a helper for Poly, despite
    it having significant functionality.

    A term would be something like 2*(x**3)*(y**3), but you can
    also have constant terms.  For constants, see the methods
    _Term.constant, _Term.one, and _Term.zero.

    Our basic data structure simply stores a coefficient
    (abbreviated as "coeff") and a list of VarPowers.

    We also keep a dictionary keyed on var names for quick lookups,
    as well as a "sig" that represents the signature of our term.
    Two terms can only be combined if they have the same sig.
    """

    def __init__(self, coeff, var_powers):
        enforce_type(var_powers, list)
        for var_power in var_powers:
            enforce_type(var_power, _VarPower)
        enforce_type(coeff, Value.value_type)
        vars = [vp.var for vp in var_powers]
        assert vars == sorted(vars)
        assert len(vars) == len(set(vars))

        self.var_powers = var_powers
        self.coeff = coeff

        self.sig = "*".join(str(vp) for vp in var_powers)
        self.var_dict = {vp.var: vp.exponent for vp in var_powers}

    def __add__(self, other):
        return self.add_to_similar_term(other)

    def __mul__(self, other):
        """
        IMPORTANT: We assume commutative multiplication.
        """
        return self.multiply_with(other)

    def __neg__(self):
        return _Term(Value.negate(self.coeff), self.var_powers)

    def __pow__(self, exponent):
        return self.raised_to_exponent(exponent)

    def __rmul__(self, other):
        """
        if term == x**2, it is more natural for people to
        write something like 5*(x**2) than (x**2)*5, so we
        support the __rmul__ protocol.
        """
        return self.multiply_with(other)

    def __str__(self):
        """
        An example string is "60*x*(y**22)".
        """
        c = self.coeff
        c_str = str(c) if c > 0 else f"({c})"
        if not self.var_powers:
            return c_str
        if self.coeff == Value.one:
            return self.sig
        return c_str + "*" + self.sig

    def __sub__(self, other):
        """
        You should never try to substract terms.  Let the Poly
        class handle substraction.
        """
        raise NotImplementedError

    def add_to_similar_term(self, other):
        """
        We rely heavily on the Poly class to only invoke term
        addition when the terms have the same signature.
        """
        enforce_type(other, _Term)
        if self.sig != other.sig:
            raise AssertionError("Do not combine unlike terms!!!!")
        assert len(self.var_powers) == len(other.var_powers)
        return _Term(Value.add(self.coeff, other.coeff), self.var_powers)

    def apply(self, **var_assignments):
        """
        This substitutes variables in our term with actual
        integers, producing a simpler Term.

        If we get passed in vars that we don't know about,
        just ignore them.

        If none of the vars are in our term, then we just
        return ourself.  See Poly.apply for more context.
        """
        for var, value in var_assignments.items():
            enforce_type(var, str)
            enforce_type(value, Value.value_type)

        if not set(var_assignments) & set(self.var_dict):
            return self

        new_coeff = self.coeff
        new_vps = []
        for vp in self.var_powers:
            if vp.var in var_assignments:
                value = var_assignments[vp.var]
                new_coeff = Value.mul(new_coeff, vp.compute_power(value))
            else:
                new_vps.append(vp)
        return _Term(new_coeff, new_vps)

    def eval(self, **var_assignments):
        """
        This function returns the actual numerical value of
        our term given values for all its variables.

        If we get passed in vars that we don't know about,
        just ignore them. (That relieves Poly from having
        to check each of its terms to see which variables
        are used.)
        """
        for var, value in var_assignments.items():
            enforce_type(var, str)
            enforce_type(value, Value.value_type)

        for var in self.variables():
            if var not in var_assignments:
                raise ValueError(f"You are not providing an assignment for {var}.")

        product = Value.one
        for vp in self.var_powers:
            product = Value.mul(product, vp.compute_power(var_assignments[vp.var]))
        return Value.mul(self.coeff, product)

    def factorize_on_var(self, substituted_var):
        """
        This method is used by Poly when you are trying to substitute
        a variable with some polynomial expression.  The _Term object here
        basically splits out the non-substituted portion of the term,
        and reports the power of the substituted variable.
        """
        if substituted_var not in self.var_dict:
            return (self, Value.zero)

        var_powers = [vp for vp in self.var_powers if vp.var != substituted_var]
        power_of_substituted_var = self.var_dict[substituted_var]
        return (_Term(self.coeff, var_powers), power_of_substituted_var)

    def is_one(self):
        return self.coeff == Value.one and len(self.var_powers) == 0

    def multiply_with(self, other):
        """
        suppose term1 = 2*(x**10)
            and term2 = 5*x * 7*z
        then
            term1 * 3 == 6*(x**10)
            term1 * term2 == term2 * term1 == 70*(x**11)*z
        """
        if type(other) == Value.value_type:
            return self.multiply_by_constant(other)
        elif type(other) == _Term:
            return self.multiply_terms(other)

        raise TypeError("We don't support this type of multiplication.")

    def multiply_by_constant(self, c):
        enforce_type(c, Value.value_type)
        if c == Value.zero:
            return _Term.zero()
        if c == Value.one:
            return self
        return _Term(Value.mul(c, self.coeff), self.var_powers)

    def multiply_terms(self, other):
        """
        It is always possible to multiply two terms together, whether
        they have the same exact variables, disjoint variables, or some
        common subset of overlapping variables.

        The coefficient is trivial--just multiply the two coefficients.

        For the VarPower pieces, we use a dict to collect common
        variables.
        """
        if other.coeff == 0:
            return _Term.zero()
        elif other.is_one():
            return self

        coeff = Value.mul(self.coeff, other.coeff)
        exponents = collections.defaultdict(int)
        for vp in self.var_powers:
            exponents[vp.var] = vp.exponent
        for vp in other.var_powers:
            exponents[vp.var] += vp.exponent
        parms = list(exponents.items())
        parms.sort()
        vps = [_VarPower(var, exponent) for var, exponent in parms]
        return _Term(coeff, vps)

    def raised_to_exponent(self, exponent):
        """
        To exponentiate a term, we exponentiate our coefficient and
        all our VarPower sub-terms.

        In our world exponentiation is truly just a shorthand for
        repeated multiplication, so we expect non-negative exponents,
        and we expect our Value class to respect those semantics.
        """
        enforce_type(exponent, int)
        if exponent < 0:
            raise ValueError("We do not support negative exponentiation yet.")

        if exponent == 0:
            return _Term.one()

        if exponent == 1:
            return self

        coeff = Value.power(self.coeff, exponent)
        vps = [_VarPower(vp.var, vp.exponent * exponent) for vp in self.var_powers]
        return _Term(coeff, vps)

    def sort_key(self, var_list):
        """
        This is used by Poly to sort terms in the normal high
        school algebra format.
        """
        return tuple(self.var_dict.get(var, Value.zero) for var in var_list)

    def transform_coefficient(self, f):
        assert callable(f)
        return _Term(f(self.coeff), self.var_powers)

    def variables(self):
        """
        If self represents something like 5*a*b*c, this method
        returns {"a", "b", "c"}.  This helps Poly determine the
        set of variables across all terms.
        """
        return set(self.var_dict.keys())

    @staticmethod
    def constant(c):
        enforce_type(c, Value.value_type)
        return _Term(c, [])

    @staticmethod
    def one():
        return _Term(Value.one, [])

    @staticmethod
    def sum(terms):
        """
        This is a helper for Poly.
        Poly will only call us with terms that have the same sig.

        We essentially just adds up coefficients.

        We also special-case the situation where there is only
        one term in the sum, since there is no need to create
        new objects in that case, as _Term objects are immutable.
        """
        if len(terms) < 1:
            raise ValueError("We expect at least one term to be summed.")

        if len(terms) == 1:
            return terms[0]

        term = terms[0]
        sig = term.sig
        coeff = term.coeff
        for other in terms[1:]:
            enforce_type(other, _Term)
            if other.sig != sig:
                raise AssertionError("We cannot combine unlike terms!!!")
            coeff = Value.add(coeff, other.coeff)

        return _Term(coeff, term.var_powers)

    @staticmethod
    def var(var):
        enforce_type(var, str)
        return _Term(Value.one, [_VarPower(var, Value.one)])

    @staticmethod
    def zero():
        return _Term(Value.zero, [])


class Poly:
    def __init__(self, terms):
        if type(terms) == _Term:
            raise ValueError(
                "Pass in a list of _Terms or use Poly's other constructors."
            )
        enforce_type(terms, list)
        for term in terms:
            enforce_type(term, _Term)
        self.terms = terms

        """
        Note the invariant here. As SOON as a Poly gets constructed, it
        immediately gets simplified, and its terms are put in a canonical
        order. And the Poly object never gets mutated.

        Because we eagerly do simplification and canonicalization, it is
        somewhat expensive to construct a Poly object, but then all
        subsequent calls to eval() are quicker.  If possible, callers
        should try to reuse existing Poly objects.  For example, if you
        multiple a Poly by one, don't unnecessarily create a new Poly.
        """
        self.simplify()
        self.put_terms_in_order()

    def __add__(self, other):
        """
        We assume commutative addition.
        """
        return self.add_with(other)

    def __eq__(self, other):
        """
        Two Poly objects are considered equal if they have the
        same canonical representation after simplification.

        Any two Poly objects that are equal under this definition
        should also return the exact same values when you call
        their eval methods for any particular combination of
        variable assignments (using integers).

        I believe the converse is true over the integers.  In other
        words if two Poly objects are reported NOT to be equal
        by this method, that should imply that there exists at
        least one possible assignment of integer values to the
        variables that will produce different eval() results from
        the two "non-equal" polynomials.

        Note that we only consider two polynomials to be equivalent
        if they use the same set of variable names.  While
        x+3 and y+3 are structurally equivalent, we consider them
        to be non-equal.
        """
        enforce_type(other, Poly)
        return self.canonicalized_string() == other.canonicalized_string()

    def __mul__(self, other):
        return self.multiply_with(other)

    def __neg__(self):
        return Poly([-term for term in self.terms])

    def __pow__(self, exponent):
        return self.raised_to_exponent(exponent)

    def __radd__(self, other):
        """
        We assume commutative addition.
        """
        return self.add_with(other)

    def __rmul__(self, other):
        return self.multiply_with(other)

    def __rsub__(self, other):
        if type(other) == Value.value_type:
            other = Poly.constant(other)
        enforce_type(other, Poly)
        return -self + other

    def __str__(self):
        """
        We try to make sure our canonical string representation is
        consistent across equivalent polynomials, and hopefully this
        is what the human wants too.
        """

        return self.canonicalized_string()

    def __sub__(self, other):
        if type(other) == Value.value_type:
            return self + Poly.constant(Value.negate(other))
        return self + (-other)

    def add_with(self, other):
        """
        We add either a Value-based constant (e.g. an integer)
        or another Poly to ourself and return a new Poly (unless
        we are adding Value.zero).
        """
        if type(other) == Value.value_type:
            if other == Value.zero:
                # take advantage of immutability
                return self
            """
            For convenience, just immediately make a Poly
            from the value and continue with Poly+Poly addition.
            """
            other = Poly.constant(other)

        enforce_type(other, Poly)

        """
        All the heavy lifting happens when we construct the
        new Poly--see __init__ for more context.
        """
        return Poly(self.terms + other.terms)

    def apply(self, **var_assignments):
        """
        This does a partial application of a subset of variables to
        our polynomial. I perhaps could have called this "partial",
        but I wanted to avoid confusion with possible future extensions
        related to partial derivates.
        """
        my_vars = self.variables()
        for var, value in var_assignments.items():
            if type(value) is Poly:
                raise ValueError("Use Poly.substitute instead")
            enforce_type(value, Value.value_type)
            if var not in my_vars:
                raise ValueError(f"{var} is not a variable for {self}")
        return Poly([term.apply(**var_assignments) for term in self.terms])

    def canonicalized_string(self):
        """
        This method is easy, because we do the heavy lifting of calling
        put_terms_in_order when we make a Poly object.
        """
        if len(self.terms) == 0:
            return str(Value.zero)
        return "+".join(str(term) for term in self.terms)

    def eval(self, **var_assignments):
        """
        This method converts a Poly to a Value (e.g. integer) by
        using the supplied variable assignments.
        """
        my_vars = self.variables()
        if len(set(var_assignments)) < len(my_vars):
            raise ValueError("Not enough variables supplied. Maybe use apply?")

        for var, value in var_assignments.items():
            enforce_type(value, Value.value_type)

        result = Value.zero
        for term in self.terms:
            result = Value.add(result, term.eval(**var_assignments))
        return result

    def multiply_with(self, other):
        """
        We mostly rely on Poly.__init__ to do the heavy lifting here.
        """
        if type(other) == int:
            return Poly([term * other for term in self.terms])
        elif type(other) == _Term:
            raise ValueError("Use Poly contructors to build up terms.")
        enforce_type(other, Poly)
        terms = [t1 * t2 for t1 in self.terms for t2 in other.terms]
        return Poly(terms)

    def put_terms_in_order(self):
        if len(self.terms) <= 1:
            return
        sorted_vars = sorted(self.variables())
        self.terms.sort(key=lambda term: term.sort_key(sorted_vars), reverse=True)

    def raised_to_exponent(self, exponent):
        """
        Our definition of p***4 is literally p*p*p*p.

        We only support the high-school-math notion of exponentation;
        p**4 is just a shorthand for a discrete number of multiplications.
        """
        enforce_type(exponent, int)
        if exponent < 0:
            raise ValueError("we do not support negative exponents")

        if exponent == 0:
            return Poly.one()
        if exponent == 1:
            return self
        return self * self.raised_to_exponent(exponent - 1)

    def simplify(self):
        """
        In high school algebra, you remember

            (x + 3) * (x + 4) = x*2 + 3x + 4x + 12

        And then you combine the two middle terms to 7x.

        That is what we do here in the more general sense.
        """
        terms = self.terms
        if len(terms) == 0:
            return
        if len(terms) == 1:
            if terms[0].coeff == Value.zero:
                self.terms = []
            return

        """
        Put all the "like" terms in the same bucket, then add them.

        And then throw away any zero terms.
        """
        buckets = collections.defaultdict(list)
        for term in terms:
            sig = term.sig
            buckets[sig].append(term)

        new_terms = []
        for sub_terms in buckets.values():
            term = _Term.sum(sub_terms)
            if term.coeff != Value.zero:
                new_terms.append(term)

        self.terms = new_terms

    def substitute(self, var, poly):
        enforce_type(var, str)
        enforce_type(poly, Poly)
        if var not in self.variables():
            raise ValueError("Unknown variable")

        new_polys = []
        for term in self.terms:
            smaller_term, power = term.factorize_on_var(var)
            if power == Value.zero:
                new_poly = Poly([smaller_term])
            else:
                new_poly = Poly([smaller_term]) * (poly**power)
            new_polys.append(new_poly)
        return Poly.sum(new_polys)

    def transform_coefficients(self, f):
        assert callable(f)
        terms = [t.transform_coefficient(f) for t in self.terms]
        return Poly(terms)

    def variables(self):
        vars = set()
        for term in self.terms:
            vars |= term.variables()
        return vars

    @staticmethod
    def constant(c):
        enforce_type(c, Value.value_type)
        return Poly([_Term.constant(c)])

    @staticmethod
    def one():
        return Poly.constant(Value.one)

    @staticmethod
    def sum(poly_list):
        """
        You can use ordinary Python sum() on a list of polynomials,
        but this should be faster, since it avoids creating a bunch
        of intermediate partial polynomial sums for large lists.
        """
        enforce_type(poly_list, list)
        for poly in poly_list:
            enforce_type(poly, Poly)

        if len(poly_list) == 0:
            return Poly.zero()

        if len(poly_list) == 1:
            return poly_list[0]

        terms = []
        for p in poly_list:
            terms.extend(p.terms)
        return Poly(terms)

    @staticmethod
    def var(label):
        """
        Create a single-term polynomial with coefficient 1 and
        degree 1.

        Note that label is just the name of a variable like "x".
        (It might feel strange to folks that we don't have any
        objects corresponding directly to a variable--instead,
        variables are just implicitly used inside of _VarPower,
        _Term, and Poly.
        """
        enforce_type(label, str)
        coeff = Value.one
        exponent = 1  # exponents are ALWAYS integers
        var_power = _VarPower(label, exponent)
        term = _Term(coeff, [var_power])
        return Poly([term])

    @staticmethod
    def zero():
        return Poly([])
