from nompy import (
    StrParser,
    parser_map,
    sequence2,
    StrParserResult,
    take_while,
    sequence,
)


def terminated(first: StrParser, second: StrParser) -> StrParser:
    return parser_map(sequence2((first, second)), lambda x: x[0])


def preceded(first: StrParser, second: StrParser) -> StrParser:
    return parser_map(sequence2((first, second)), lambda x: x[1])


def delimited(first: StrParser, second: StrParser, third: StrParser) -> StrParser:
    return parser_map(sequence((first, second, third)), lambda x: x[1])


def wraped(target: StrParser, wrap: StrParser) -> StrParser:
    return delimited(wrap, target, wrap)


def opt[V, E](parser: StrParser[V, E]) -> StrParser[V, E]:
    def new_parser(s: str) -> StrParserResult:
        res = parser(s)
        if res.error is not None:
            return StrParserResult(return_value=None, error=None, remain=s)
        return res

    return new_parser


def space() -> StrParser:
    return take_while(lambda c: c in " \t\n")
