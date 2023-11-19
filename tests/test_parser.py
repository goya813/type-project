from type_project.ast import Let, Value, Plus, Var, Env, Judgement, Expr
from type_project.parser import parser_expr, parser_environment, parser_judge


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


def test_environment():
    pret = parser_environment()("x = 3, y = 2, z = true")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == Env([("x", 3), ("y", 2), ("z", True)])


def test_judge():
    pret = parser_judge()("x = 3, y = 2 |- 1 + 1 evalto 2")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == Judgement(Env([("x", 3), ("y", 2)]), Plus(1, 1), 2)
