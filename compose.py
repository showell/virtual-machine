"""
compose.py — symbolic six-step composition of the VM step polynomials
for a fixed program.

Purpose
-------
The existing stepper evaluates the step polynomials one step at a time
on concrete 0/1 inputs. This tool does the same work SYMBOLICALLY:
substitute the current state polynomials (in h0, l0) into the master
step polynomials to obtain the state polynomials after step i.

After six steps, accepted(h0, l0) is a single polynomial that tells
you, for each (h0, l0) in {0,1}x{0,1}, whether the program accepts
the input AX = 2*h0 + l0. That is the Cook-Levin "computation as a
formula" shape for this particular program.

This is primarily a MEASUREMENT tool. It reports per-step stats so we
can tell whether the polynomial size blows up (structural problem) or
the coefficients blow up (arithmetic problem). It has hard caps so it
cannot hang: if any intermediate polynomial exceeds MAX_MONOMIALS or
any step exceeds MAX_STEP_SECONDS, it aborts with a partial report.
"""

import time

from poly import Poly
import stepper


MAX_MONOMIALS = 50_000
MAX_STEP_SECONDS = 5.0

OPS = {"nada": 0, "zero": 1, "decr": 2, "mod2": 3}
STATE_VARS = ("hb", "lb", "halted", "accepted")


def poly_stats(p):
    if len(p.terms) == 0:
        return (0, 0, {})
    max_coeff = max(abs(t.coeff) for t in p.terms)
    var_max = {}
    for t in p.terms:
        for vp in t.var_powers:
            var_max[vp.var_name] = max(var_max.get(vp.var_name, 0), vp.exponent)
    return (len(p.terms), max_coeff, var_max)


def safe_substitute(poly, var_name, replacement):
    if var_name in poly.variables():
        return poly.substitute(var_name, replacement)
    return poly


def safe_apply(poly, **kv):
    present = {k: v for k, v in kv.items() if k in poly.variables()}
    if not present:
        return poly
    return poly.apply(**present)


def run_program(n, program):
    halted = False
    AX = n
    accepted = False
    for op in program:
        if halted:
            continue
        if op == "nada":
            pass
        elif op == "zero":
            if AX == 0:
                halted = True
                accepted = True
        elif op == "decr":
            if AX == 0:
                halted = True
            else:
                AX -= 1
        elif op == "mod2":
            AX = AX % 2
    return accepted


def compose(program, verbose=True):
    """Compose the step polynomials through a fixed 6-instruction program.

    Returns (hb, lb, halted, accepted) polynomials in (h0, l0), or
    None if a cap was hit.
    """
    (sym_hb, sym_lb, sym_halted, sym_accepted) = stepper.STEP_POLYNOMIALS

    state = {
        "hb": Poly.var("h0"),
        "lb": Poly.var("l0"),
        "halted": Poly.constant(0),
        "accepted": Poly.constant(0),
    }

    if verbose:
        print(f"{'step':>4}  {'op':<5}  {'monos[hb,lb,halted,acc]':<28}  {'max|c|':>6}  {'max_deg':>7}  {'time':>6}")
        print("-" * 72)

    for i, op_name in enumerate(program):
        op = OPS[op_name]
        op_hb = op // 2
        op_lb = op % 2

        step_start = time.monotonic()

        new_state = {}
        for label, sym_poly in (
            ("hb", sym_hb),
            ("lb", sym_lb),
            ("halted", sym_halted),
            ("accepted", sym_accepted),
        ):
            p = sym_poly
            for v in STATE_VARS:
                p = safe_substitute(p, v, state[v])
            p = safe_apply(p, op_hb=op_hb, op_lb=op_lb)

            monos, _, _ = poly_stats(p)
            if monos > MAX_MONOMIALS:
                print(f"ABORT at step {i+1} ({op_name}) on {label}: {monos} monomials > {MAX_MONOMIALS}")
                return None
            if time.monotonic() - step_start > MAX_STEP_SECONDS:
                print(f"ABORT at step {i+1} ({op_name}) on {label}: exceeded {MAX_STEP_SECONDS}s")
                return None
            new_state[label] = p

        state = new_state
        step_elapsed = time.monotonic() - step_start

        if verbose:
            stats = [poly_stats(state[v]) for v in STATE_VARS]
            monos = "[" + ",".join(f"{s[0]}" for s in stats) + "]"
            max_c = max((s[1] for s in stats), default=0)
            all_degs = {}
            for _, _, vd in stats:
                for k, v in vd.items():
                    all_degs[k] = max(all_degs.get(k, 0), v)
            max_deg = max(all_degs.values()) if all_degs else 0
            print(f"{i+1:>4}  {op_name:<5}  {monos:<28}  {max_c:>6}  {max_deg:>7}  {step_elapsed:>5.2f}s")

    return (state["hb"], state["lb"], state["halted"], state["accepted"])


def verify(program, accepted_poly):
    print(f"  accepted(h0, l0) = {accepted_poly}")
    for n in range(4):
        hb_val = n // 2
        lb_val = n % 2
        assignments = {}
        vars_used = accepted_poly.variables()
        if "h0" in vars_used:
            assignments["h0"] = hb_val
        if "l0" in vars_used:
            assignments["l0"] = lb_val
        got = accepted_poly.eval(**assignments) if vars_used else (
            accepted_poly.terms[0].coeff if accepted_poly.terms else 0
        )
        expected = 1 if run_program(n, program) else 0
        flag = "OK" if got == expected else "MISMATCH"
        print(f"  input {n}: composed={got}, interpreter={expected}  {flag}")
        assert got == expected, (n, got, expected)


def main():
    programs = [
        ["nada"] * 6,
    ]
    for program in programs:
        print()
        print(f"Program: {program}")
        result = compose(program)
        if result is None:
            print("  (composition aborted)")
            continue
        _, _, _, accepted = result
        print()
        verify(program, accepted)


if __name__ == "__main__":
    main()
