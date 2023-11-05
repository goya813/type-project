from type_project.ast import *


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
