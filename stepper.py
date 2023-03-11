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

def evaluate(*, hb, lb, halted, accepted, is_decr):
    is_3 = AND(hb, lb)
    is_2 = AND(hb, NOT(lb))
    is_1 = AND(NOT(hb), lb)
    is_0 = AND(NOT(hb), NOT(lb))

    is_check = NOT(is_decr)

    stays_same = OR(halted, is_check)
    runs_check = AND(is_check, NOT(halted))
    runs_decr = AND(is_decr, NOT(halted))
    
    becomes_3 = AND(is_3, stays_same)
    becomes_2 = OR(AND(is_2, stays_same), AND(is_3, runs_decr))
    becomes_1 = OR(AND(is_1, stays_same), AND(is_2, runs_decr))
    becomes_0 = OR(AND(is_0, stays_same), AND(is_1, runs_decr))

    accepted = OR(accepted, AND(is_0, runs_check))

    halted = ORR(halted, accepted, AND(is_0, runs_decr))

    hb_set = OR(becomes_3, becomes_2)
    lb_set = OR(becomes_3, becomes_1)

    return (hb_set, lb_set, halted, accepted)

def step(*, AX, halted, accepted, cmd):
    assert AX in [0, 1, 2, 3]
    assert halted in [0, 1]
    assert cmd in ["decr", "check"]
    is_decr = cmd == "decr"

    hb = AX // 2
    lb = AX % 2

    hb = VAR(hb, "a")
    lb = VAR(lb, "b")
    halted = VAR(halted, "c")
    accepted = VAR(accepted, "d")
    is_decr = VAR(is_decr, "e")

    (hb_set, lb_set, halted, accepted) = evaluate(
        hb=hb,
        lb=lb,
        halted=halted,
        accepted=accepted,
        is_decr=is_decr,
    )
    # print(lb_set.label)

    AX = 2 * hb_set.val + lb_set.val
    return (AX, halted.val, accepted.val)


print(step(AX=0, halted=False, accepted=False, cmd="check"))
