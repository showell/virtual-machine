"""
Operation of a finite virtual machine:
    
    single register called AX

    We only use two-bit numbers: {0, 1, 2, 3}.

    The machine executes a program.

    Every program is a sequence of these opcodes (aka instructions):

        0 (check):
            AX = 3 -> ignore and continue
            AX = 2 -> ignore and continue
            AX = 1 -> ignore and continue
            AX = 0 -> halt and accept input

        1 (decr):
            AX = 3 -> AX = 2 and continue
            AX = 2 -> AX = 1 and continue
            AX = 1 -> AX = 0 and continue
            AX = 0 -> halt and reject input

    If the virtual machine runs out of instructions to execute when
    running a program, then it will also reject the input.

    Also, any program longer than 8 instructions is considered invalid
    and the virtual machine rejects all inputs.

    If a user wants to validate an input, they can put that number into
    AX and run their program. By definition every program "recognizes" some
    "language" that is a subset of {0, 1, 2, 3}.  That language corresponds
    to the exact set of numbers that would be accepted by the virtual
    machine when passed into the program.
"""
 
EVEN_NUMBERS = [
    #            AX=0 AX=1 AX=2 AX=3
    "check",   # acc  -    -    -
    "decr",    #      AX=0 AX=1 AX=2
    "decr",    #      rej  AX=0 AX=1
    "check",   #           acc  -
               #                rej
               #  0         2
]

ODD_NUMBERS = [
    #            AX=0 AX=1 AX=2 AX=3
    "decr",    # rej  AX=0 AX=1 AX=2
    "check",   #      acc  -    -
    "decr",    #           AX=0 AX=1
    "decr",    #           rej  AX=0
    "check",   #                acc
               #      1         3
]

BIG_NUMBERS = [
    "decr",
    "decr",
    "check",
    "decr",
    "check",
]

SMALL_NUMBERS = [
    "check",
    "decr",
    "check",
]

JUST_TWO = [
    "decr",
    "decr",
    "check",
]

# This is only the most obvious solution.
EMPTY_SET = [
    # no instructions, just fail
]

def run_progam(n, program):
    halted = False
    AX = n
    status = None

    if len(program) > 8:
        return False
    
    for op in program:
        if halted:
            continue
        if op == "decr":
            if AX == 0:
               halted = True
               status = False
            else:
                AX -= 1
        elif op == "check":
            if AX == 0:
                halted = True
                status = True
            else:
                pass
        else:
            assert False

    return status
                
def assemble(program):
    ops = {"check": 1, "decr": 2}
    n = 0
    for i, op in enumerate(program):
        n *= 2
        n += ops[op]
    return n

def disassemble(n):
    if n == 0:
        return []
    elif n % 2 == 0:
        return disassemble((n - 2) // 2) + ["decr"]
    else:
        return disassemble((n - 1) // 2) + ["check"]
        
assert assemble(["check", "decr"]) == 4
assert disassemble(4) == ["check", "decr"]

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
    for x in range(256):
        solutions[f(x)].append(x)

    for y in reversed(range(16)):
        lang = language(y)
        x_list = solutions[y]
        print(f"Since f(x) = {y} for all x in {set(x_list)}, {lang} is recognized by")
        for x in x_list:
            print("  ", disassemble(x))
        print()

find_solutions()
