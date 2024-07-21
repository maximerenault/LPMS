"""
Infix calculator
Adapted from https://gist.github.com/baileyparker/309436dddf2f34f06cfc363aa5a6c86f

EBNF formulation:

PrecedenceLast = ...
...
Precedence4 = Precedence3 { ("+"|"-") Term } ;
Precedence3 = Precedence2 { ("*"|"/"|"%") Precedence2 } ;
Precedence2 = Precedence1 { ("**") Precedence1 } ;
Precedence1 = Number | "(" PrecedenceLast ")" | Function "(" PrecedenceLast ")" | Constant | Variable ;

Function = "sin" | "cos" | "tan" | "abs" ... ;
Number = Integer { "." Integer } | "." Integer ;
Integer = Digit { Digit } ;
Digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
Constant = "e" | "pi" ;
Variable = "t" | ... ;
"""

import numpy as np
import operator as op
from exceptions.calculatorexceptions import (
    UnexpectedCharacterError,
    BadNumberError,
    BadFunctionError,
    WrongArgsLenError,
    UnexpectedEndError,
)

# Constants for operator precedence
PREC_EXPONENTIATION = 1
PREC_MULT_DIV_MOD = 2
PREC_ADD_SUB = 3
PREC_RELATIONAL = 4
PREC_EQUALITY = 5
PREC_LOGICAL_AND = 6
PREC_LOGICAL_XOR = 7
PREC_LOGICAL_OR = 8


# Utility functions
def evaluate(items):
    """Evaluate a list of float-returning functions separated by operators
    (at the same level of precedence). Returns the result.

    >>> evaluate([lambda *args: 3, '*', lambda *args: 4, '/', lambda *args: 2])
    6
    """

    assert items, "Cannot evaluate empty list"
    assert len(items) % 2 == 1, "List must be of odd length"
    assoc = "left_to_right"  # Useful if one day we add right_to_left associativity

    if assoc == "right_to_left":
        while len(items) > 1:
            items[-3:] = [_evaluate_binary(*items[-3:])]

    if assoc == "left_to_right":
        while len(items) > 1:
            items[:3] = [_evaluate_binary(*items[:3])]

    return items[0]


def _evaluate_binary(lhs, op, rhs):
    """Evaluates a single binary operation op where lhs and rhs are functions
    returning floats or float arrays."""
    return lambda *args: flatten(operators)[op](lhs(*args), rhs(*args))


def flatten(iterable):
    """Flattens a nested iterable by one nesting layer.

    >>> flatten([[1,2], [3]])
    [1, 2, 3]

    >>> flatten({1: {"a": "aa", "b": "bb"}, 2: {"c": "cc"}})
    {'a': 'aa', 'b': 'bb', 'c': 'cc'}
    """
    if isinstance(iterable, dict):
        newdict = {}
        for x in iterable.values():
            newdict.update(x)
        return newdict
    return [x for l in iterable for x in l]


def get_char(list_str, idx):
    """Returns a list of characters of index idx from strings
    listed in list_str. If the string is too short,
    returns an empty string.

    >>> get_char(["abc", "d", "ef"], 1)
    ["b", "", "f"]

    Args:
        list_str (list(str)): list of strings
        id (int): index of strings to retrieve

    Returns:
        list(str): list of characters at index id
    """
    return [string[idx] if idx < len(string) else "" for string in list_str]


def is_char_inorder(list_str):
    """Generator for checking non-number tokens. It asks for the character
    to check, then takes all the tokens starting with this character
    and yields True if such tokens exist, False otherwise. It repeats
    until no more tokens can be checked.

    >>> x = is_char_inorder(["abc","d","ef","g","hij"])
    >>> next(x)
    None
    >>> x.send("h")
    True
    >>> next(x)
    None
    >>> x.send("i")
    True
    >>> next(x)
    None
    >>> x.send("c")
    False

    Yields:
        bool: does the next character correspond to a token
    """
    my_tokens = list_str
    for idx in range(max(len(tok) for tok in my_tokens)):
        list_char_idx = get_char(my_tokens, idx)
        c = yield
        my_tokens = [my_tokens[i] for i, x in enumerate(list_char_idx) if x == c]
        yield bool(my_tokens)


"""
Copied from https://en.cppreference.com/w/c/language/operator_precedence
Precedence                                                  Associativity
1	()	Function call	                                    Left-to-right
2   **      Power
3	* / %	Multiplication, division, and remainder
4	+ -	Addition and subtraction
6	< <=	For relational operators < and ≤ respectively
    > >=	For relational operators > and ≥ respectively
7	== !=	For relational = and ≠ respectively
8	&	Logical AND
9	^	Logical XOR (exclusive or)
10	|	Logical OR (inclusive or)
"""

# These take one value : func(expression)
functions = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "abs": np.abs,
    "floor": np.floor,
}

# These take two values and are disposed between them : expr op expr
operators = {
    PREC_EXPONENTIATION: {"**": op.pow},
    PREC_MULT_DIV_MOD: {"*": op.mul, "/": op.truediv, "%": op.mod},
    PREC_ADD_SUB: {"+": op.add, "-": op.sub},
    PREC_RELATIONAL: {"<": op.lt, "<=": op.le, ">": op.gt, ">=": op.ge},
    PREC_EQUALITY: {"==": op.eq, "!=": op.ne},
    PREC_LOGICAL_AND: {"&": op.and_},
    PREC_LOGICAL_XOR: {"^": op.xor},
    PREC_LOGICAL_OR: {"|": op.or_},
}

constants = {"e": np.e, "pi": np.pi}
variables = ["t"]
all_tokens = list(functions) + list(flatten(operators)) + list(constants) + variables
all_chars = "".join(all_tokens) + "0123456789.e-+()"


# Classes
class PeekableIterator:
    """An iterator that supports 1-lookahead (peek).
    >>> i = PeekableIterator([1, 2, 3])
    >>> i.peek()
    1
    >>> i.peek()
    1
    >>> next(i)
    1
    >>> next(i)
    2
    >>> i.peek()
    3
    """

    def __init__(self, iterable):
        self._iterator = iter(iterable)
        self._next_item = next(self._iterator, None)
        self._done = self._next_item is None

    def peek(self):
        if self._done:
            raise StopIteration
        return self._next_item

    def __next__(self):
        if self._done:
            raise StopIteration
        next_item = self._next_item
        self._next_item = next(self._iterator, None)
        self._done = self._next_item is None
        return next_item

    def __iter__(self):
        return self


class BaseParser:
    """A base class containing utilities useful for a Parser."""

    def __init__(self, items):
        self._items = PeekableIterator(items)

    def _take(self, predicate):
        """
        Yields a contiguous group of items from the items being parsed for
        which the predicate returns True.

        >>> p = BaseParser([2, 4, 3])
        >>> list(p._take(lambda x: x % 2 == 0))
        [2, 4]
        """
        while not self._items._done and predicate(self._items.peek()):
            yield next(self._items)


class Scanner(BaseParser):
    """Scanner scans an input string for calculator tokens and yields them.

    >>> list(Scanner('11 * (2 + 3)').scan())
    [11, '(', 2, '+', 3, ')']
    """

    def scan(self):
        """Yields all tokens in the input."""
        while not self._items._done:
            self._consume_whitespace()
            self._check_supported()
            yield from self._take(lambda c: c in "()")
            yield from self._take_number()
            yield from self._take_function_operator_variable()

    def _consume_whitespace(self):
        list(self._take(str.isspace))

    def _check_supported(self):
        """Checks if next char is supported. Avoids infinite loops."""
        c = self._items.peek()
        if c not in all_chars:
            raise UnexpectedCharacterError(c)

    def _take_number(self):
        """Yields a single number if there is one next in the input.
        Supports decimal and scientific notation.
        """
        number = "".join(self._take(lambda c: c.isdigit() or c == "."))
        if number:
            number += "".join(self._take(lambda c: c == "e"))
            if number[-1] == "e":
                number += "".join(self._take(lambda c: c in "-+"))
                number += "".join(self._take(lambda c: c.isdigit() or c == "."))
        if number:
            try:
                yield float(number)
            except ValueError:
                raise BadNumberError(number)

    def _take_function_operator_variable(self):
        """Yields a single function, operator or variable if there is one next in the input."""
        gen = is_char_inorder(all_tokens)

        def check(c):
            try:
                next(gen)
                return gen.send(c)
            except StopIteration:
                return False

        fov = "".join(self._take(check))
        if fov:
            if fov not in all_tokens:
                raise BadFunctionError(fov, all_tokens)
            yield fov


class Parser(BaseParser):
    """Parser for tokenized calculator inputs."""

    def __init__(self, items):
        super().__init__(items)
        self.vars = []

    def parse(self):
        """Parse calculator input and return the result of evaluating it.

        >>> Parser([1, '*', '(', 2, '+', 3, ')']).parse()
        5
        """
        return self._parse_expression(max(operators.keys())), self.vars

    def _parse_expression(self, precedence):
        """Parse a Term and return the result of evaluating it.

        >>> Parser([3, '*', 2])._parse_expression(2)
        6
        """
        if precedence == PREC_EXPONENTIATION:
            parse = self._parse_factor
        else:
            parse = lambda: self._parse_expression(precedence - 1)

        # Parse the first (required) Factor
        factors = [parse()]
        # Parse any following ("op") Factor
        ops = lambda t: t in operators[precedence]
        factors += flatten((op, parse()) for op in self._take(ops))

        return evaluate(factors)

    def _parse_factor(self):
        """Parse a Factor and return the result of evaluating it.

        >>> Parser([1])._parse_factor()
        1

        >>> Parser(['(', 1, '+', 2, '*', 'abs', '(', '-', 3, ')', ')'])._parse_factor()
        7
        """
        for value in self._take(lambda t: isinstance(t, float)):
            return lambda *args: value

        for var in self._take(lambda t: t in variables):
            if var not in self.vars:
                self.vars.append(var)

            def lambd(*args):
                if len(args) != len(self.vars):
                    raise WrongArgsLenError(len(args), len(self.vars))
                return args[variables.index(var)]

            return lambd

        for sign in self._take(lambda t: t in "+-"):
            value = self._parse_factor()
            return lambda *args: (value(*args) if sign == "+" else -value(*args))

        for cons in self._take(lambda t: t in constants):
            value = constants[cons]
            return lambda *args: value

        for func in self._take(lambda t: t in functions):
            self._expect("(")
            value = self._parse_expression(max(operators.keys()))
            self._expect(")")
            return lambda *args: functions[func](value(*args))

        for _ in self._take(lambda t: t == "("):
            value = self._parse_expression(max(operators.keys()))
            self._expect(")")
            return lambda *args: value(*args)

        # Parsing the number, function and subexpresion failed
        raise self._unexpected("number", "(", "function")

    def _expect(self, char):
        """Expect a certain character, or raise if it is not next."""
        for _ in self._take(lambda t: t == char):
            return
        raise self._unexpected(char)

    def _unexpected(self, *expected):
        """Create an exception for an unexpected character."""
        try:
            return UnexpectedCharacterError(self._items.peek(), expected)
        except StopIteration:
            return UnexpectedEndError(expected)


def calculate(expression, return_vars=False):
    """Evaluates a mathematical expression and returns the result.

    >>> calculate('3 * (1 + 6 / 3)')
    9
    """
    scan = Scanner(expression).scan()
    result, vars = Parser(scan).parse()

    if return_vars:
        return (result(), vars) if not vars else (result, vars)

    return result() if not vars else result


# my_constants = {"Emin": 0.1, "Emax": 2.0, "T1": 0.15, "T2": 0.3, "Tt": 0.7}
# constants = constants | my_constants
# all_tokens = list(functions) + list(flatten(operators)) + list(constants) + variables
# all_chars = "".join(all_tokens) + "0123456789.e-+()"  # Add characters specific to numbers

# tmod = calculate("t-floor(t/Tt)*Tt")
# El = calculate("1.333e3 * (Emin+(Emax-Emin)*( (t<=T2)*(t>=T1)*1/2*(1+cos(pi*(t-T1)/(T2-T1))) + (t<T1)*1/2*(1-cos(pi*t/T1)) ))")

# t = np.linspace(0,3,300)
# tmod_values = tmod(t)
# El_values = El(tmod_values)

# import matplotlib.pyplot as plt

# plt.plot(t,El_values)
# plt.show()
