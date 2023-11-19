from type_project.ast import (
    Let,
    Value,
    Plus,
    Var,
    Env,
    Judgement,
    Expr,
    FunctionEval,
    FunctionApply,
    FunctionValue,
    LetRec,
    Index,
)
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


def test_fun():
    pret = parser_expr("fun a -> 1")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == FunctionEval("a", 1)


def test_apply():
    pret = parser_expr("f 1")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == FunctionApply(Var("f"), 1)

    pret = parser_expr("f 1 2")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == FunctionApply(FunctionApply(Var("f"), 1), 2)

    pret = parser_expr("f 1 + 2")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == Plus(FunctionApply(Var("f"), 1), 2)


def test_let_rec():
    pret = parser_expr("let rec x = 1 in x")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == LetRec("x", 1, Var("x"))

    pret = parser_expr("let rec f = fun x -> x in f 1")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == LetRec(
        "f", FunctionEval("x", Var("x")), FunctionApply(Var("f"), 1)
    )


def test_nameless_form():
    pret = parser_expr("#2 + #1")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == Plus(Index(2), Index(1))

    pret = parser_expr("fun . -> #1")

    assert pret.error is None
    assert pret.remain == ""

    assert pret.return_value == FunctionEval(".", Index(1))
