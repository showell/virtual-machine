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

def IF(b, x, y):
    return ADD(MULT(b, x), MULT(NOT(b), y))
assert IF(0, 0, 0) == 0
assert IF(0, 0, 1) == 1
assert IF(0, 1, 0) == 0
assert IF(0, 1, 1) == 1
assert IF(1, 0, 0) == 0
assert IF(1, 0, 1) == 0
assert IF(1, 1, 0) == 1
assert IF(1, 1, 1) == 1

def ORR(x, y, z):
    return OR(OR(x, y), z)

def IS_0(x):
    return int((x - 1) * (x-2) * (x-3) / -6)
assert IS_0(3) == 0
assert IS_0(2) == 0
assert IS_0(1) == 0
assert IS_0(0) == 1

def IS_1(x):
    return IF(IS_0(x), 0, IS_0(x-1))

assert IS_1(3) == 0
assert IS_1(2) == 0
assert IS_1(1) == 1
assert IS_1(0) == 0

def IS_SMALL(x):
    return OR(IS_0(x), IS_1(x))
assert IS_SMALL(3) == 0
assert IS_SMALL(2) == 0
assert IS_SMALL(1) == 1
assert IS_SMALL(0) == 1

def IS_2(x):
    return IF(IS_SMALL(x), 0, NOT(x - 2))
assert IS_2(3) == 0
assert IS_2(2) == 1
assert IS_2(1) == 0
assert IS_2(0) == 0

def IS_3(x):
    return IF(IS_SMALL(x), 0, x - 2)
assert IS_3(3) == 1
assert IS_3(2) == 0
assert IS_3(1) == 0
assert IS_3(0) == 0

def step(*, AX, halted, accepted, cmd):
    assert AX in [0, 1, 2, 3]
    assert halted in [0, 1]
    assert cmd in ["decr", "check"]
    is_decr = cmd == "decr"

    AX = VAR(AX, "x")
    halted = VAR(halted, "halted")
    accepted = VAR(accepted, "accepted")
    is_decr = VAR(is_decr, "is_decr")

    is_3 = IS_3(AX)
    is_2 = IS_2(AX)
    is_1 = IS_1(AX)
    is_0 = IS_0(AX)

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

    AX = 0 * becomes_0 + 1 * becomes_1 + 2 * becomes_2 + 3 * becomes_3    
    return (AX, halted, accepted)


print(step(AX=0, halted=False, accepted=False, cmd="check"))
