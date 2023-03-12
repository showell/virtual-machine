class Expr:
    def __init__(self, *, val, label):
        self.val = val
        self.label = label

def VAR(x, label):
    return Expr(val=x, label=label)

def ADD(x, y):
    return Expr(val=x.val + y.val, label=f"{x.label})+({y.label}")

def SUB(x, y):
    return Expr(val=x.val - y.val, label=f"{x.label}-({y.label})")

def MULT(x, y):
    return Expr(val=x.val * y.val, label=f"({x.label})*({y.label})")

def DECR(x):
    return Expr(val=x.val - 1, label=f"{x.label} - 1")

def NOT(x):
    return MULT(DECR(x), DECR(x))

def AND(x, y):
    return MULT(x, y)

def OR(x, y):
    return SUB(ADD(x,y), MULT(x,y))

def ORR(x, y, z):
    return OR(OR(x, y), z)

def evaluate(*, hb, lb, halted, accepted, op_hb, op_lb):
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
    becomes_1 = ORR(AND(is_1, stays_same), AND(is_2, runs_decr), AND(is_odd, runs_mod2))
    becomes_0 = ORR(AND(is_0, stays_same), AND(is_1, runs_decr), AND(is_even, runs_mod2))

    accepted = OR(accepted, AND(is_0, runs_check))

    halted = ORR(halted, accepted, AND(is_0, runs_decr))

    hb_set = OR(becomes_3, becomes_2)
    lb_set = OR(becomes_3, becomes_1)

    return (hb_set, lb_set, halted, accepted)

def step(*, AX, halted, accepted, op):
    assert AX in [0, 1, 2, 3]
    assert halted in [0, 1]
    assert op in [0, 1, 2, 3]

    hb = AX // 2
    lb = AX % 2

    op_hb = op // 2
    op_lb = op % 2

    hb = VAR(hb, "a")
    lb = VAR(lb, "b")
    halted = VAR(halted, "c")
    accepted = VAR(accepted, "d")
    op_hb = VAR(op_hb, "ophb1")
    op_lb = VAR(op_lb, "ophb2") 

    (hb_set, lb_set, halted, accepted) = evaluate(
        hb=hb,
        lb=lb,
        halted=halted,
        accepted=accepted,
        op_hb=op_hb,
        op_lb=op_lb,
    )
    # print(lb_set.label)

    AX = 2 * hb_set.val + lb_set.val
    return (AX, halted.val, accepted.val)
