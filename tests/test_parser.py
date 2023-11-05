from type_project.ast import Let, Value, Plus, Var, Env
from type_project.parser import parser_expr, parser_environment


def test_let():
    pret = parser_expr("let x = 1 in x + 1")
    assert pret.error is None
    assert pret.remain == ""

    let_expr = pret.return_value

    assert let_expr == Let("x", 1, Plus(Var("x"), 1))


def test_environment():
    pret = parser_environment()("x= 3,y = 2")

    assert pret.error is None
    assert pret.remain == ""

    assert Env([("x", 3), ("y", 2)]) == pret.return_value
