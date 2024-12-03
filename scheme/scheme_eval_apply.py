import sys

from pair import *
from scheme_utils import *
from ucb import main, trace

import scheme_forms

##############
# Eval/Apply #
##############

def scheme_eval(expr, env, _=None):  # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # Evaluate atoms
    if scheme_symbolp(expr):
        return env.lookup(expr)
    elif self_evaluating(expr):
        return expr

    # All non-atomic expressions are lists (combinations)
    if not scheme_listp(expr):
        raise SchemeError('malformed list: {0}'.format(repl_str(expr)))
    first, rest = expr.first, expr.rest
    if scheme_symbolp(first) and first in scheme_forms.SPECIAL_FORMS:
        return scheme_forms.SPECIAL_FORMS[first](rest, env)
    else:
        # BEGIN PROBLEM 3
        # evaluate the first part of the expression to find the operator
        operator = scheme_eval(first, env) 
        # ensure that the operator is a valid procedure
        validate_procedure(operator)
        # evaluate the rest of the expressions (the operands)
        operands = rest.map(lambda operand: scheme_eval(operand, env))
        # apply the operator to the evaluated operands
        return scheme_apply(operator, operands, env)
        # END PROBLEM 3


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    validate_procedure(procedure)
    if not isinstance(env, Frame):
        assert False, "Not a Frame: {}".format(env)
    if isinstance(procedure, BuiltinProcedure):
        # BEGIN PROBLEM 2
        # convert the scheme list args to a python list
        py_args = []
        while isinstance(args, Pair):
            py_args.append(args.first)
            args = args.rest

        # if the procedure requires the environment, add it to the arguments
        if procedure.need_env:
            py_args.append(env)

        # try applying the procedure to the arguments
        try:
            return procedure.py_func(*py_args)
        # catch errors due to incorrect number of arguments
        except TypeError as e:
            raise SchemeError('incorrect number of arguments: {0}'.format(procedure))
        # END PROBLEM 2
    elif isinstance(procedure, LambdaProcedure):
        # BEGIN PROBLEM 9
        # create a new environment for the lambda procedure
        new_env = procedure.env.make_child_frame(procedure.formals, args)
        # evaluate the body of the lambda in the new environment
        return eval_all(procedure.body, new_env)
        # END PROBLEM 9
    elif isinstance(procedure, MuProcedure):
        # BEGIN PROBLEM 11
        # create a new environment with dynamic scope
        new_env = env.make_child_frame(procedure.formals, args)
        # evaluate the body of the mu procedure in the new environment
        return eval_all(procedure.body, new_env)
        # END PROBLEM 11
    else:
        assert False, "Unexpected procedure: {}".format(procedure)

def eval_all(expressions, env):
    """Evaluate each expression in the Scheme list EXPRESSIONS in
    Frame ENV (the current environment) and return the value of the last.

    >>> eval_all(read_line("(1)"), create_global_frame())
    1
    >>> eval_all(read_line("(1 2)"), create_global_frame())
    2
    >>> x = eval_all(read_line("((print 1) 2)"), create_global_frame())
    1
    >>> x
    2
    >>> eval_all(read_line("((define x 2) x)"), create_global_frame())
    2
    """
    # BEGIN PROBLEM 6
    # if there are no expressions, return None
    if expressions is nil:
        return None
    # iterate over the expressions, evaluating each one
    result = None
    while expressions is not nil:
        result = scheme_eval(expressions.first, env)
        expressions = expressions.rest
    # return the result of the last expression 
    return result
    # END PROBLEM 6


################################
# Extra Credit: Tail Recursion #
################################

class Unevaluated:
    """An expression and an environment in which it is to be evaluated."""

    def __init__(self, expr, env):
        """Expression EXPR to be evaluated in Frame ENV."""
        self.expr = expr
        self.env = env

def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not an Unevaluated."""
    validate_procedure(procedure)
    val = scheme_apply(procedure, args, env)
    if isinstance(val, Unevaluated):
        return scheme_eval(val.expr, val.env)
    else:
        return val

def optimize_tail_calls(unoptimized_scheme_eval):
    """Return a properly tail recursive version of an eval function."""
    def optimized_eval(expr, env, tail=False):
        """Evaluate Scheme expression EXPR in Frame ENV. If TAIL,
        return an Unevaluated containing an expression for further evaluation.
        """
        if tail and not scheme_symbolp(expr) and not self_evaluating(expr):
            return Unevaluated(expr, env)

        # BEGIN OPTIONAL PROBLEM 1
        while True:
            if scheme_symbolp(expr):
                return env.lookup(expr)
            elif self_evaluating(expr):
                return expr

            if not scheme_listp(expr):
                raise SchemeError('malformed list: {0}'.format(repl_str(expr)))

            first, rest = expr.first, expr.rest

            if scheme_symbolp(first) and first in scheme_forms.SPECIAL_FORMS:
                unevaluated = scheme_forms.SPECIAL_FORMS[first](rest, env)
            else:
                operator = scheme_eval(first, env)
                validate_procedure(operator)
                operands = rest.map(lambda operand: scheme_eval(operand, env))
                expr = operator.apply(operands, env)
                continue  # Tail call

            if tail:
                return Unevaluated(unevaluated, env)
            else:
                return unevaluated

        # END OPTIONAL PROBLEM 1


    return optimized_eval

################################################################
# Uncomment the following line to apply tail call optimization #
################################################################

# scheme_eval = optimize_tail_calls(scheme_eval)
