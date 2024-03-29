from sympy import solve, poly, expand, sqrt, latex
from sympy.abc import w, x, y, z, I
from sympy.parsing.sympy_parser import parse_expr


def solve_singularities(points: str) -> list:
    """Given a string of points of the singular location, returns the cartesian co-ordinate of each point."""
    points = points.replace("^", "**")
    points = parse_expr(points)
    sols = []
    for item in points:
        sol = solve(item, dict=True)
        for subsol in sol:
            # add missing vars
            if w not in subsol:
                subsol[w] = 1
            if x not in subsol:
                subsol[x] = 1
            if y not in subsol:
                subsol[y] = 1
            if z not in subsol:
                subsol[z] = 1
            sols.append(subsol)

    for i, v in enumerate(sols):
        if v[z] != 0:
            v[w] /= v[z]
            v[x] /= v[z]
            v[y] /= v[z]
            v[z] = 1
        elif v[y] != 0:
            v[w] /= v[y]
            v[x] /= v[y]
            v[y] = 1
        elif v[x] != 0:
            v[w] /= v[x]
            v[x] = 1
        else:
            v[w] = 1

        # fix roundoffs
        if isinstance(v[w], float) and v[w].is_integer:
            v[w] = int(v[w])
        if isinstance(v[x], float) and v[x].is_integer:
            v[x] = int(v[x])
        if isinstance(v[y], float) and v[y].is_integer:
            v[y] = int(v[y])
        if isinstance(v[z], float) and v[z].is_integer:
            v[z] = int(v[z])
        sols[i] = (v[w], v[x], v[y], v[z])
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
        shifted = shifted.replace("w", "(x-" + str(sol[0]) + ")")
        shifted = shifted.replace("x", "(x-" + str(sol[1]) + ")")
        shifted = shifted.replace("y", "(y-" + str(sol[2]) + ")")
        shifted = shifted.replace("z", "(z-" + str(sol[3]) + ")")
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
    milnor = []
    degrees = []
    for i, ideal in enumerate(pd):
        # solve ideal
        sols = solve(ideal, dict=True)
        # add missing
        for sol in sols:
            if w not in sol:
                sol[w] = 1
            if x not in sol:
                sol[x] = 1
            if y not in sol:
                sol[y] = 1
            if z not in sol:
                sol[z] = 1

            sol = (sol[w], sol[x], sol[y], sol[z])

            # check if that ideal is singular
            if sol in sings and sol not in milnor:
                milnor.append(sol)
                degrees.append(int(degs[i] / len(sols)))
    return degrees


def solve_tjurina(degs: str, pd: str, sings: list) -> list:
    pd = pd.replace("^", "**")
    pd = parse_expr(pd)
    degs = parse_expr(degs)
    tjurina = []
    degrees = []
    for i, ideal in enumerate(pd):
        sols = solve(ideal, dict=True)
        for sol in sols:
            if w not in sol:
                sol[w] = 1
            if x not in sol:
                sol[x] = 1
            if y not in sol:
                sol[y] = 1
            if z not in sol:
                sol[z] = 1
            sol = (sol[w], sol[x], sol[y], sol[z])
            if sol in sings and sol not in tjurina:
                tjurina.append(sol)
                degrees.append(int(degs[i] / len(sols)))
    return degrees
