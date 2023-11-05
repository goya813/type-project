from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Iterable, Callable, TypeVarTuple


class ErrorPlusErrorL(Exception):
    pass


class ErrorPlusBoolL(Exception):
    def __init__(self, e1: bool, e2: Any):
        self.e1 = e1
        self.e2 = e2


class ErrorPlusBoolR(Exception):
    def __init__(self, e1: Any, e2: bool):
        self.e1 = e1
        self.e2 = e2


class ErrorLtBoolL(Exception):
    def __init__(self, e1: bool, e2: Any):
        self.e1 = e1
        self.e2 = e2


class ErrorLtBoolR(Exception):
    def __init__(self, e1: Any, e2: bool):
        self.e1 = e1
        self.e2 = e2


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
class PlusBoolL:
    e1: bool
    e2: Any

    def __str__(self):
        return f"{'true' if self.e1 else 'false'} + {self.e2}"


@dataclass
class PlusBoolR:
    e1: Any
    e2: bool

    def __str__(self):
        return f"{self.e1} + {'true' if self.e2 else 'false'}"


@dataclass
class Judgement:
    e: Any
    v: Any


# Expr = If | Lt | Plus | Minus | Times | int | bool
Expr = Any
Value = int | bool


T = TypeVar("T")
V = TypeVar("V")
E = TypeVar("E")
T1 = TypeVar("T1")
E1 = TypeVar("E1")
T2 = TypeVar("T2")
E2 = TypeVar("E2")

@dataclass
class ParserResult(Generic[T, V, E]):
    return_value: V | None
    error: E | None
    remain: Iterable[T]

@dataclass
class StrParserResult(Generic[V, E]):
    return_value: V | None
    error: E | None
    remain: str


@dataclass
class TagParserError:
    tag: str

@dataclass
class TupleParserError:
    pass

StrParser = Callable[[str], StrParserResult[V, E]]

def tag(literal: str) -> StrParser[str, TagParserError]:
    def parser(s: str) -> StrParserResult[str, TagParserError]:
        if s.startswith(literal):
            return StrParserResult(literal, None, s[len(literal):])
        else:
            return StrParserResult(None, TagParserError(literal), s)
    return parser


# @overload
# def sequence[T1, E1](parsers: tuple[StrParser[T1, E1]]) -> StrParser[tuple[T1], TupleParserError]:
#     ...
#
#
# @overload
# def sequence[T1, E1, T2, E2](parsers: tuple[StrParser[T1, E1], StrParser[T2, E2]]) -> StrParser[tuple[T1, T2], TupleParserError]:
#     ...


Ts = TypeVarTuple("Ts")
Es = TypeVarTuple("Es")

def sequence(parsers: Any) -> StrParser[Any, TupleParserError]:
    def parser(s: str) -> StrParserResult[tuple[*Ts], TupleParserError]:
        result = []
        for p in parsers:
            r = p(s)
            if r.return_value is None:
                return StrParserResult(None, TupleParserError(), s)
            else:
                result.append(r.return_value)
                s = r.remain
        return StrParserResult(tuple[*Ts](result), None, s)
    return parser

@dataclass
class AltParserError:
    child_errors: list[Any]


def alt(parsers: tuple[StrParser[T1, E1]]) -> StrParser[T1, E1]:
    def parser(s: str) -> StrParserResult[T1, E1]:
        errs = []
        for p in parsers:
            ret = p(s)
            if ret.return_value is not None:
                return ret
            errs.append(ret.error)
        return StrParserResult(None, AltParserError(errs), s)
    return parser


def many0(parser: StrParser[T, E]) -> StrParser[list[T], E]:
    def new_parser(s: str) -> StrParserResult[list[T], E]:
        result = []
        while True:
            r = parser(s)
            if r.return_value is None:
                return StrParserResult(result, None, s)
            else:
                result.append(r.return_value)
                s = r.remain
    return new_parser


@dataclass
class TakeWhileError:
    pass


def take_while(cond: Callable[[str], bool]) -> StrParser[str, TakeWhileError]:
    def parser(s: str) -> StrParserResult[str, TakeWhileError]:
        l = s
        result = ""
        for i in range(len(s)):
            if cond(s[i]):
                result += s[i]
            else:
                break
        return StrParserResult(result, None, s[len(result):])
    return parser


def take_while_m_n(m: int, n: int, cond: Callable[[str], bool]) -> StrParser[str, TakeWhileError]:
    def parser(s: str) -> StrParserResult[str, TakeWhileError]:
        l = s
        result = ""
        for i in range(n):
            if len(s) == 0:
                break
            elif cond(s[0]):
                result += s[0]
                s = s[1:]
            else:
                break
        if len(result) < m:
            return StrParserResult(None, TakeWhileError(), l)
        else:
            return StrParserResult(result, None, s)
    return parser


def parser_map(parser: StrParser[T1, E], f: Callable[[T1], T2]) -> StrParser[T2, E]:
    def new_parser(s: str) -> StrParserResult[T2, E]:
        r = parser(s)
        if r.return_value is None:
            return StrParserResult(None, r.error, r.remain)
        else:
            return StrParserResult(f(r.return_value), None, r.remain)
    return new_parser


@dataclass
class MapExceptionError:
    exception: Exception


def parser_map_exception(parser: StrParser[T1, E1], f: Callable[[T1], T2]) -> StrParser[T2, MapExceptionError | E1]:
    def new_parser(s: str) -> StrParserResult[T2, MapExceptionError | E1]:
        r = parser(s)
        if r.return_value is None:
            return StrParserResult(None, r.error, r.remain)
        else:
            try:
                ret_val = f(r.return_value)
            except Exception as e:
                return StrParserResult(None, MapExceptionError(e), r.remain)
            return StrParserResult(ret_val, None, r.remain)
    return new_parser


def parser_int() -> StrParser[int, str]:
    return parser_map_exception(take_while(lambda c: c in "0123456789"), int)


def parser_bool() -> StrParser[bool, str]:
    return parser_map(alt([tag("true"), tag("false")]), lambda x: x == "true")


def parser_paren_expr() -> StrParser[Expr, str]:
    return parser_map_exception(skip_space_sequence((tag("("), parser_expr, tag(")"))), lambda x: x[1])


def parser_unary() -> StrParser[Expr, str]:
    return alt([
        parser_paren_expr(),
        parser_int(),
        parser_bool(),
    ])


def assoc_left(head: Expr, tail: list[tuple[str, Expr]]) -> Any:
    if len(tail) == 0:
        return head
    else:
        match tail[0]:
            case ("+", e2):
                return assoc_left(Plus(e1=head, e2=e2), tail[1:])
            case ("-", e2):
                return assoc_left(Minus(e1=head, e2=e2), tail[1:])
            case ("*", e2):
                return assoc_left(Times(e1=head, e2=e2), tail[1:])
            case ("<", e2):
                return assoc_left(Lt(e1=head, e2=e2), tail[1:])
            case _:
                raise Exception("unreachable")


def parser_times() -> StrParser[Times, str]:
    return parser_map(skip_space_sequence((parser_unary(), many0(skip_space_sequence((tag("*"), parser_unary()))))), lambda x: assoc_left(x[0], x[1]))


def parser_plus_minus() -> StrParser[list[Plus | Minus], str]:
    return parser_map(skip_space_sequence((parser_times(), many0(skip_space_sequence((tag("+"), parser_times()))))), lambda x: assoc_left(x[0], x[1]))


def parser_lt() -> StrParser[Lt, str]:
    return parser_map(skip_space_sequence((parser_plus_minus(), many0(skip_space_sequence((tag("<"), parser_plus_minus()))))), lambda x: assoc_left(x[0], x[1]))


def parser_if() -> StrParser[If, str]:
    return parser_map(
        skip_space_sequence((tag("if"), parser_expr, tag("then"), parser_expr, tag("else"), parser_expr), ),
        lambda x: If(e1=x[1], e2=x[3], e3=x[5])
    )


def skip_space_sequence(parsers: StrParser[Any, Any]) -> StrParser[Any, Any]:
    ret_parsers = []
    for p in parsers:
        ret_parsers.append(p)
        ret_parsers.append(take_while(lambda c: c in " \t\n"))
    return parser_map(sequence(tuple(ret_parsers)), lambda x: x[::2])


def parser_expr(s: str) -> StrParserResult[Expr, str]:
    return alt([
        parser_lt(),
        parser_if(),
    ])(s)


def is_int(x):
    return not isinstance(x, bool) and isinstance(x, int)


def solve_value(e: Expr) -> Value:
    match e:
        case Plus(e1, e2):
            v1 = solve_value(e1)
            v2 = solve_value(e2)
            v1_is_int = is_int(v1)
            v2_is_int = is_int(v2)

            if not v1_is_int:
                raise ErrorPlusBoolL(e1, e2)

            if not v2_is_int:
                raise ErrorPlusBoolR(e1, e2)

            return v1 + v2
        case Minus(e1, e2):
            v1 = solve_value(e1)
            v2 = solve_value(e2)
            v1_is_int = is_int(v1)
            v2_is_int = is_int(v2)
            match (v1_is_int, v2_is_int):
                case (True, True):
                    return v1 - v2
                case _:
                    raise Exception(f"evalto error")
        case Times(e1, e2):
            v1 = solve_value(e1)
            v2 = solve_value(e2)
            v1_is_int = is_int(v1)
            v2_is_int = is_int(v2)
            match (v1_is_int, v2_is_int):
                case (True, True):
                    return v1 * v2
                case _:
                    raise Exception(f"evalto error")
        case Lt(e1, e2):
            v1 = solve_value(e1)
            v2 = solve_value(e2)
            v1_is_int = is_int(v1)
            v2_is_int = is_int(v2)
            match (v1_is_int, v2_is_int):
                case (True, True):
                    return v1 < v2
                case (False, False):
                    raise ErrorLtBoolL(v1, v2)
                case (False, True):
                    raise ErrorLtBoolL(v1, v2)
                case (True, False):
                    raise ErrorLtBoolR(v1, v2)
                case _:
                    raise Exception(f"evalto error")
        case If(e1, e2, e3):
            if solve_value(e1):
                return solve_value(e2)
            else:
                return solve_value(e3)
        case int(x):
            return x
        case bool(x):
            return x


def solve(e: Expr) -> str:
    result = ""
    match e:
        case Plus(e1, e2):
            try:
                x1 = solve_value(e1)
            except ErrorPlusBoolR as e:
                result += f"{e1} + {e2} evalto error by E-PlusErrorL" + "{\n"
                result += f" {e1} evalto error by E-PlusBoolR" + "{\n"
                result += f"{e.e2} evalto {e.e2} by E-Bool" + "{};\n"
                result += "};\n"
                result += "};\n"
                return result

            try:
                x2 = solve_value(e2)
            except ErrorPlusBoolR:
                result += f"{e1} + {e2} evalto error \n"
                return result

            v = x1 + x2
            result += f"{e1} + {e2} evalto {v} by E-Plus" + "{\n"
            result += solve(e1)
            result += solve(e2)
            result += f" {x1} plus {x2} is {v} by B-Plus" + "{};\n"
            result += "};\n"

        case Minus(e1, e2):
            x1 = solve_value(e1)
            x2 = solve_value(e2)
            match (x1, x2):
                case (int(), int()):
                    v = x1 - x2
                    result += f"{e1} - {e2} evalto {v} by E-Minus" + "{\n"
                    result += solve(e1)
                    result += solve(e2)
                    result += f" {x1} minus {x2} is {v} by B-Minus" + "{};\n"
                    result += "};\n"
                case _:
                    result += f"{e1} - {e2} evalto error\n"
        case Times(e1, e2):
            x1 = solve_value(e1)
            x2 = solve_value(e2)
            match (x1, x2):
                case (int(), int()):
                    v = x1 * x2
                    result += f"{e1} * {e2} evalto {v} by E-Times" + "{\n"
                    result += solve(e1)
                    result += solve(e2)
                    result += f" {x1} times {x2} is {v} by B-Times" + "{};\n"
                    result += "};\n"
                case _:
                    result += f"{e1} * {e2} evalto error\n"
        case If(e1, e2, e3):
            x1 = solve_value(e1)
            is_bool = isinstance(x1, bool)
            if is_bool:
                if x1:
                    try:
                        x2 = solve_value(e2)
                        result += f"{e} evalto {x2} by E-IfT" + "{\n"
                        result += solve(e1)
                        result += solve(e2)
                    except:
                        result += f"{e} evalto error by E-IfTError" + "{\n"
                        result += solve(e1)
                        result += solve(e2)
                        result += "};\n"
                else:
                    try:
                        x3 = solve_value(e3)
                        result += f"{e} evalto {x3} by E-IfF" + "{\n"
                        result += solve(e1)
                        result += solve(e3)
                        result += "};\n"
                    except:
                        result += f"{e} evalto error by E-IfFError" + "{\n"
                        result += solve(e1)
                        result += solve(e3)
                        result += "};\n"
            else:
                result += f"{e} evalto error by E-IfInt" + "{\n"
                result += solve(e1)
                result += "};\n"
        case Lt(e1, e2):
            try:
                is_true = solve_value(e)
                v1 = solve_value(e1)
                v2 = solve_value(e2)
                if is_true:
                    result += f"{e1} < {e2} evalto true by E-Lt" + "{\n"
                    result += solve(e1)
                    result += solve(e2)
                    result += f" {v1} less than {v2} is true by B-Lt" + "{};\n"
                else:
                    result += f"{e1} < {e2} evalto false by E-Lt" + "{\n"
                    result += solve(e1)
                    result += solve(e2)
                    result += f" {v1} less than {v2} is false by B-Lt" + "{};\n"
                result += "};\n"
            except ErrorLtBoolL:
                result += f"{e1} < {e2} evalto error by E-LtBoolL" + "{\n"
                result += f"{e1} evalto {e1} by E-Bool" + "{};\n"
                result += "};\n"
            except ErrorLtBoolR:
                result += f"{e1} < {e2} evalto error by E-LtBoolR" + "{\n"
                result += f"{e2} evalto {e2} by E-Bool" + "{};\n"
                result += "};\n"
        case int(x):
            result += f"{x} evalto {x} by E-Int" + "{};\n"
        case bool(x):
            result += f"{x} evalto {x} by E-Bool" + "{};\n"

    return result


if __name__ == '__main__':
    # e = Plus(Plus(1, True), 2)
    # j = Judgement(e, "error")
    # e = Plus(Plus(3, If(Lt(-23, Times(-2, 8)), 8, 2)), 4)
    # j = Judgement(e, 15)
    # e = Times(Plus(4, 5), Minus(1, 10))
    # j = Judgement(e, -81)
    # e = Minus(Minus(8, 2), 3)
    # j = Judgement(e, 3)
    # e = If(Plus(2, 3), 1, 3)
    # j = Judgement(e, "error")
    # e = If(Plus(2, 3), 1, 3)
    # j = Judgement(e, "error")
    e = If(Lt(3, 4), Lt(1, True), Minus(3, False))
    j = Judgement(e, "error")
    """
    3 + if -23 < -2 * 8 then 8 else 2 + 4 evalto 11
    3 + (if -23 < -2 * 8 then 8 else 2) + 4 evalto 15
    1 + true + 2 evalto error
    """

    """
    8 - 2 - 3 evalto 3 by E-Minus {
     8 - 2 evalto 6 by E-Minus {
      8 evalto 8 by E-Int{};
      2 evalto 2 by E-Int{};
      8 minus 2 is 6 by B-Minus{}; 
     };
     3 evalto 3 by E-Int{};
     6 minus 3 is 3 by B-Minus{};
    };
    """
    """
    if 4 < 5 then 2 + 3 else 8 * 8 evalto 5 by E-IfT {
     4 < 5 evalto true by E-Lt {
      4 evalto 4 by E-Int{};
      5 evalto 5 by E-Int{};
      4 less than 5 is true by B-Lt{};
     };
     
    }
    """
    """
    1 + true + 2 evalto error by E-PlusErrorL {
     1 + true evalto error by E-PlusBoolR {
      true evalto true by E-Bool{};
     };
    };
    """
    result = solve(j.e)
    print(result.replace("True", "true").replace("False", "false"))
    # parsed_expr = parser_expr("if 2 + 3 then 1 else 3 evalto error")
    # result = solve(parsed_expr.return_value)

    # print(result.replace("True", "true").replace("False", "false"))
