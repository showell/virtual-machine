"""
Operation of a finite virtual machine:
    
    single register called AX

    We only use two-bit numbers: {0, 1, 2, 3}.

    The machine executes a program.

    Every program is a sequence of these opcodes (aka instructions):

        00 (pass):
            (do nothing)

        01 (check):
            AX = 3 -> ignore and continue
            AX = 2 -> ignore and continue
            AX = 1 -> ignore and continue
            AX = 0 -> halt and accept input

        10 (decr):
            AX = 3 -> AX = 2 and continue
            AX = 2 -> AX = 1 and continue
            AX = 1 -> AX = 0 and continue
            AX = 0 -> halt and reject input

        11 (mod2):
            AX = 3 -> AX = 1
            AX = 2 -> AX = 0
            AX = 1 -> AX = 1
            AX = 0 -> AX = 0

    Every program must include exactly six instructions.  If at the end
    of that program you have not accepted the input, then the input is
    implicitly rejected.

    If a user wants to validate an input, they can put that number into
    AX and run their program. By definition every program "recognizes" some
    "language" that is a subset of {0, 1, 2, 3}.  That language corresponds
    to the exact set of numbers that would be accepted by the virtual
    machine when passed into the program.

    SOME LANGUAGES (phrased as questions):

        is_tiny [0]
        is_not_tiny [1, 2, 3]
        is_huge [3]
        is_not_huge [0, 1, 2]
        is_small [0, 1]
        is_big [2, 3]
        is_even [0, 2]
        is_odd [1, 3]
        is_middling [1, 2]
        is_extreme [0, 3]
        is_one [1]
        is_not_one [0, 2, 3]
        is_two [2]
        is_not_two [0, 1, 3]
        always_false []
        always_true [0, 1, 2, 3]
"""

import stepper

MAX_STEPS = 6


def run_progam(n, program):
    halted = False
    AX = n
    status = None

    assert len(program) == MAX_STEPS

    for op in program:
        if halted:
            continue
        if op == "pass":
            pass
        elif op == "check":
            if AX == 0:
                halted = True
                status = True
            else:
                pass
        elif op == "decr":
            if AX == 0:
                halted = True
                status = False
            else:
                AX -= 1
        elif op == "mod2":
            AX = AX % 2
        else:
            assert False

    return status


OPS = {"pass": 0, "check": 1, "decr": 2, "mod2": 3}


def test_with_stepper(program, ax):
    AX = ax
    halted = False
    accepted = False
    for cmd in program:
        (AX, halted, accepted) = stepper.step(
            AX=AX,
            halted=halted,
            accepted=accepted,
            op=OPS[cmd],
        )
    return accepted


def assemble(program):
    return sum(OPS[op] * (4**i) for i, op in enumerate(program))


def disassemble(n):
    ops = ["pass", "check", "decr", "mod2"]
    program = []
    for i in range(MAX_STEPS):
        program.append(ops[n % 4])
        n = n // 4
    return program


assert assemble(["check", "decr"]) == 9
assert disassemble(9) == ["check", "decr"] + ["pass"] * (MAX_STEPS - 2)


def encoded_language(lang):
    return sum(2**n for n in lang)


def language(code):
    lang = []
    i = 0
    while code:
        if code % 2 == 1:
            lang.append(i)
        code = code // 2
        i += 1
    return lang


assert encoded_language([]) == 0
assert language(0) == []
assert encoded_language([1, 3]) == 10
assert language(10) == [1, 3]


def f(program_number):
    lang = []
    program = disassemble(program_number)
    for i in range(4):
        if run_progam(i, program):
            lang.append(i)
    return encoded_language(lang)


def find_solutions():
    solutions = {}
    for y in range(16):
        solutions[y] = []
    for x in range(4**MAX_STEPS):
        solutions[f(x)].append(x)

    for y in range(16):
        assert len(solutions[y]) > 0

    for y in range(16):
        lang = language(y)
        x_list = solutions[y]
        programs = [disassemble(x) for x in x_list]
        print(f"f(x) = {y} for {len(x_list)} values of x")
        print(f" an example program to recognize {lang} is:")
        print("--")
        example_program = programs[0]
        for cmd in example_program:
            print(cmd)
        print("--")
        print()

        for i in range(4):
            accepted = test_with_stepper(example_program, i)
            assert accepted == (i in lang)


find_solutions()
