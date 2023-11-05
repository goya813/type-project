from dataclasses import dataclass
from typing import Any


@dataclass
class Plus:
    e1: Any
    e2: Any


@dataclass
class Minus:
    e1: Any
    e2: Any

@dataclass
class Times:
    e1: Any
    e2: Any

@dataclass
class Lt:
    e1: Any
    e2: Any


@dataclass
class If:
    e1: Any
    e2: Any
    e3: Any


@dataclass
class Judgement:
    e: Any
    v: Any


Expr = Any
Value = int | bool

