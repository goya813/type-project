from type_project.ast import *
from type_project.parser import parser_expr

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Derivation:
    conclusion: Judgement
    rule: str
    premises: list["Derivation | str"]

    def val(self) -> Value:
        return self.conclusion.v


def infer(env: Env, e: Expr, v: Value = None) -> Derivation:
    def by(v: Value, rule: str, premises: list[Derivation | str]) -> Derivation:
        return Derivation(Judgement(env, e, v), rule, premises)

    def by_int2(
        fn: Callable[[int, int], Value], op: str, name: str, e1: Expr, e2: Expr
    ) -> Derivation:
        d1 = infer(env, e1)
        d2 = infer(env, e2)
        match (d1.val(), d2.val()):
            case (bool(), _):
                return by(Error(), f"E-{name}BoolL", [d1])
            case (Error(), _):
                return by(Error(), f"E-{name}ErrorL", [d1])
            case (_, bool()):
                return by(Error(), f"E-{name}BoolR", [d2])
            case (_, Error()):
                return by(Error(), f"E-{name}ErrorR", [d2])
            case (int(l), int(r)):
                v = fn(l, r)
                d3 = f"{l} {op} {r} is {v} by B-{name}" + "{}"
                return by(v, f"E-{name}", [d1, d2, d3])

    match e:
        case Var(e1):
            k, v = env.top()
            if e1 == k:
                return by(v, "E-Var1", [])
            else:
                d = infer(env.pop(), e)
                return by(d.val(), "E-Var2", [d])
        case Plus(e1, e2):
            return by_int2(lambda x, y: x + y, "plus", "Plus", e1, e2)
        case Minus(e1, e2):
            return by_int2(lambda x, y: x - y, "minus", "Minus", e1, e2)
        case Times(e1, e2):
            return by_int2(lambda x, y: x * y, "times", "Times", e1, e2)
        case Lt(e1, e2):
            return by_int2(lambda x, y: x < y, "less than", "Lt", e1, e2)
        case If(e1, e2, e3):
            d1 = infer(env, e1)
            match d1.val():
                case True:
                    d2 = infer(env, e2)
                    match d2.val():
                        case Error():
                            return by(Error(), "E-IfTError", [d1, d2])
                        case v:
                            return by(v, "E-IfT", [d1, d2])
                case False:
                    d3 = infer(env, e3)
                    match d3.val():
                        case Error():
                            return by(Error(), "E-IfFError", [d1, d3])
                        case v:
                            return by(v, "E-IfF", [d1, d3])
                case Error():
                    return by(Error(), "E-IfError", [d1])
                case int():
                    return by(Error(), "E-IfInt", [d1])

        case Let(key, e1, e2):
            d1 = infer(env, e1)
            d2 = infer(env.push(key, d1.val()), e2)
            return by(d2.val(), "E-Let", [d1, d2])
        case bool(x):
            return by(x, "E-Bool", [])
        case int(x):
            return by(x, "E-Int", [])
    raise Exception(env, e, v)


def pp(d: Derivation | str, depth=0) -> str:
    indent = "  " * depth
    if isinstance(d, str):
        return indent + d + ";"
    premises = "\n".join([pp(c, depth=depth + 1) for c in d.premises])
    body = "\n".join([" {", premises, indent + "}"]) if premises else "{}"
    return f"{indent}{d.conclusion} by {d.rule}{body};"


if __name__ == "__main__":
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

    env = Env([])
    e = Let(
        "x",
        Let("y", Minus(3, 2), Times(Var("y"), Var("y"))),
        Let("y", 4, Plus(Var("x"), Var("y"))),
    )
    # e = parser_expr("let x = let y = 3 - 2 in y * y in let y = 4 in x + y").return_value
    j = Judgement(env, e, 5)
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
    result = pp(infer(j.env, j.e, j.v))
    print(result.replace("True", "true").replace("False", "false"))
    # parsed_expr = parser_expr("if 2 + 3 then 1 else 3 evalto error")
    # result = solve(parsed_expr.return_value)

    # print(result.replace("True", "true").replace("False", "false"))
