"""A Scheme interpreter and its read-eval-print loop."""

from scheme_builtins import *
from scheme_reader import *
from ucb import main, trace

##############
# Eval/Apply #
##############

def scheme_eval(expr, env, _=None): # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in environment ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    if scheme_symbolp(expr):
        return env.get(expr)
    elif scheme_atomp(expr) or expr is None:
        return expr
    elif not scheme_listp(expr):
        raise SchemeError('unable to parse expression {0}'.format(expr))
    else:
        first, rest = expr.first, expr.second
        if scheme_symbolp(first) and first in SPECIAL_FORM_IDENTIFIERS:
            form = SPECIAL_FORM_IDENTIFIERS[first]
            return form(rest, env)
        first = scheme_eval(first, env)
        if scheme_procedurep(first):
            rest_expr = rest.map(lambda exp: scheme_eval(exp, env))
            return scheme_apply(first, rest_expr, env)
        else:
            raise SchemeError('expr {0} of type {1} is not callable {2}'.format(expr, type(first), first))


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    environment ENV."""
    check_procedure(procedure)
    return procedure.apply(args, env)

def scheme_eval_list(exprs, env):
    """Evaluates each expression in list in order, then returns final expr"""
    if exprs is nil:
        return None
    while exprs.first is not nil:
        if exprs.second is not nil:
            scheme_eval(exprs.first, env)
            exprs = exprs.second
        else:
            return scheme_eval(exprs.first, env)


# Environments #
################

class Frame:
    """An environment frame binds Scheme symbols to Scheme values."""

    def __init__(self, parent):
        """An empty frame with parent frame PARENT (which may be None)."""
        self.parent = parent
        self.bindings = {}

    def __repr__(self):
        if self.parent is None:
            return '<Global Frame>'
        s = sorted(['{0}: {1}'.format(k, v) for k, v in self.bindings.items()])
        return '<{{{0}}} -> {1}>'.format(', '.join(s), repr(self.parent))

    def define(self, symbol, value):
        """Define Scheme SYMBOL to have VALUE."""

        self.bindings[symbol] = value

    # BEGIN PROBLEM 2/3
    def get(self, symbol):
        if symbol in self.bindings.keys():
            return self.bindings[symbol]
        elif self.parent:
                return self.parent.get(symbol)
        raise SchemeError('unknown identifier: {0}'.format(symbol))
    # END PROBLEM 2/3

    def new_child_frame(self, formals, values):
        if len(formals) == len(values):
            new_frame = Frame(self)
            while formals is not nil:
                new_frame.define(formals.first, values.first)
                formals, values = formals.second, values.second
            return new_frame
        else:
            raise SchemeError('invalid params in trying to create new frame')


##############
# Procedures #
##############

class Procedure:
    """The supertype of all Scheme procedures."""

def scheme_procedurep(x):
    return isinstance(x, Procedure)

class BuiltinProcedure(Procedure):
    """A Scheme procedure defined as a Python function."""

    def __init__(self, fn, use_env=False, name='builtin'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env):
        """Apply SELF to ARGS in ENV, where ARGS is a Scheme list.

        >>> env = create_global_frame()
        >>> plus = env.bindings['+']
        >>> twos = Pair(2, Pair(2, nil))
        >>> plus.apply(twos, env)
        4
        """
        # BEGIN PROBLEM 2
        py_args = []
        while args is not nil:
            py_args.append(args.first)
            args = args.second

        try:
            if not self.use_env:
                return self.fn(*py_args)
            else:
                return self.fn(*py_args, env)
        except:
            raise SchemeError('invalid parameters for function {0}'.format(self))
        # END PROBLEM 2

class UserProcedure(Procedure):
    "A procedure defined by the user"
    def apply(self, args, env):
        function_frame = self.create_call_frame(args, env)
        return scheme_eval_list(self.body, function_frame)

    def create_fn_subframe(self, args, env):
        """Creates and manages a subframe for the function, allowing us to bind
        the parameters to computable args, in a frame that is scoped separately and
        beneath parent frames"""
        subframe = env.new_child_frame(self.formals, args)
        return subframe

class LambdaProcedure(UserProcedure):
    """A procedure defined by a lambda expression or a define form."""

    def __init__(self, formals, body, env):
        """A procedure with formal parameter list FORMALS (a Scheme list),
        whose body is the Scheme list BODY, and whose parent environment
        starts with Frame ENV."""
        self.formals = formals
        self.body = body
        self.env = env

    def __str__(self):
        return str(Pair('lambda', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(
            repr(self.formals), repr(self.body), repr(self.env))

    def create_call_frame(self, args, env):
        """Creates and manages a subframe for the function, allowing us to bind
        the parameters to computable args, in a frame that is scoped separately and
        beneath parent frames"""
        # LambdaProcedure will use its own environment
        return UserProcedure.create_fn_subframe(self, args, self.env)


def add_builtins(frame, funcs_and_names):
    """Enter bindings in FUNCS_AND_NAMES into FRAME, an environment frame,
    as built-in procedures. Each item in FUNCS_AND_NAMES has the form
    (NAME, PYTHON-FUNCTION, INTERNAL-NAME)."""
    for name, fn, proc_name in funcs_and_names:
        frame.define(name, BuiltinProcedure(fn, name=proc_name))

#################
# Special Forms #
#################

"""
How you implement special forms is up to you. We recommend you encapsulate the
logic for each special form separately somehow, which you can do here.
"""

def eval_define_spform(expr, env):
    """Evalutes the 'define' special form"""
    check_form(expr, 2) #(define var expr) should have a length of 2
    key = expr.first
    if scheme_symbolp(key):
        val = scheme_eval(expr.second.first, env)
        env.define(key, val)
        return key
    elif isinstance(key, Pair):
        name = key.first
        formals = key.second
        body = expr.second

        check_formals(formals)
        env.define(name, LambdaProcedure(formals, body, env))
        return name
    else:
        raise SchemeError('non symbol {0}'.format(key))

def eval_quote_spform(expr, env):
    """Evaluates the 'quote' special form"""
    check_form(expr, 1, 1) #(quote expr) should have a min length of 1
    return expr.first      #returns the expr


def eval_quasiquote_spform(expr, env):
    "Evaluates quasiquotes as necessary"
    check_form(expr.first, 1) #(quasiquote expr) should have 1 parameter
    #keep track of position within quote-unquote hierarchy
    def eval_unquotes(exp, env, quote_hierarchy=1):
        if isinstance(exp, Pair):
            if exp.first == 'unquote':
                quote_hierarchy -= 1
                if quote_hierarchy == 0:
                    check_form(exp.second, 1) #evaluating the unquoted exp
                    return scheme_eval(exp.second.first, env)
            elif exp.first == 'quasiquote':
                quote_hierarchy += 1
            evaled_first = eval_unquotes(exp.first, env, quote_hierarchy)
            evaled_second = eval_unquotes(exp.second, env, quote_hierarchy)
            return Pair(evaled_first, evaled_second)
        else:
            return exp

    return eval_unquotes(expr.first, env)

def eval_unquote_spform(expr, env):
    """Defaults to throwing an error"""
    raise SchemeError('unexpected unquote {0}'.format(expr))

def eval_begin_spform(exprs, env):
    """Evaluates expressions in order, similar to scheme_eval_list"""
    #Allows for empty exprs, so no need to check form
    return scheme_eval_list(exprs, env)

def eval_lambda_spform(expr, env):
    """Evaluate an anonymous lambda function"""
    #Validate well-formed expr
    check_form(expr, 2)
    check_formals(expr.first)

    formal_params = expr.first
    body = expr.second
    return LambdaProcedure(formal_params, body, env)

def eval_if_spform(expr, env):
    """Evaluate a single conditional expression"""
    check_form(expr, 2, 3)
    condition = scheme_eval(expr.first, env)
    if scheme_truep(condition):
        return scheme_eval(expr.second.first, env)
    elif expr.second.second is not nil:
        return scheme_eval(expr.second.second.first, env)
    # return None

def eval_and_spform(expr, env):
    """Evaluate a set of 'and' expressions"""
    if expr is nil:
        return True

    while expr is not nil:
        evaled_expr = scheme_eval(expr.first, env)
        if scheme_truep(evaled_expr):
            if expr.second is nil:
                return evaled_expr
            expr = expr.second
        else:
            return False

def eval_or_spform(expr, env):
    """Evaluate a set of 'or' expressions"""
    if expr is nil:
        return False

    while expr is not nil:
        evaled_expr = scheme_eval(expr.first, env)
        if scheme_truep(evaled_expr):
            return evaled_expr
        else:
            if expr.second is nil:
                return False
            expr = expr.second


def eval_cond_spform(expr, env):
    """Evaluate conditional expressions"""
    while expr is not nil:
        conditional_statement = expr.first
        check_form(conditional_statement, 1)

        condition = conditional_statement.first
        body = conditional_statement.second

        if condition == 'else':
            evaluated_condition = True
            #Check to make sure else is last item
            if expr.second is not nil:
                raise SchemeError('else must be last condition')
        else:
            evaluated_condition = scheme_eval(condition, env)
        if scheme_truep(evaluated_condition):
            if body is not nil:
                return scheme_eval_list(body, env)
            return evaluated_condition
        expr = expr.second

def eval_let_spform(expr, env):
    """Evaluate a 'let' expression"""
    check_form(expr, 2)  #let should have formals defined and a body

    formals_expr = expr.first
    body = expr.second

    #creating expression frame from variable assignments
    if not scheme_listp(formals_expr):
        raise SchemeError('improper syntax for variable assignments')

    formals = nil
    args = nil

    while formals_expr is not nil:
        formal_expr = formals_expr.first
        check_form(formal_expr, 2, 2)

        formal = formal_expr.first
        val = scheme_eval(formal_expr.second.first, env)

        formals = Pair(formal, formals)
        args = Pair(val, args)

        formals_expr = formals_expr.second
    check_formals(formals)

    let_env = env.new_child_frame(formals, args)
    return scheme_eval_list(body, let_env)

def eval_mu_spform(expr, env):
    """Evaluate a 'mu' expression"""
    check_form(expr, 2)
    mu_formals = expr.first
    check_formals(mu_formals)

    body = expr.second
    return MuProcedure(mu_formals, body)

SPECIAL_FORM_IDENTIFIERS = {
    'define'    : eval_define_spform,
    'quote'     : eval_quote_spform,
    'quasiquote': eval_quasiquote_spform,
    'unquote'   : eval_unquote_spform,
    'begin'     : eval_begin_spform,
    'lambda'    : eval_lambda_spform,
    'if'        : eval_if_spform,
    'and'       : eval_and_spform,
    'or'        : eval_or_spform,
    'cond'      : eval_cond_spform,
    'let'       : eval_let_spform,
    'mu'        : eval_mu_spform
}

# Utility methods for checking the structure of Scheme programs

def check_form(expr, min, max=float('inf')):
    """Check EXPR is a proper list whose length is at least MIN and no more
    than MAX (default: no maximum). Raises a SchemeError if this is not the
    case.

    >>> check_form(read_line('(a b)'), 2)
    """
    if not scheme_listp(expr):
        raise SchemeError('badly formed expression: ' + repl_str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError('too few operands in form')
    elif length > max:
        raise SchemeError('too many operands in form')

def check_formals(formals):
    """Check that FORMALS is a valid parameter list, a Scheme list of symbols
    in which each symbol is distinct. Raise a SchemeError if the list of
    formals is not a well-formed list of symbols or if any symbol is repeated.

    >>> check_formals(read_line('(a b c)'))
    """
    symbols = set()
    def check_and_add(symbol):
        if not scheme_symbolp(symbol):
            raise SchemeError('non-symbol: {0}'.format(symbol))
        if symbol in symbols:
            raise SchemeError('duplicate symbol: {0}'.format(symbol))
        symbols.add(symbol)

    while isinstance(formals, Pair):
        check_and_add(formals.first)
        formals = formals.second

    if formals != nil:
        check_and_add(formals)

def check_procedure(procedure):
    """Check that PROCEDURE is a valid Scheme procedure."""
    if not scheme_procedurep(procedure):
        raise SchemeError('{0} is not callable: {1}'.format(
            type(procedure).__name__.lower(), repl_str(procedure)))

#################
# Dynamic Scope #
#################

class MuProcedure(UserProcedure):
    """A procedure defined by a mu expression, which has dynamic scope.
     _________________
    < Scheme is cool! >
     -----------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
    """

    def __init__(self, formals, body):
        """A procedure with formal parameter list FORMALS (a Scheme list) and
        Scheme list BODY as its definition."""
        self.formals = formals
        self.body = body


    def __str__(self):
        return str(Pair('mu', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'MuProcedure({0}, {1})'.format(
            repr(self.formals), repr(self.body))

    def create_call_frame(self, args, env):
        """Creates a frame that is dynamically scoped"""
        return env.new_child_frame(self.formals, args)



##################
# Tail Recursion #
##################

# Make classes/functions for creating tail recursive programs here?

def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not a Thunk.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the extra credit."""
    val = scheme_apply(procedure, args, env)
    # Add stuff here?
    return val



####################
# Extra Procedures #
####################

def scheme_map(fn, s, env):
    check_type(fn, scheme_procedurep, 0, 'map')
    check_type(s, scheme_listp, 1, 'map')
    return s.map(lambda x: complete_apply(fn, Pair(x, nil), env))

def scheme_filter(fn, s, env):
    check_type(fn, scheme_procedurep, 0, 'filter')
    check_type(s, scheme_listp, 1, 'filter')
    head, current = nil, nil
    while s is not nil:
        item, s = s.first, s.second
        if complete_apply(fn, Pair(item, nil), env):
            if head is nil:
                head = Pair(item, nil)
                current = head
            else:
                current.second = Pair(item, nil)
                current = current.second
    return head

def scheme_reduce(fn, s, env):
    check_type(fn, scheme_procedurep, 0, 'reduce')
    check_type(s, lambda x: x is not nil, 1, 'reduce')
    check_type(s, scheme_listp, 1, 'reduce')
    value, s = s.first, s.second
    while s is not nil:
        value = complete_apply(fn, scheme_list(value, s.first), env)
        s = s.second
    return value

################
# Input/Output #
################

def read_eval_print_loop(next_line, env, interactive=False, quiet=False,
                         startup=False, load_files=()):
    """Read and evaluate input until an end of file or keyboard interrupt."""
    if startup:
        for filename in load_files:
            scheme_load(filename, True, env)
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expression = scheme_read(src)
                result = scheme_eval(expression, env)
                if not quiet and result is not None:
                    print(repl_str(result))
        except (SchemeError, SyntaxError, ValueError, RuntimeError) as err:
            if (isinstance(err, RuntimeError) and
                'maximum recursion depth exceeded' not in getattr(err, 'args')[0]):
                raise
            elif isinstance(err, RuntimeError):
                print('Error: maximum recursion depth exceeded')
            else:
                print('Error:', err)
        except KeyboardInterrupt:  # <Control>-C
            if not startup:
                raise
            print()
            print('KeyboardInterrupt')
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            print()
            return

def scheme_load(*args):
    """Load a Scheme source file. ARGS should be of the form (SYM, ENV) or
    (SYM, QUIET, ENV). The file named SYM is loaded into environment ENV,
    with verbosity determined by QUIET (default true)."""
    if not (2 <= len(args) <= 3):
        expressions = args[:-1]
        raise SchemeError('"load" given incorrect number of arguments: '
                          '{0}'.format(len(expressions)))
    sym = args[0]
    quiet = args[1] if len(args) > 2 else True
    env = args[-1]
    if (scheme_stringp(sym)):
        sym = eval(sym)
    check_type(sym, scheme_symbolp, 0, 'load')
    with scheme_open(sym) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines,)
    def next_line():
        return buffer_lines(*args)

    read_eval_print_loop(next_line, env, quiet=quiet)

def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise an error."""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    env.define('eval',
               BuiltinProcedure(scheme_eval, True, 'eval'))
    env.define('apply',
               BuiltinProcedure(complete_apply, True, 'apply'))
    env.define('load',
               BuiltinProcedure(scheme_load, True, 'load'))
    env.define('procedure?',
               BuiltinProcedure(scheme_procedurep, False, 'procedure?'))
    env.define('map',
               BuiltinProcedure(scheme_map, True, 'map'))
    env.define('filter',
               BuiltinProcedure(scheme_filter, True, 'filter'))
    env.define('reduce',
               BuiltinProcedure(scheme_reduce, True, 'reduce'))
    env.define('undefined', None)
    add_builtins(env, BUILTINS)
    return env

@main
def run(*argv):
    import argparse
    parser = argparse.ArgumentParser(description='CS 61A Scheme Interpreter')
    parser.add_argument('-load', '-i', action='store_true',
                       help='run file interactively')
    parser.add_argument('file', nargs='?',
                        type=argparse.FileType('r'), default=None,
                        help='Scheme file to run')
    args = parser.parse_args()

    next_line = buffer_input
    interactive = True
    load_files = []

    if args.file is not None:
        if args.load:
            load_files.append(getattr(args.file, 'name'))
        else:
            lines = args.file.readlines()
            def next_line():
                return buffer_lines(lines)
            interactive = False

    read_eval_print_loop(next_line, create_global_frame(), startup=True,
                         interactive=interactive, load_files=load_files)
    tscheme_exitonclick()
