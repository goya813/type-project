from dataclasses import dataclass
from typing import Any


Expr = Any
Value = int | bool


@dataclass
class Error:
    def __str__(self):
        return "error"


@dataclass
class Plus:
    e1: Any
    e2: Any

    def __str__(self):
        return f"({self.e1} + {self.e2})"


@dataclass
class Minus:
    e1: Any
    e2: Any

    def __str__(self):
        return f"({self.e1} - {self.e2})"


@dataclass
class Times:
    e1: Any
    e2: Any

    def __str__(self):
        return f"({self.e1} * {self.e2})"


@dataclass
class Lt:
    e1: Any
    e2: Any

    def __str__(self):
        return f"{self.e1} < {self.e2}"


@dataclass
class If:
    e1: Any
    e2: Any
    e3: Any

    def __str__(self):
        return f"if {self.e1} then {self.e2} else {self.e3}"


@dataclass
class Let:
    key: str
    e1: Any
    e2: Any

    def __str__(self):
        return f"let {self.key} = {self.e1} in {self.e2}"


@dataclass
class Var:
    key: str

    def __str__(self):
        return self.key


@dataclass
class Var:
    key: str

    def __str__(self):
        return self.key


class Env:
    vars: list[(str, Value)]

    def __init__(self, vars: list[(str, Value)]):
        self.vars = vars

    def __eq__(self, other):
        return self.vars == other

    def pop(self) -> "Env":
        return Env(self.vars[:-1])

    def push(self, key: str, value: Value) -> "Env":
        return Env(self.vars + [(key, value)])

    def top(self) -> (str, Value):
        return self.vars[-1]

    def lookup(self, key):
        for k, v in self.vars[::-1]:
            if k == key:
                return v
        raise KeyError(f"key {key} not found")

    def __str__(self):
        return ",".join([f"{k}={v}" for k, v in self.vars])

    def __repr__(self):
        return str(self)


@dataclass
class Judgement:
    env: Env | None
    e: Any
    v: Any

    def __str__(self):
        prefix = ""
        if self.env:
            prefix = str(self.env)
            if prefix:
                prefix += " "
            prefix += "|- "
        return f"{prefix}{self.e} evalto {self.v}"
