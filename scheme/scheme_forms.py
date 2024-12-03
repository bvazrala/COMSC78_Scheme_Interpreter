from scheme_eval_apply import *
from scheme_utils import *
from scheme_classes import *
from scheme_builtins import *

#################
# Special Forms #
#################

# Each of the following do_xxx_form functions takes the cdr of a special form as
# its first argument—a Scheme list representing a special form without the
# initial identifying symbol (if, lambda, quote, ...). Its second argument is
# the environment in which the form is to be evaluated.

def do_define_form(expressions, env):
    """Evaluate a define form.

    >>> env = create_global_frame()
    >>> do_define_form(read_line("(x 2)"), env) # evaluating (define x 2)
    'x'
    >>> scheme_eval("x", env)
    2
    >>> do_define_form(read_line("(x (+ 2 8))"), env) # evaluating (define x (+ 2 8))
    'x'
    >>> scheme_eval("x", env)
    10
    >>> # problem 10
    >>> env = create_global_frame()
    >>> do_define_form(read_line("((f x) (+ x 8))"), env) # evaluating (define (f x) (+ x 8))
    'f'
    >>> scheme_eval(read_line("(f 3)"), env)
    11
    """
    validate_form(expressions, 2)  # At least two expressions
    signature = expressions.first
    if scheme_symbolp(signature):
        # (define x <expr>)
        validate_form(expressions, 2, 2)  # Exactly two expressions
        # BEGIN PROBLEM 4
        # evaluate the second expression to get the value
        value = scheme_eval(expressions.rest.first, env)
        # define the symbol in the current environment
        env.define(signature, value)
        # return the defined symbol
        return signature
        # END PROBLEM 4

    elif isinstance(signature, Pair) and scheme_symbolp(signature.first):
        # BEGIN PROBLEM 10
        # extract the function name from the signature
        func_name = signature.first
        # extract the formal parameters from the signature
        formals = signature.rest
        # extract the body of the lambda function
        body = expressions.rest
        # create a new lambda procedure with the given formals and body
        lambda_proc = LambdaProcedure(formals, body, env)
        # define the lambda procedure in the environment
        env.define(func_name, lambda_proc)
        # return the function name
        return func_name
        # END PROBLEM 10

    else:
        bad_signature = signature.first if isinstance(signature, Pair) else signature
        raise SchemeError('non-symbol: {0}'.format(bad_signature))

def do_quote_form(expressions, env):
    """Evaluate a quote form.

    >>> env = create_global_frame()
    >>> do_quote_form(read_line("((+ x 2))"), env) # evaluating (quote (+ x 2))
    Pair('+', Pair('x', Pair(2, nil)))
    """
    validate_form(expressions, 1, 1)  # Exactly one expression
    # BEGIN PROBLEM 5
    # simply return the first expression without evaluating it
    return expressions.first
    # END PROBLEM 5


def do_begin_form(expressions, env):
    """Evaluate a begin form.

    >>> env = create_global_frame()
    >>> x = do_begin_form(read_line("((print 2) 3)"), env) # evaluating (begin (print 2) 3)
    2
    >>> x
    3
    """
    validate_form(expressions, 1)
    result = None
    while expressions is not nil:
        exp = expressions.first
        result = scheme_eval(exp, env)
        expressions = expressions.rest
    return result

def do_lambda_form(expressions, env):
    """Evaluate a lambda form.

    >>> env = create_global_frame()
    >>> do_lambda_form(read_line("((x) (+ x 2))"), env) # evaluating (lambda (x) (+ x 2))
    LambdaProcedure(Pair('x', nil), Pair(Pair('+', Pair('x', Pair(2, nil))), nil), <Global Frame>)
    """
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    # BEGIN PROBLEM 7
    # the body of the lambda starts from the rest of the expressions
    body = expressions.rest
    # ensure that the body contains at least one expression
    validate_form(body, 1)  # At least one expression in body
    # return a new lambda procedure
    return LambdaProcedure(formals, body, env)
    # END PROBLEM 7


def do_if_form(expressions, env):
    """Evaluate an if form.

    >>> env = create_global_frame()
    >>> do_if_form(read_line("(#t (print 2) (print 3))"), env) # evaluating (if #t (print 2) (print 3))
    2
    >>> do_if_form(read_line("(#f (print 2) (print 3))"), env) # evaluating (if #f (print 2) (print 3))
    3
    """
    validate_form(expressions, 2, 3)  # 2 or 3 expressions
    test = scheme_eval(expressions.first, env)
    if is_scheme_true(test):
        consequent = expressions.rest.first
        return scheme_eval(consequent, env)
    elif len(expressions) == 3:
        alternative = expressions.rest.rest.first
        return scheme_eval(alternative, env)
    else:
        return None

def do_and_form(expressions, env):
    """Evaluate a (short-circuited) and form.

    >>> env = create_global_frame()
    >>> do_and_form(read_line("(#f (print 1))"), env) # evaluating (and #f (print 1))
    False
    >>> # evaluating (and (print 1) (print 2) (print 4) 3 #f)
    >>> do_and_form(read_line("((print 1) (print 2) (print 3) (print 4) 3 #f)"), env)
    1
    2
    3
    4
    False
    """
    # BEGIN PROBLEM 12
    # if no expressions, return True as default for 'and'
    if expressions is nil:
        return True
    result = True
    # evaluate each expression in turn
    while expressions is not nil:
        result = scheme_eval(expressions.first, env)
        # if any expression evaluates to false, short-circuit and return it
        if is_scheme_false(result):
            return result
        expressions = expressions.rest
    # if all expressions are true, return the last result
    return result
    # END PROBLEM 12


def do_or_form(expressions, env):
    """Evaluate a (short-circuited) or form.

    >>> env = create_global_frame()
    >>> do_or_form(read_line("(10 (print 1))"), env) # evaluating (or 10 (print 1))
    10
    >>> do_or_form(read_line("(#f 2 3 #t #f)"), env) # evaluating (or #f 2 3 #t #f)
    2
    >>> # evaluating (or (begin (print 1) #f) (begin (print 2) #f) 6 (begin (print 3) 7))
    >>> do_or_form(read_line("((begin (print 1) #f) (begin (print 2) #f) 6 (begin (print 3) 7))"), env)
    1
    2
    6
    """
    # BEGIN PROBLEM 12
    # if no expressions, return False as default for 'or'
    if expressions is nil:
        return False
    # evaluate each expression in turn
    while expressions is not nil:
        result = scheme_eval(expressions.first, env)
        # if any expression evaluates to true, short-circuit and return it
        if is_scheme_true(result):
            return result
        expressions = expressions.rest
    # if none are true, return False
    return False
    # END PROBLEM 12


def do_cond_form(expressions, env):
    """Evaluate a cond form.

    >>> do_cond_form(read_line("((#f (print 2)) (#t 3))"), create_global_frame())
    3
    """
    # BEGIN PROBLEM 13
    # iterate through each clause in the cond expression
    while expressions is not nil:
        clause = expressions.first
        # ensure each clause has at least one expression
        validate_form(clause, 1)
        test = clause.first
        # handle the special 'else' clause
        if test == 'else':
            # ensure 'else' is the last clause
            if expressions.rest != nil:
                raise SchemeError('else must be last')
            result_expressions = clause.rest
            # if 'else' has no expressions, return True
            if result_expressions is nil:
                return True
            else:
                return eval_all(result_expressions, env)
        else:
            # evaluate the test expression
            test_result = scheme_eval(test, env)
            # if the test is true, evaluate the rest of the clause
            if is_scheme_true(test_result):
                result_expressions = clause.rest
                if result_expressions is nil:
                    return test_result
                else:
                    return eval_all(result_expressions, env)
        expressions = expressions.rest
    # return None if no clause evaluates to true
    return None
    # END PROBLEM 13


def do_let_form(expressions, env):
    """Evaluate a let form.

    >>> env = create_global_frame()
    >>> do_let_form(read_line("(((x 2) (y 3)) (+ x y))"), env)
    5
    """
    validate_form(expressions, 2)
    bindings = expressions.first
    body = expressions.rest
    let_env = make_let_frame(bindings, env)
    return eval_all(body, let_env)

def make_let_frame(bindings, env):
    """Create a child frame of Frame ENV that contains the definitions given in
    BINDINGS. The Scheme list BINDINGS must have the form of a proper bindings
    list in a let expression: each item must be a list containing a symbol
    and a Scheme expression."""
    if not scheme_listp(bindings):
        raise SchemeError('bad bindings list in let form')
    names, values = nil, nil
    # BEGIN PROBLEM 14
    # iterate through each binding in the let expression
    current = bindings
    while current is not nil:
        binding = current.first
        # ensure each binding is a pair of a symbol and an expression
        validate_form(binding, 2, 2)
        symbol = binding.first
        expression = binding.rest.first
        # validate that the symbol is a valid variable name
        validate_formals(Pair(symbol, nil))
        # prepend the symbol and its evaluated value to their respective lists
        names = Pair(symbol, names)
        values = Pair(scheme_eval(expression, env), values)
        current = current.rest
    # create a new child frame with the bindings
    return env.make_child_frame(names, values)
    # END PROBLEM 14

    return env.make_child_frame(names, values)




def do_quasiquote_form(expressions, env):
    """Evaluate a quasiquote form."""
    def quasiquote_item(val, env, level):
        """Evaluate Scheme expression VAL that is nested at depth LEVEL in
        a quasiquote form in Frame ENV."""
        if not scheme_pairp(val):
            return val
        elif val.first == 'unquote':
            level -= 1
            if level == 0:
                validate_form(val.rest, 1, 1)
                return scheme_eval(val.rest.first, env)
        elif val.first == 'quasiquote':
            level += 1
        return val.map(lambda x: quasiquote_item(x, env, level))
    validate_form(expressions, 1, 1)
    return quasiquote_item(expressions.first, env, 1)

def do_unquote(expressions, env):
    raise SchemeError('unquote outside of quasiquote')

#################
# Dynamic Scope #
#################

def do_mu_form(expressions, env):
    """Evaluate a mu form."""
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    body = expressions.rest
    validate_form(body, 1)  # At least one expression in body
    return MuProcedure(formals, body)

SPECIAL_FORMS = {
    'and': do_and_form,
    'begin': do_begin_form,
    'cond': do_cond_form,
    'define': do_define_form,
    'if': do_if_form,
    'lambda': do_lambda_form,
    'let': do_let_form,
    'or': do_or_form,
    'quote': do_quote_form,
    'quasiquote': do_quasiquote_form,
    'unquote': do_unquote,
    'mu': do_mu_form,
}
