from type_project.ast import Let, Value, Plus, Var
from type_project.parser import parser_expr


def test_let():
    pret = parser_expr("let x = 1 in x + 1")
    assert pret.error is None
    assert pret.remain == ""

    let_expr = pret.return_value

    assert let_expr == Let("x", 1, Plus(Var("x"), 1))


def test_nested_let():
    pret = parser_expr("let x = let y = 3 - 2 in y * y in let y = 4 in x + y")
    assert pret.error is None
    assert pret.remain == ""

    print(pret)
