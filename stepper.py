from poly import Poly


def VAR(label):
    return Poly.var(label)


def NOT(x):
    return 1 - x


def AND(x, y):
    return x * y


def OR(x, y):
    return (x + y) - (x * y)


def OR3(x, y, z):
    return OR(OR(x, y), z)


def construct_polynomials(*, hb, lb, halted, accepted, op_hb, op_lb):
    is_3 = AND(hb, lb)
    is_2 = AND(hb, NOT(lb))
    is_1 = AND(NOT(hb), lb)
    is_0 = AND(NOT(hb), NOT(lb))

    is_check = AND(NOT(op_hb), op_lb)
    is_decr = AND(op_hb, NOT(op_lb))
    is_mod2 = AND(op_hb, op_lb)

    stays_same = OR(halted, is_check)
    runs_check = AND(is_check, NOT(halted))
    runs_decr = AND(is_decr, NOT(halted))
    runs_mod2 = AND(is_mod2, NOT(halted))

    is_even = OR(is_0, is_2)
    is_odd = OR(is_1, is_3)

    becomes_3 = AND(is_3, stays_same)
    becomes_2 = OR(AND(is_2, stays_same), AND(is_3, runs_decr))
    becomes_1 = OR3(AND(is_1, stays_same), AND(is_2, runs_decr), AND(is_odd, runs_mod2))
    becomes_0 = OR3(
        AND(is_0, stays_same), AND(is_1, runs_decr), AND(is_even, runs_mod2)
    )

    accepted = OR(accepted, AND(is_0, runs_check))

    halted = OR3(halted, accepted, AND(is_0, runs_decr))

    hb_set = OR(becomes_3, becomes_2)
    lb_set = OR(becomes_3, becomes_1)

    return (hb_set, lb_set, halted, accepted)


STEP_POLYNOMIALS = construct_polynomials(
    hb=VAR("hb"),
    lb=VAR("lb"),
    halted=VAR("halted"),
    accepted=VAR("accepted"),
    op_hb=VAR("op_hb"),
    op_lb=VAR("op_lb"),
)


def step(*, AX, halted, accepted, op):
    assert AX in [0, 1, 2, 3]
    assert halted in [0, 1]
    assert accepted in [0, 1]
    assert op in [0, 1, 2, 3]

    hb = AX // 2
    lb = AX % 2

    op_hb = op // 2
    op_lb = op % 2

    halted = int(halted)
    accepted = int(accepted)

    (hb_set, lb_set, new_halted, new_accepted) = STEP_POLYNOMIALS

    hb_set = hb_set.eval(
        hb=hb,
        lb=lb,
        halted=halted,
        accepted=accepted,
        op_hb=op_hb,
        op_lb=op_lb,
    )
    lb_set = lb_set.eval(
        hb=hb,
        lb=lb,
        halted=halted,
        accepted=accepted,
        op_hb=op_hb,
        op_lb=op_lb,
    )
    new_halted = new_halted.eval(
        hb=hb,
        lb=lb,
        halted=halted,
        accepted=accepted,
        op_hb=op_hb,
        op_lb=op_lb,
    )
    new_accepted = new_accepted.eval(
        hb=hb,
        lb=lb,
        halted=halted,
        accepted=accepted,
        op_hb=op_hb,
        op_lb=op_lb,
    )

    AX = 2 * hb_set + lb_set
    return (AX, new_halted, new_accepted)
