"""
Operation of a finite virtual machine:

    single register called AX

    We only use two-bit numbers: {0, 1, 2, 3}.

    The machine executes a program.

    Every program is a sequence of these opcodes (aka instructions):

        00 (nada):
            (do nothing)

        01 (zero):
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
OPS = dict(
    nada=0,
    zero=1,
    decr=2,
    mod2=3
)

COMMENT = dict(
    nada="# do nothing",
    decr="# reject zero or decrement AX",
    mod2="# subtract 2 from AX if AX >= 2",
    zero="# accept original input if AX = 0",
)


def run_progam(n, program):
    halted = False
    AX = n
    status = None

    assert len(program) == MAX_STEPS

    for op in program:
        if halted:
            continue
        if op == "nada":
            pass
        elif op == "zero":
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


def assemble(program):
    return sum(OPS[op] * (4**i) for i, op in enumerate(program))


def disassemble(n):
    ops = ["nada", "zero", "decr", "mod2"]
    program = []
    for i in range(MAX_STEPS):
        program.append(ops[n % 4])
        n = n // 4
    return program


assert assemble(["zero", "decr"]) == 9
assert disassemble(9) == ["zero", "decr"] + ["nada"] * (MAX_STEPS - 2)


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


def get_language_that_program_accepts(program):
    lang = []
    for i in range(4):
        if run_progam(i, program):
            lang.append(i)
    return lang

def complement(lang):
    return [i for i in range(4) if i not in lang]

def find_solutions():
    solutions = {}

    for y in range(16):
        solutions[y] = []

    for program_number in range(4**MAX_STEPS):
        program = disassemble(program_number)
        lang = get_language_that_program_accepts(program)
        solutions[encoded_language(lang)].append(program_number)

    for y in range(16):
        assert len(solutions[y]) > 0

    for y in range(16):
        lang = language(y)
        rejected_lang = complement(lang)
        x_list = solutions[y]
        programs = [disassemble(x) for x in x_list]
        print(f"{lang} is solved by {len(x_list)} possible program")
        print(f"See an example program below.")
        print(f"   it accepts {lang}")
        print(f"   it rejects {rejected_lang}")
        print("--")
        example_program = programs[0]
        for cmd in example_program:
            print(cmd, COMMENT[cmd])
        print("--")
        print()

        for i in range(4):
            accepted = stepper.test_with_stepper(example_program, i)
            assert accepted == (i in lang)


find_solutions()
