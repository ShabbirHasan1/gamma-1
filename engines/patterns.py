import pandas as pd
from typing import Callable, List, Dict
from dataclasses import dataclass
from functools import lru_cache

from exceptions import InvalidMethodException, NotDefinedException
from exceptions.exceptions import InvalidImplementationException

@dataclass
class Variables:
    COLOR: str = "color"
    WHITE: str = "white"
    BLACK: str = "black"
    OPEN: float = 0.0
    HIGH: float = 0.0
    LOW: float = 0.0
    CLOSE: float = 0.0

@dataclass
class Methods:
    PREVIOUS: str = "previous"
    NEXT: str = "next"
    IF: str = "if"
    ELSE: str = "else"

@dataclass
class Symbols:
    BRACKET_OPEN: str = "("
    BRACKET_CLOSE: str = ")"
    DOT = "."
    EQUAL: str = "="
    EQUAL_EQUAL: str = "=="
    METHOD_OPEN: str = "{"
    METHOD_CLOSE: str = "}"
    LESS_THAN: str = "<"
    GREATER_THAN: str = ">"
    SEMICOLON: str = ";"
    DOUBLE_QUOTE: str = '"'

class PatternEngine:
    def __init__(self, ticker: str = None, pricesDf: pd.DataFrame = None):
        
        self._df: pd.DataFrame = pricesDf
        self._ticker: str = ticker

        self._containers: Dict = {}

        self._variables: Dict = {
            "color": Variables.COLOR,
            "white": Variables.WHITE,
            "black": Variables.BLACK,
            "open": Variables.OPEN,
            "high": Variables.HIGH,
            "low": Variables.LOW,
            "close": Variables.CLOSE,
        }

        self._methods: Dict = {
            "previous": Methods.PREVIOUS,
            "next": Methods.NEXT,
            "if": Methods.IF,
            "else": Methods.ELSE
        }

        self._symbols: Dict = {
            "(": Symbols.BRACKET_OPEN,
            ")": Symbols.BRACKET_CLOSE,
            ".": Symbols.DOT,
            ">": Symbols.GREATER_THAN,
            "<": Symbols.LESS_THAN,
            "=": Symbols.EQUAL,
            "{": Symbols.METHOD_OPEN,
            "}": Symbols.METHOD_CLOSE,
            "==": Symbols.EQUAL_EQUAL,
            ";": Symbols.SEMICOLON,
            '"': Symbols.DOUBLE_QUOTE
        }

    @lru_cache
    def _getPrices(self, interval: str, period: str, callback: Callable = None) -> pd.DataFrame:
        """Get prices from the database

        Args:
            interval (str): Set the interval
            period (str): Set the period
            callback (Callable, optional): Callback method. Defaults to None.

        Raises:
            InvalidMethodException: If ticker is not provided

        Returns:
            pd.DataFrame: Returns the prices in pandas dataframe.
        """

        if self._ticker is None:
            raise InvalidMethodException("Ticker not provided.")
        from utils import Prices
        return Prices.getHistory(self._ticker, interval, period) if callback is None else Prices.getHistory(self._ticker, interval, period, callback)

    @lru_cache
    def _getTokens(self, expression: str, callback: Callable = None) -> List:
        """Get the tokens from the expression
        
        Args:
            expression (str): Set the expression
            callback (Callable, optional): Callback method. Defaults to None.
        
        Returns:
            List: Returns the token in list.
        """

        expression = expression.lower()
        tokens: List = []
        token: str = ""
        i = 0
        
        while i < len(expression):
            if expression[i] not in self._symbols.keys() and expression[i] != " ":
                if i != len(expression) - 1:
                    token += expression[i]
                    i += 1
                else:
                    token += expression[i]
                    tokens.append(token)
                    i += 1
            else:
                if token != "":
                    tokens.append(token)
                token = ""
                if expression[i] != " ":
                    tokens.append(expression[i])
                i += 1
        
        return tokens if callback is None else callback(tokens)

    def _getStatements(self, tokens: List, callback: Callable = None) -> List[List]:
        """Generates statements from tokens

        Args:
            tokens (List): Contains the tokens
            callback (Callable, optional): Callable method. Defaults to None.

        Returns:
            List[List]: Returns are list of statements
        """
        statements: List = []
        statement: List = []
        for tok in tokens:
            if tok != Symbols.SEMICOLON and tok != Symbols.METHOD_CLOSE:
                statement.append(tok)
            else:
                statement.append(tok)
                statements.append(statement)
                statement = []
        
        return statements if callback is None else callback(statements)

    def test(self, string: str = None):
        toks: List = self._getTokens(string)
        statements = self._getStatements(toks)
       
        '''
        Each statement ends with ;. This is when we don't have any loop.
        If we have loop, then condition starts with ( and ends with ), next comes { some other conditions }

        Instead of thinking IF and ELSE as Conditional we can think of them as Methods, which accepts either 0 or 1.

        This makes it somewhat easy, now we only need to handle variables or methods.

        Now for method the pseudocode:
            method(somevalue) { code }
                    or
            method(somevalue).Variable 

        Ok now we pretty much have all the statements and now we can start making sense of them.
        '''

        for statement in statements:
            for i in range(len(statement)):
                if statement[i] == Symbols.EQUAL:
                    # if only one equal we assign, if double then we check. For any case we want either one or two tokens in front
                    # of it.
                    if i < 1:
                        raise InvalidImplementationException(f'Invalid implementation of "{Symbols.EQUAL}"')
                    elif statement[i-1] == Symbols.EQUAL:
                        # Here we check, not assign
                        return
                    else:
                        # we assign here.
                        # One can assign to either containers or new variables
                        if statement[i-1] in self._variables:
                            # we have reserved container.
                            # we also need to check that if the assigned value is definite or a variable.
                            # if definite we can simply assign them, or else we have to get that value from the variable
                            # and then assign it.
                            if statement[i+1] in self._containers.keys():
                                # we are assigning a already defined variable.
                                try:
                                    self._variables[statement[i-1]] = self._containers[statement[i+1]]
                                except KeyError:
                                    raise InvalidImplementationException(f'{statement[i+1]} not defined.')
                            elif statement[i+1] in self._variables:
                                self._variables[statement[i-1]] = self._variables[statement[i+1]]
                            else:
                                self._variables[statement[i-1]] = statement[i+1]

        return self._variables['color']