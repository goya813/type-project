from nompy import StrParser, parser_map, sequence2, StrParserResult


def terminated(first: StrParser, second: StrParser) -> StrParser:
    return parser_map(sequence2((first, second)), lambda x: x[0])


def preceded(first: StrParser, second: StrParser) -> StrParser:
    return parser_map(sequence2((first, second)), lambda x: x[1])


class Empty:
    pass


def opt[V, E](parser: StrParser[V, E]) -> StrParser[V, E]:
    def new_parser(s: str) -> StrParserResult:
        res = parser(s)
        if res.error is not None:
            return StrParserResult(return_value=None, error=None, remain=s)
        return res

    return new_parser
