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


def solve_value(e: Expr, env: Env) -> Value:
    match e:
        case Var(e1):
            return env.lookup(e1)
        case Plus(e1, e2):
            v1 = solve_value(e1, env)
            v2 = solve_value(e2, env)
            v1_is_int = is_int(v1)
            v2_is_int = is_int(v2)

            if not v1_is_int:
                raise ErrorPlusBoolL(e1, e2)

            if not v2_is_int:
                raise ErrorPlusBoolR(e1, e2)

            return v1 + v2
        case Minus(e1, e2):
            v1 = solve_value(e1, env)
            v2 = solve_value(e2, env)
            v1_is_int = is_int(v1)
            v2_is_int = is_int(v2)
            match (v1_is_int, v2_is_int):
                case (True, True):
                    return v1 - v2
                case _:
                    raise Exception(f"evalto error")
        case Times(e1, e2):
            v1 = solve_value(e1, env)
            v2 = solve_value(e2, env)
            v1_is_int = is_int(v1)
            v2_is_int = is_int(v2)
            match (v1_is_int, v2_is_int):
                case (True, True):
                    return v1 * v2
                case _:
                    raise Exception(f"evalto error")
        case Lt(e1, e2):
            v1 = solve_value(e1, env)
            v2 = solve_value(e2, env)
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
            if solve_value(e1, env):
                return solve_value(e2, env)
            else:
                return solve_value(e3, env)
        case int(x):
            return x
        case bool(x):
            return x


def generate_env_text(env: Env) -> str:
    if len(env.vars) == 0 or env.vars is None:
        return "|-"

    result = ""
    for k, v in env.vars[:-1]:
        result += f"{k} = {v}, "

    k, v = env.vars[-1]
    result += f"{k} = {v} |-"

    return result


def solve(e: Expr, env: Env) -> str:
    result = ""

    def append_result(s: str, e: Env, has_newline: bool = True, use_env: bool = True):
        nonlocal result
        if use_env:
            result += generate_env_text(e)
        result += s
        if has_newline:
            result += "\n"

    match e:
        case Var(e1):
            key, _ = env.vars[-1]
            value = env.lookup(e1)

            if e1 == key:
                append_result(f"{e1} evalto {value} by E-Var1" + "{};", env)
            else:
                append_result(f"{e1} evalto {value} by E-Var2" + "{", env)
                append_result(solve(e, env.pop()), env, use_env=False)
                append_result("};", env, use_env=False)

        case Plus(e1, e2):
            try:
                x1 = solve_value(e1, env)
            except ErrorPlusBoolR as e:
                append_result(f"{e1} + {e2} evalto error by E-PlusErrorL" + "{", env)
                append_result(f"{e1} + {e2} evalto error by E-PlusErrorL" + "{", env)
                append_result(f" {e1} evalto error by E-PlusBoolR" + "{", env)
                append_result(f"{e.e2} evalto {e.e2} by E-Bool" + "{};", env)
                append_result("};", env, use_env=False)
                append_result("};", env, use_env=False)
                return result

            try:
                x2 = solve_value(e2, env)
            except ErrorPlusBoolR:
                append_result(f"{e1} + {e2} evalto error ", env)
                return result

            v = x1 + x2
            append_result(f"{e1} + {e2} evalto {v} by E-Plus" + "{", env)
            append_result(solve(e1, env), env, use_env=False)
            append_result(solve(e2, env), env, use_env=False)
            append_result(f" {x1} plus {x2} is {v} by B-Plus" + "{};", env, use_env=False)
            append_result("};", env, use_env=False)

        case Minus(e1, e2):
            x1 = solve_value(e1, env)
            x2 = solve_value(e2, env)
            match (x1, x2):
                case (int(), int()):
                    v = x1 - x2
                    append_result(f"{e1} - {e2} evalto {v} by E-Minus" + "{", env)
                    append_result(solve(e1, env), env, use_env=False)
                    append_result(solve(e2, env), env, use_env=False)
                    append_result(f" {x1} minus {x2} is {v} by B-Minus" + "{};", env, use_env=False)
                    append_result("};", env, use_env=False)
                case _:
                    append_result(f"{e1} - {e2} evalto error", env)
        case Times(e1, e2):
            x1 = solve_value(e1, env)
            x2 = solve_value(e2, env)
            match (x1, x2):
                case (int(), int()):
                    v = x1 * x2
                    append_result(f"{e1} * {e2} evalto {v} by E-Times" + "{", env)
                    append_result(solve(e1, env), env, use_env=False)
                    append_result(solve(e2, env), env, use_env=False)
                    append_result(f" {x1} times {x2} is {v} by B-Times" + "{};", env, use_env=False)
                    append_result("};", env, use_env=False)
                case _:
                    append_result(f"{e1} * {e2} evalto error", env)
        case If(e1, e2, e3):
            x1 = solve_value(e1, env)
            is_bool = isinstance(x1, bool)
            if is_bool:
                if x1:
                    try:
                        x2 = solve_value(e2, env)
                        append_result(f"{e} evalto {x2} by E-IfT" + "{", env)
                        append_result(solve(e1, env), env, use_env=False)
                        append_result(solve(e2, env), env, use_env=False)
                        append_result("};", env, use_env=False)
                    except:
                        append_result(f"{e} evalto error by E-IfTError" + "{", env)
                        append_result(solve(e1, env), env, use_env=False)
                        append_result(solve(e2, env), env, use_env=False)
                        append_result("};", env, use_env=False)
                else:
                    try:
                        x3 = solve_value(e3, env)
                        append_result(f"{e} evalto {x3} by E-IfF" + "{", env)
                        append_result(solve(e1, env), env, use_env=False)
                        append_result(solve(e3, env), env, use_env=False)
                        append_result("};", env, use_env=False)
                    except:
                        append_result(f"{e} evalto error by E-IfFError" + "{", env)
                        append_result(solve(e1, env), env, use_env=False)
                        append_result(solve(e3, env), env, use_env=False)
                        append_result("};", env, use_env=False)
            else:
                append_result(f"{e} evalto error by E-IfInt" + "{", env)
                append_result(solve(e1, env), env, use_env=False)
                append_result("};", env, use_env=False)
        case Lt(e1, e2):
            try:
                is_true = solve_value(e, env)
                v1 = solve_value(e1, env)
                v2 = solve_value(e2, env)
                if is_true:
                    append_result(f"{e1} < {e2} evalto true by E-Lt" + "{", env)
                    append_result(solve(e1, env), env, use_env=False)
                    append_result(solve(e2, env), env, use_env=False)
                    append_result(f" {v1} less than {v2} is true by B-Lt" + "{};", env, use_env=False)
                else:
                    append_result(f"{e1} < {e2} evalto false by E-Lt" + "{", env)
                    append_result(solve(e1, env), env, use_env=False)
                    append_result(solve(e2, env), env, use_env=False)
                    append_result(f" {v1} less than {v2} is false by B-Lt" + "{};", env, use_env=False)
                append_result("};", env, use_env=False)
            except ErrorLtBoolL:
                append_result(f"{e1} < {e2} evalto error by E-LtBoolL" + "{\n", env)
                append_result(f"{e1} evalto {e1} by E-Bool" + "{};", env)
                append_result("};", env, use_env=False)
            except ErrorLtBoolR:
                append_result(f"{e1} < {e2} evalto error by E-LtBoolR" + "{", env)
                append_result(f"{e2} evalto {e2} by E-Bool" + "{};", env)
                append_result("};", env, use_env=False)
        case Let(key, e1, e2):
            v1 = solve_value(e1, env)
            env = env.push(key, v1)
            v2 = solve_value(e2, env)
            append_result(f"let {key} = {e1} in {e2} evalto error by E-LtBoolR" + "{", env)
            append_result(f"{e2} evalto {e2} by E-Bool" + "{};", env)
            append_result("};", env, use_env=False)
        case int(x):
            append_result(f"{x} evalto {x} by E-Int" + "{};", env)
        case bool(x):
            append_result(f"{x} evalto {x} by E-Bool" + "{};", env)

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

    env = Env([("x", True), ("y", 4)])
    e = If(Var("x"), Plus(Var("y"), 1), Minus(Var("y"), 1))
    j = Judgement(e, 5)
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
    result = solve(j.e, env)
    print(result.replace("True", "true").replace("False", "false"))
    # parsed_expr = parser_expr("if 2 + 3 then 1 else 3 evalto error")
    # result = solve(parsed_expr.return_value)

    # print(result.replace("True", "true").replace("False", "false"))
