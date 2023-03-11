def ADD(x, y):
    return x + y

def SUB(x, y):
    return x - y

def MULT(x, y):
    return x * y

def DECR(x):
    return x - 1

def VAR(x, label):
    return x

def NOT(x):
    return MULT(DECR(x), DECR(x))
assert NOT(0) == 1
assert NOT(1) == 0

def AND(x, y):
    return MULT(x, y)
assert AND(0, 0) == 0
assert AND(0, 1) == 0
assert AND(1, 0) == 0
assert AND(1, 1) == 1 

def OR(x, y):
    return SUB(ADD(x,y), MULT(x,y))
assert OR(0, 0) == 0
assert OR(0, 1) == 1
assert OR(1, 0) == 1
assert OR(1, 1) == 1

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

    hb = VAR(hb, "hb")
    lb = VAR(lb, "lb")
    halted = VAR(halted, "halted")
    accepted = VAR(accepted, "accepted")
    is_decr = VAR(is_decr, "is_decr")

    (hb_set, lb_set, halted, accepted) = evaluate(
        hb=hb,
        lb=lb,
        halted=halted,
        accepted=accepted,
        is_decr=is_decr,
    )

    AX = 2 * hb_set + lb_set
    return (AX, halted, accepted)


print(step(AX=0, halted=False, accepted=False, cmd="check"))
