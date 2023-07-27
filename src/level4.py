import os

from typing import Generic, TypeVar, Dict, List, Optional
from abc import ABC, abstractmethod

# Type variables for variable type (V) and domain type (D)
V = TypeVar('V')  # variable type
D = TypeVar('D')  # domain type


class Constraint(Generic[V, D], ABC):
    """
    Base class for all constraints.
    """
    def __init__(self, variables: List[V]) -> None:
        """
        Initialize the constraint with a list of variables it applies to.
        """
        self.variables = variables

    @abstractmethod
    def satisfied(self, assignment: Dict[V, D]) -> bool:
        """
        Abstract method to be overridden by subclasses.
        It checks whether the constraint is satisfied based on the given variable assignment.
        """
        ...


class CSP(Generic[V, D]):
    """
    Constraint Satisfaction Problem (CSP) class.
    """
    def __init__(self, variables: List[V], domains: Dict[V, List[D]]) -> None:
        """
        Initialize the CSP with variables and their domains.
        """
        self.variables: List[V] = variables
        self.domains: Dict[V, List[D]] = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        self.satisfied_constraints: Dict[V, List[Constraint[V, D]]] = {}  # Store satisfied constraints

        # Initialize constraints for each variable
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it.")

    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        """
        Adds a constraint to variables as per their domains.
        """
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)

    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        """
        Checks if the value assignment is consistent by evaluating all constraints
        for the given variable against it.
        """
        for constraint in self.constraints[variable]:
            if constraint not in self.satisfied_constraints.get(variable, []):
                if not constraint.satisfied(assignment):
                    return False
                self.satisfied_constraints.setdefault(variable, []).append(constraint)
        return True

    def backtracking_search(self, assignment: Dict[V, D] = {}) -> Optional[Dict[V, D]]:
        """
        Performs backtracking search to find a valid solution for the CSP.
        """
        if len(assignment) == len(self.variables):
            return assignment

        unassigned: List[V] = [v for v in self.variables if v not in assignment]
        first: V = unassigned[0]

        for value in self.domains[first]:
            local_assignment = assignment.copy()

            if value in local_assignment.values():
                continue

            local_assignment[first] = value

            if self.consistent(first, local_assignment):
                result: Optional[Dict[V, D]] = self.backtracking_search(local_assignment)

                if result is not None:
                    return result

        return None


class CustomConstraint(Constraint[str, int]):
    """
    CustomConstraint is a subclass of Constraint class.
    """
    def __init__(self, equation: str) -> None:
        """
        Initialize the CustomConstraint with the equation and extract unique letters from it.
        """
        self.letters: List[str] = extract_unique_letters(equation)
        super().__init__(self.letters)
        self.equation = equation

    def check_equation(self, input_string):
        """
        Checks if the equation is correct by evaluating the left and right sides and comparing the results.
        """
        left_side, right_side = input_string.split("=")
        left_side = left_side.strip()
        right_side = right_side.strip()

        try:
            left_result = eval(left_side)
            right_result = eval(right_side)

            if left_result == right_result:
                return True
            else:
                return False
        except:
            return False

    def satisfied(self, assignment: Dict[str, int]) -> bool:
        """
        Checks if the constraint is satisfied based on the assignment of values to variables.
        """
        if len(set(assignment.values())) < len(assignment):
            return False

        if len(assignment) == len(self.letters):
            modified_equation = self.equation
            for var, value in assignment.items():
                modified_equation = modified_equation.replace(var, str(value))
            return self.check_equation(modified_equation)

        return True  # no conflict


def extract_unique_letters(input_string):
    """
    Extracts unique letters from the input string (excluding '+', '*', '-', '=', and duplicates).
    """
    return set(char for char in input_string if char.isalpha() and char not in ('+', '*', '-', '='))


class CSPSolver:
    """
    CSPSolver class for handling input from 'input.txt' and writing output to 'output.txt'.
    """
    def __init__(self, input_file='input4.txt', output_file='output4.txt'):
        # Get the absolute path of the currently running Python script
        current_script_path = os.path.abspath(__file__)
        # Extract the directory from the script path
        current_folder = os.path.dirname(current_script_path)

        self.input_file = os.path.join(current_folder, "testcases", "input", input_file)
        self.output_file = os.path.join(current_folder, "testcases", "output", output_file)

        # Clear output file
        with open(self.output_file, 'w') as file:
            file.write("")

    def read_input(self):
        """
        Read the input equation from 'input.txt'.
        """
        try:
            with open(self.input_file, 'r') as file:
                return [equation.strip() for equation in file]
        except:
            print("please create input.txt!")
            exit(0)

    def write_output(self, solution):
        """
        Write the solution to 'output.txt'.
        """
        with open(self.output_file, 'a') as file:
            if solution is None:
                file.write("No solution found!\n")
            else:
                # Sort the dictionary by keys
                sorted_dict = {k: v for k, v in sorted(solution.items())}

                for variable, _ in sorted_dict.items():
                    file.write(f"{variable}")

                file.write(f"=")

                for _, value in sorted_dict.items():
                    file.write(f"{value}")
            file.write("\n")

    def solve_csp(self):
        """
        Read the input equation, solve the CSP, and write the output to 'output.txt'.
        """
        input_equations = self.read_input()
        for input_equation in input_equations:
            letters = extract_unique_letters(input_equation)
            possible_digits = {letter: set(range(10)) for letter in letters}

            unique_first_chars = extract_unique_letters(input_equation)
            for letter in unique_first_chars:
                possible_digits[letter] = set(range(1, 10))

            csp = CSP(letters, possible_digits)
            csp.add_constraint(CustomConstraint(input_equation))
            solution = csp.backtracking_search()

            self.write_output(solution)


if __name__ == "__main__":
    print("Please wait for a second!")
    solver = CSPSolver()
    solver.solve_csp()
