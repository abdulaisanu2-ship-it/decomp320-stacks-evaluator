"""
DCOMP320 - Data Structures and Algorithm
Assignment: Stacks Implementation

Reads mathematical expressions from input.txt, evaluates each one using
stacks (shunting-yard style, two stacks), and writes the results to
output.txt in the same layout as the input (separator lines preserved).

Usage:
    python stack_evaluator.py [input_file] [output_file]
Defaults: input.txt -> output.txt
"""

import sys


class Stack:
    """A simple LIFO stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        """Return True if the stack has no items."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items in the stack."""
        return len(self._items)


# Operator precedence ('u' is unary minus, e.g. -5 or 3 * -2)
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "u": 3}


def tokenize(expression):
    """Convert an expression string into a list of tokens.

    Numbers become floats; operators and parentheses stay as strings.
    A '-' with no operand before it is marked as unary minus ('u').
    """
    tokens = []
    i = 0
    n = len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            start = i
            while i < n and (expression[i].isdigit() or expression[i] == "."):
                i += 1
            try:
                tokens.append(float(expression[start:i]))
            except ValueError:
                raise ValueError(f"Invalid number '{expression[start:i]}'")
        elif ch in "+-*/()":
            # '-' is unary at the start, after '(' or after another operator
            if ch == "-" and (not tokens or tokens[-1] in ("(", "+", "-", "*", "/", "u")):
                tokens.append("u")
            else:
                tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"Invalid character '{ch}'")
    return tokens


def apply_operator(operators, operands):
    """Pop one operator and its operand(s), compute, and push the result."""
    op = operators.pop()
    try:
        if op == "u":
            operands.push(-operands.pop())
            return
        right = operands.pop()
        left = operands.pop()
    except IndexError:
        raise ValueError("Invalid expression")
    if op == "+":
        operands.push(left + right)
    elif op == "-":
        operands.push(left - right)
    elif op == "*":
        operands.push(left * right)
    elif op == "/":
        if right == 0:
            raise ValueError("Division by zero")
        operands.push(left / right)


def evaluate_expression(expression):
    """Evaluate an infix expression using an operand stack and operator stack."""
    operands = Stack()
    operators = Stack()

    for token in tokenize(expression):
        if isinstance(token, float):
            operands.push(token)
        elif token == "(":
            operators.push(token)
        elif token == ")":
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators, operands)
            if operators.is_empty():
                raise ValueError("Mismatched parentheses")
            operators.pop()  # discard '('
        elif token == "u":
            operators.push(token)  # prefix operator: nothing to resolve first
        else:  # binary operator + - * /
            while (not operators.is_empty()
                   and operators.peek() != "("
                   and PRECEDENCE[operators.peek()] >= PRECEDENCE[token]):
                apply_operator(operators, operands)
            operators.push(token)

    while not operators.is_empty():
        if operators.peek() == "(":
            raise ValueError("Mismatched parentheses")
        apply_operator(operators, operands)

    if operands.size() != 1:
        raise ValueError("Invalid expression")
    return operands.pop()


def format_result(value):
    """Show whole numbers without '.0'; otherwise up to 4 decimal places."""
    if value == int(value):
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def is_separator(line):
    """A separator is a line containing only 3 or more dashes."""
    stripped = line.strip()
    return len(stripped) >= 3 and set(stripped) == {"-"}


def process_file(input_path, output_path):
    """Read input line by line, evaluate expressions, write results."""
    with open(input_path, "r") as infile, open(output_path, "w") as outfile:
        for line in infile:
            text = line.rstrip("\n")
            if is_separator(text) or text.strip() == "":
                outfile.write(text + "\n")  # keep layout unchanged
            else:
                try:
                    result = format_result(evaluate_expression(text))
                except ValueError as err:
                    result = f"Error: {err}"
                outfile.write(result + "\n")


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    try:
        process_file(input_path, output_path)
        print(f"Done. Results written to {output_path}")
    except FileNotFoundError:
        print(f"Error: could not find '{input_path}'")


if __name__ == "__main__":
    main()
