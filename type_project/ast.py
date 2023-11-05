from dataclasses import dataclass
from typing import Any


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
    name: str
    e1: Any
    e2: Any

    def __str__(self):
        return f"let {self.name} = {self.e1} in {self.e2}"


@dataclass
class Judgement:
    e: Any
    v: Any


Expr = Any
Value = int | bool

