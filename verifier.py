from pathlib import Path

from cgshop2025_pyutils import (
    DelaunayBasedSolver,
    InstanceDatabase,
    ZipSolutionIterator,
    ZipWriter,
    verify,
)

# Load the instances from the example_instances folder. Instead of referring to the folder,
# you can also give a path to a zip file.
idb = InstanceDatabase("example_instances/")

# If the solution zip file already exists, delete it
if Path("example_solutions.zip").exists():
    Path("example_solutions.zip").unlink()

# Compute solutions for all instances using the provided (naive) solver
solutions = []
for instance in idb:
    solver = DelaunayBasedSolver(instance)
    solution = solver.solve()
    solutions.append(solution)

# Write the solutions to a new zip file
with ZipWriter("example_solutions.zip") as zw:
    for solution in solutions:
        zw.add_solution(solution)

# Verify the solutions
for solution in ZipSolutionIterator("example_solutions.zip"):
    instance = idb[solution.instance_uid]
    result = verify(instance, solution)
    print(f"{solution.instance_uid}: {result}")
    assert not result.errors, "Expect no errors."