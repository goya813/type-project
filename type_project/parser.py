from typing import Any, Callable, TypeVar
from nompy import (
    StrParser,
    MapExceptionError,
    StrParserResult,
    take_while,
    tag,
    parser_map,
    alt,
    sequence,
    many0,
    sequence2,
)

from type_project.ast import (
    Expr,
    If,
    Lt,
    Plus,
    Minus,
    Times,
    Let,
    Var,
    Env,
    Value,
    Judgement,
    Error,
    FunctionValue,
    FunctionEval,
    FunctionApply,
    LetRec,
)

from type_project.parser_utility import (
    terminated,
    opt,
    preceded,
    delimited,
    space0,
    wraped,
    space1,
)

T = TypeVar("T")
V = TypeVar("V")
E = TypeVar("E")
T1 = TypeVar("T1")
E1 = TypeVar("E1")
T2 = TypeVar("T2")
E2 = TypeVar("E2")


def parser_map_exception(
    parser: StrParser[T1, E1], f: Callable[[T1], T2]
) -> StrParser[T2, MapExceptionError | E1]:
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


def parser_error() -> StrParser[Error, str]:
    return parser_map(tag("error"), lambda x: Error())


def parser_paren_expr() -> StrParser[Expr, str]:
    return parser_map_exception(
        skip_space_sequence((tag("("), parser_expr, tag(")"))), lambda x: x[1]
    )


def parser_unary() -> StrParser[Expr, str]:
    return alt(
        [
            parser_paren_expr(),
            parser_int(),
            parser_bool(),
            parser_error(),
            parser_var(),
        ]
    )


def parser_value() -> StrParser[Value, str]:
    return alt(
        [
            parser_int(),
            parser_bool(),
        ]
    )


def parser_var() -> StrParser[Expr, str]:
    return parser_map(parser_name(), Var)


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
    return parser_map(
        skip_space_sequence(
            (parser_apply(), many0(skip_space_sequence((tag("*"), parser_apply()))))
        ),
        lambda x: assoc_left(x[0], x[1]),
    )


def parser_apply() -> StrParser[FunctionApply | Expr, str]:
    def f(x: tuple[Expr, list[Expr]]):
        ret = x[0]
        for l in x[1]:
            ret = FunctionApply(ret, l)
        return ret

    return parser_map(
        sequence(
            (
                parser_unary(),
                many0(
                    preceded(space1(), parser_unary()),
                ),
            )
        ),
        f,
    )


def parser_plus_minus() -> StrParser[list[Plus | Minus], str]:
    return parser_map(
        skip_space_sequence(
            (
                parser_times(),
                many0(skip_space_sequence((alt((tag("+"), tag("-"))), parser_times()))),
            )
        ),
        lambda x: assoc_left(x[0], x[1]),
    )


def parser_lt() -> StrParser[Lt, str]:
    return parser_map(
        skip_space_sequence(
            (
                parser_plus_minus(),
                many0(skip_space_sequence((tag("<"), parser_plus_minus()))),
            )
        ),
        lambda x: assoc_left(x[0], x[1]),
    )


def parser_if() -> StrParser[If, str]:
    return parser_map(
        skip_space_sequence(
            (
                tag("if"),
                parser_expr,
                tag("then"),
                parser_expr,
                tag("else"),
                parser_expr,
            ),
        ),
        lambda x: If(e1=x[1], e2=x[3], e3=x[5]),
    )


def parser_let() -> StrParser[Let, str]:
    return parser_map(
        skip_space_sequence(
            (tag("let"), parser_name(), tag("="), parser_expr, tag("in"), parser_expr)
        ),
        lambda x: Let(key=x[1], e1=x[3], e2=x[5]),
    )


def parser_letrec() -> StrParser[LetRec, str]:
    return parser_map(
        skip_space_sequence(
            (
                tag("let"),
                tag("rec"),
                parser_name(),
                tag("="),
                parser_expr,
                tag("in"),
                parser_expr,
            )
        ),
        lambda x: LetRec(key=x[2], e1=x[4], e2=x[6]),
    )


def parser_fun() -> StrParser[FunctionEval, str]:
    return parser_map(
        skip_space_sequence((tag("fun"), parser_name(), tag("->"), parser_expr)),
        lambda x: FunctionEval(x[1], x[3]),
    )


def skip_space_sequence(parsers: tuple[StrParser[Any, Any]]) -> StrParser[Any, Any]:
    ret_parsers = []
    for p in parsers:
        ret_parsers.append(p)
        ret_parsers.append(take_while(lambda c: c in " \t\n"))
    return parser_map(sequence(tuple(ret_parsers)), lambda x: x[::2])


def parser_expr(s: str) -> StrParserResult[Expr, str]:
    return alt(
        [
            parser_let(),
            parser_letrec(),
            parser_fun(),
            parser_if(),
            parser_lt(),
        ]
    )(s)


def parser_bind() -> StrParser[tuple[str, Value]]:
    return parser_map(
        skip_space_sequence((parser_name(), tag("="), parser_value())),
        lambda x: (x[0], x[2]),
    )


def parser_name() -> StrParser[str, str]:
    def is_not_keyword(s):
        if s in {"let", "if", "then", "else", "in", "evalto"}:
            raise ValueError
        if s == "":
            raise ValueError
        return s

    return parser_map_exception(take_while(str.isalnum), is_not_keyword)


def parser_environment() -> StrParser[Env, str]:
    def create_env(x):
        bind_head = x[0]

        env = Env([])
        if bind_head is not None:
            env = env.push(bind_head[0], bind_head[1])
        bind_tail = x[1]
        for b in bind_tail:
            env = env.push(b[0], b[1])
        return env

    return parser_map(
        skip_space_sequence(
            (
                opt(parser_bind()),
                many0(preceded(wraped(tag(","), space0()), parser_bind())),
            )
        ),
        create_env,
    )


def parser_judge() -> StrParser[Judgement]:
    def f(x):
        return Judgement(x[0], x[2], x[4])

    return parser_map(
        skip_space_sequence(
            (
                parser_environment(),
                tag("|-"),
                parser_expr,
                tag("evalto"),
                parser_value(),
            )
        ),
        f,
    )


if __name__ == "__main__":
    print(parser_expr("1+2"))
    print(parser_expr("if true then 1 else 2"))
    print(parser_expr("1 + 2 * 3"))
    print(parser_expr("1 * 2 + 3"))
    print(parser_expr("if 4 < 5 then 1 else 2"))
    print(parser_expr("if 4 < 5 + 1 then 1 else 2"))
    print(parser_expr("let x = 1 in x + 1"))
