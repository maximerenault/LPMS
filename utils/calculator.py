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
from exceptions.calculatorexceptions import *

# A few utility functions


def evaluate(items):
    """
    Evaluate a list of float returning functions separated by operators
    (at the same level of precedence). Returns the result.

    >>> evaluate([lambda *args: 3, '*', lambda *args: 4, '/', lambda *args: 2])
    6
    """

    assert items # Cannot evaluate empty list
    assert len(items) % 2 == 1 # List must be of odd length

    assoc = "left_to_right" # Useful if one day we add right_to_left associativity

    if assoc == "right_to_left":
        while len(items) > 1:
            items[-3:] = [_evaluate_binary(*items[-3:])]
    
    if assoc == "left_to_right":
        while len(items) > 1:
            items[:3] = [_evaluate_binary(*items[:3])]

    return items[0]


def _evaluate_binary(lhs, op, rhs):
    """
    Evalutates a single binary operation op where lhs and rhs are functions
    returning floats or float arrays.
    """
    return lambda *args: flatten(operators)[op](lhs(*args), rhs(*args))


def flatten(iterable):
    """
    Flattens a nested iterable by one nesting layer.

    >>> flatten([[1,2], [3]])
    [1, 2, 3]

    >>> flatten({1: {"a": "aa", "b": "bb"}, 2: {"c": "cc"}})
    {'a': 'aa', 'b': 'bb', 'c': 'cc'}
    """
    if type(iterable) == dict:
        newdict = {}
        for x in iterable.values():
            newdict = newdict | x
        return newdict
    return [x for l in iterable for x in l]


def get_char(list_str, id):
    """
    Returns a list of characters of index id from strings
    listed in liststr. If the string is too short,
    returns an empty string.

    >>> get_char(["abc", "d", "ef"], 1)
    ["b", "", "f"]

    Args:
        list_str (list(str)): list of strings
        id (int): index of strings to retrieve

    Returns:
        list(str): list of characters at index id
    """
    list_ret = []
    for string in list_str:
        try:
            list_ret += string[id]
        except IndexError:
            list_ret += ""
    return list_ret


def is_char_inorder(list_str):
    """
    Generator for checking non number tokens. It asks for the character
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
    for id in range(max([len(tok) for tok in my_tokens])):
        list_char_id = get_char(my_tokens, id)
        c = yield
        my_tokens = [my_tokens[i] for i, x in enumerate(list_char_id) if x == c]
        yield my_tokens != []


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
    1: {"**": op.pow},
    2: {"*": op.mul, "/": op.truediv, "%": op.mod},
    3: {"+": op.add, "-": op.sub},
    4: {
        "<": op.lt,
        "<=": op.le,
        ">": op.gt,
        ">=": op.ge,
    },
    5: {"==": op.eq, "!=": op.ne},
    6: {"&": op.and_},
    7: {"^": op.xor},
    8: {"|": op.or_},
}

# Constants
constants = {"e": np.e, "pi": np.pi}

# Variables
variables = ["t"]

all_tokens = list(functions) + list(flatten(operators)) + list(constants) + variables
all_chars = "".join(all_tokens) + "0123456789.e-+()"  # Add characters specific to numbers


class PeekableIterator:
    """
    An iterator that supports 1-lookahead (peek).
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
        self._next_item = next(self._iterator)
        self._done = False

    def peek(self):
        """
        Return the next item that will be returned by the iterator without
        advancing the iterator. Raises StopIteration if the iterator is done.
        """
        if self._done:
            raise StopIteration

        return self._next_item

    def __next__(self):
        """
        Return next item and update the peekable.
        Raises StopIteration if the iterator is done.
        """
        if self._done:
            raise StopIteration

        next_item = self._next_item
        try:
            self._next_item = next(self._iterator)
        except StopIteration:
            self._done = True
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
            # Ignore any whitespace that may be next
            self._consume_whitespace()
            self._check_supported()

            yield from self._take(lambda c: c in "()")
            yield from self._take_number()
            yield from self._take_function_operator_variable()

    def _consume_whitespace(self):
        """_take()s whitespace characters, but does not yield them."""
        # Note we need the list here to force evaluation of the generator
        list(self._take(lambda char: char.isspace()))

    def _check_supported(self):
        """Checks if next char is supported. Avoids infinite loops."""
        c = self._items.peek()
        if not c in all_chars:
            raise UnexpectedCharacterError(c)

    def _take_number(self):
        """
        Yields a single number if there is one next in the input.
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
        return self._parse_expression(max(list(operators))), self.vars

    def _parse_expression(self, precedence):
        """Parse a Term and return the result of evaluating it.

        >>> Parser([3, '*', 2])._parse_expression(2)
        6
        """
        if precedence == 1:
            parse = self._parse_factor
        else:
            parse = lambda: self._parse_expression(precedence - 1)

        # Parse the first (required) Factor
        factors = [parse()]

        # Parse any following ("op") Factor
        ops = lambda t: t in operators[precedence].keys()
        factors += flatten((op, parse()) for op in self._take(ops))

        return evaluate(factors)

    def _parse_factor(self):
        """Parse a Factor and return the result of evaluating it.

        >>> Parser([1])._parse_factor()
        1

        >>> Parser(['(', 1, '+', 2, '*', 'abs', '(', '-', 3, ')', ')'])._parse_factor()
        7
        """

        # This isn't really a for, we're just using it to handle the case
        # where it doesn't find a number (gracefully skip). If it finds one,
        # we return the number.
        for value in self._take(lambda t: isinstance(t, float)):
            return lambda *args: value

        for var in self._take(lambda t: t in variables):
            if var not in self.vars:
                self.vars += var

            def lambd(*args):
                if len(args) != len(self.vars):
                    raise WrongArgsLenError(len(args), len(self.vars))
                return args[variables.index(var)]

            return lambd

        for sign in self._take(lambda t: t in "+-"):
            if sign == "+":
                return self._parse_factor()
            if sign == "-":
                value = self._parse_factor()
                return lambda *args: -1 * value(*args)

        for cons in self._take(lambda t: t in constants.keys()):
            value = constants[cons]
            return lambda *args: value

        for func in self._take(lambda t: t in functions.keys()):
            self._expect("(")
            value = self._parse_expression(max(list(operators)))
            self._expect(")")
            return lambda *args: functions[func](value(*args))

        for _ in self._take(lambda t: t == "("):
            value = self._parse_expression(max(list(operators)))
            self._expect(")")
            return lambda *args: value(*args)

        # Parsing the number, function and subexpresion failed
        raise self._unexpected("number", "(")

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


def calculate(expression):
    """Evaluates a mathematical expression and returns the result.

    >>> calculate('3 * (1 + 6 / 3)')
    9
    """
    scan = Scanner(expression).scan()  # Iterator, once read it has to be rebuilt (no print)
    return Parser(scan).parse()


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
