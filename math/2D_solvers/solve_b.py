from sympy import solve, poly, expand, sqrt, latex
from sympy.abc import x, y, z, I
from sympy.parsing.sympy_parser import parse_expr


def solve_singularities(points: str) -> list:
    """Given a string of points of the singular location, returns the cartesian co-ordinate of each point."""
    points = points.replace("^", "**")
    points = parse_expr(points)
    sols = []
    for item in points:
        sol = solve(item, dict=True)
        for subsol in sol:
            if x not in subsol:
                subsol[x] = 1
            if y not in subsol:
                subsol[y] = 1
            if z not in subsol:
                subsol[z] = 1
            sols.append(subsol)

    for i, v in enumerate(sols):
        if v[z] != 0:
            v[x] /= v[z]
            v[y] /= v[z]
            v[z] = 1
        elif v[y] != 0:
            v[x] /= v[y]
            v[y] = 1
        else:
            # Sing is of form (x, 0, 0)
            v[x] = 1
        # fix roundoffs
        if isinstance(v[x], float) and v[x].is_integer:
            v[x] = int(v[x])
        if isinstance(v[y], float) and v[y].is_integer:
            v[y] = int(v[y])
        if isinstance(v[z], float) and v[z].is_integer:
            v[z] = int(v[z])
        sols[i] = (v[x], v[y], v[z])
    # remove duplicate solutions
    sols = list(dict.fromkeys(sols))
    # return the latex as well for display
    return sols, latex(sols)


def solve_multiplicities(homogenized: str, points: list) -> list:
    """Given the homogenized equation and a list of singular co-ordinates return the multiplicity at each point"""
    mults = []
    for sol in points:
        shifted = homogenized
        min_degree = float("inf")
        # shift the homogenized equation by the solution
        shifted = shifted.replace("x", "(x-" + str(sol[0]) + ")")
        shifted = shifted.replace("y", "(y-" + str(sol[1]) + ")")
        shifted = shifted.replace("z", "(z-" + str(sol[2]) + ")")
        # expand generated polynominal
        for term in poly(expand(shifted)).terms():
            # tuple representing (deg(x), deg(y), deg(z)) per term
            all_degrees = term[0]

            term_degree = sum(all_degrees)

            if term_degree == 0:
                # skip constant terms
                continue

            # Get new minimum
            min_degree = min(min_degree, term_degree)

        mults.append(min_degree)
    return mults


def solve_milnor(degs: str, pd: str, sings: list) -> list:
    pd = pd.replace("^", "**")
    pd = parse_expr(pd)
    degs = parse_expr(degs)
    milnor = [0 for _ in range(len(sings))]
    for i, ideal in enumerate(pd):
        sols = solve(ideal, dict=True)
        for sol in sols:
            if x not in sol:
                sol[x] = 1
            if y not in sol:
                sol[y] = 1
            if z not in sol:
                sol[z] = 1
            sol = (sol[x], sol[y], sol[z])
            for j, sing in enumerate(sings):
                if sol == sing:
                    milnor[j] = int(degs[i] / len(sols))
    return milnor


def solve_tjurina(degs: str, pd: str, sings: list) -> list:
    pd = pd.replace("^", "**")
    pd = parse_expr(pd)
    degs = parse_expr(degs)
    tjurina = []
    for i, ideal in enumerate(pd):
        sols = solve(ideal, dict=True)
        for sol in sols:
            if x not in sol:
                sol[x] = 1
            if y not in sol:
                sol[y] = 1
            if z not in sol:
                sol[z] = 1
            sol = (sol[x], sol[y], sol[z])
            if sol in sings:
                # print(sol, degs[i] / len(sols), ideal)
                # TODO : fix not all sols valid
                tjurina.append(int(degs[i] / len(sols)))
    return tjurina


def solve_arith_genus(degree: int) -> int:
    """Using formula described here: https://en.wikipedia.org/wiki/Genus%E2%80%93degree_formula"""
    return int(0.5 * (degree - 1) * (degree - 2))


def solve_delta(mults: list) -> list:
    """Calculate delta invariant for each multiplicity"""
    delta = [int(0.5 * m * (m - 1)) for m in mults]
    return delta


def solve_geo_genus(arith_genus: int, delta: list) -> int:
    """Calculate arithmetic genus"""
    delta = sum(delta)
    return arith_genus - delta


def solve_branching(milnor: list, delta: list) -> list:
    """Using Milnor-Jung formula"""
    branching = []
    try:
        branching = [2 * d + 1 - m for m, d in zip(milnor, delta)]
        # branching = 2 * sum(delta) + 1 - sum(milnor)
    except:
        # few issues as milnor is not fully done yet
        pass
    return branching
