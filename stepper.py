from poly import Poly


def VAR(label):
    return Poly.var(label)


def NOT(x):
    return 1 - x


def AND(x, y):
    return x * y


def OR(x, y):
    return (x + y) - (x * y)


def OR4(w, x, y, z):
    return OR(OR(w, x), OR(y, z))


FALSE = Poly.constant(0)


def construct_polynomials(*, hb, lb, halted, accepted, op_hb, op_lb):
    is_3 = AND(hb, lb)
    is_2 = AND(hb, NOT(lb))
    is_1 = AND(NOT(hb), lb)
    is_0 = AND(NOT(hb), NOT(lb))

    is_pass = AND(NOT(op_hb), NOT(op_lb))
    is_check = AND(NOT(op_hb), op_lb)
    is_decr = AND(op_hb, NOT(op_lb))
    is_mod2 = AND(op_hb, op_lb)

    runs_pass = OR(is_pass, halted)
    runs_check = AND(is_check, NOT(halted))
    runs_decr = AND(is_decr, NOT(halted))
    runs_mod2 = AND(is_mod2, NOT(halted))

    pass1 = AND(is_1, runs_pass)
    pass2 = AND(is_2, runs_pass)
    pass3 = AND(is_3, runs_pass)
    pass_accepts = FALSE
    pass_halts = FALSE

    check1 = AND(is_1, runs_check)
    check2 = AND(is_2, runs_check)
    check3 = AND(is_3, runs_check)
    check_accepts = AND(is_0, runs_check)
    check_halts = FALSE

    decr1 = AND(is_2, runs_decr)
    decr2 = AND(is_3, runs_decr)
    decr3 = FALSE
    decr_accepts = FALSE
    decr_halts = AND(is_0, runs_decr)

    mod1 = AND(OR(is_3, is_1), runs_mod2)
    mod2 = FALSE
    mod3 = FALSE
    mod_accepts = FALSE
    mod_halts = FALSE

    newly_accepted = OR4(pass_accepts, check_accepts, decr_accepts, mod_accepts)
    accepted = OR(accepted, newly_accepted)

    newly_halted = OR4(pass_halts, check_halts, decr_halts, mod_halts)
    halted = OR(halted, newly_halted)

    becomes_1 = OR4(pass1, check1, decr1, mod1)
    becomes_2 = OR4(pass2, check2, decr2, mod2)
    becomes_3 = OR4(pass3, check3, decr3, mod3)

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
