import ast

def astComment(comment):
    return None
    #return ast.Expr(value=ast.Constant(value=comment))

def astReturnBoolean(val:bool):
    # Create an AST node for 'return True'
    return ast.Return(
        value=ast.Constant(value=val)  # Using ast.Constant for Python 3.8 and later
    )


def astIndexAssignment(variable_name, param, command):
    return ast.Assign(
        targets=[ast.Name(id=variable_name, ctx=ast.Store())],  # The variable 'value' to assign to
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=command, ctx=ast.Load()),  # The dictionary 'command'
                attr='get',  # The 'get' method of dictionary
                ctx=ast.Load()
            ),
            args=[
                ast.Constant(value=param)  # Argument 'param' for the get method
            ],
            keywords=[]  # No keyword arguments
        )
    )

#level: error, info, debug, warning
def astLogger(level, message, add_exception=True):
    # Create an AST node for the LOGGER.error call with an f-string
    t_values=[
                ast.Str(s=message),  # Static part of the string
                ast.Str(s="Stopping "),
                ast.FormattedValue(
                    value=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),
                        attr='name',
                        ctx=ast.Load()
                    ),
                    conversion=-1,  # -1 indicates default string conversion
                    format_spec=None
                )
            ]

    if add_exception:
        values=[
            ast.Str(s=f"{message} :"),  # Static part of the string
            ast.FormattedValue(
            value=ast.Name(id='ex', ctx=ast.Load()),  # Dynamic part, variable ex
            conversion=-1,  # -1 means no conversion, 115 for str(), 114 for repr(), 97 for ascii()
            format_spec=None  # No specific format
        )
    ]

    logger = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='LOGGER', ctx=ast.Load()),  # LOGGER object
                attr=level,  # the level such as error, info, warning, etc. 
                ctx=ast.Load()
            ),
            args=[
                ast.JoinedStr(
                    values=t_values
#[
 #                       ast.Str(s=f"{message} :"),  # Static part of the string
 #                       ast.FormattedValue(
 #                           value=ast.Name(id='ex', ctx=ast.Load()),  # Dynamic part, variable ex
 #                           conversion=-1,  # -1 means no conversion, 115 for str(), 114 for repr(), 97 for ascii()
 #                           format_spec=None  # No specific format
 #                       )
 #                   ]
                )
            ],
            keywords=[]  # No keyword arguments
        )
    )
    return logger



#body and error are arrays of statements
def astTryExcept(body, error):
    # Try-Except block
    try_except = ast.Try(
        body=body,
        handlers=[
            ast.ExceptHandler(
                type=ast.Name(id='Exception', ctx=ast.Load()),
                name=ast.Name(id='ex', ctx=ast.Store()),
                body=error
            )
        ],
        orelse=[],
        finalbody=[]
    )

    return try_except


def astCommandQueryParams(command):
    # Nodes for the try block
    # Assignment: query = str(command['query']).replace("'", "\"")
    query_assign = ast.Assign(
        targets=[ast.Name(id='query', ctx=ast.Store())],
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Call(
                    func=ast.Name(id='str', ctx=ast.Load()),
                    args=[ast.Subscript(
                        value=ast.Name(id=command, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Constant(value='query')),
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                attr='replace',
                ctx=ast.Load()
            ),
            args=[ast.Constant(value="'"), ast.Constant(value='"')],
            keywords=[]
        )
    )

    # Assignment: jparam = json.loads(query)
    jparam_assign = ast.Assign(
        targets=[ast.Name(id='jparam', ctx=ast.Store())],
        value=ast.Call(
            func=ast.Attribute(value=ast.Name(id='json', ctx=ast.Load()), attr='loads', ctx=ast.Load()),
            args=[ast.Name(id='query', ctx=ast.Load())],
            keywords=[]
        )
    )

    return [query_assign, jparam_assign]

#toInt whether or not convert to int
def astCommandParamAssignment(param_uom, val_name, toInt=True):
    # Assignment: val = int(jparam['WCTRL.uom78'])
    if toInt:
        return ast.Assign(
        targets=[ast.Name(id=val_name, ctx=ast.Store())],
        value=ast.Call(
            func=ast.Name(id='int', ctx=ast.Load()),
            args=[ast.Subscript(
                value=ast.Name(id='jparam', ctx=ast.Load()),
                slice=ast.Index(value=ast.Constant(value=param_uom)),
                ctx=ast.Load()
                )],
                keywords=[]
            )
        )
    return ast.Assign(
        targets=[ast.Name(id=val_name, ctx=ast.Store())],  # Variable 
        value=ast.Subscript(
            value=ast.Name(id='jparam', ctx=ast.Load()),  # The dictionary 'jparam'
            slice=ast.Index(value=ast.Constant(value=param_uom)),  # Key 
            ctx=ast.Load()  # Context for the Subscript
        )
    )

def astControllerBody(): 
    # Create an AST node for the assignment to self.Parameters
    assignment = ast.Assign(
        targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='Parameters', ctx=ast.Store())],
        value=ast.Call(
            func=ast.Name(id='Custom', ctx=ast.Load()),
            args=[
                ast.Name(id='polyglot', ctx=ast.Load()),
                ast.Str(s='customparams')
            ],
            keywords=[]
        )
    )

    # Create a list to store method calls
    method_calls = []

    # Subscribing to various events
    events = ['START', 'CUSTOMPARAMS', 'POLL', 'STOP']
    methods = ['start', 'parameter_handler', 'poll', 'stop']
    for event, method in zip(events, methods):
        subscribe_call = ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()),
            args=[
                ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr=event, ctx=ast.Load()),
                ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=method, ctx=ast.Load())
            ],
            keywords=[]
        ))
        method_calls.append(subscribe_call)

    # Adding self.poly.ready() and self.addAllNodes() calls
    ready_call = ast.Expr(value=ast.Call(
        func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly.ready', ctx=ast.Load()),
        args=[],
        keywords=[]
    ))
    method_calls.append(ready_call)

    add_all_nodes_call = ast.Expr(value=ast.Call(
        func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='addAllNodes', ctx=ast.Load()),
        args=[],
        keywords=[]
    ))
    method_calls.append(add_all_nodes_call)

    return [assignment] + method_calls

def astParamHandlerFunc():
    # Create AST nodes for each statement in the function body
    clear_notices = ast.Expr(value=ast.Call(
    func=ast.Attribute(
            value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()),
            attr='Notices.clear',
            ctx=ast.Load()
    ),
    args=[],
    keywords=[]
    ))

    load_parameters = ast.Expr(value=ast.Call(
    func=ast.Attribute(
            value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='Parameters', ctx=ast.Load()),
            attr='load',
            ctx=ast.Load()
    ),
    args=[ast.Name(id='params', ctx=ast.Load())],
    keywords=[]
    ))

    return_true = ast.Return(value=ast.Constant(value=True))

    # Function definition
    function_def = ast.FunctionDef(
    name='parameter_handler',
    args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self'), ast.arg(arg='params')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
    ),
    body=[clear_notices, load_parameters, return_true],
    decorator_list=[],
    returns=None
    )
 
    return function_def

import ast

def astStartFunc():
    # Function body statements
    log_info = astLogger('info', 'Starting ... ', False)

    add_all_nodes = ast.Expr(value=ast.Call(
        func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='addAllNodes', ctx=ast.Load()),
        args=[],
        keywords=[]
    ))

    update_profile = ast.Expr(value=ast.Call(
        func=ast.Name(id='polyglot.updateProfile', ctx=ast.Load()),
        args=[],
        keywords=[]
    ))

    set_custom_params_doc = ast.Expr(value=ast.Call(
        func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly.setCustomParamsDoc', ctx=ast.Load()),
        args=[],
        keywords=[]
    ))

    return_true = astReturnBoolean(True)

    # Function definition
    function_def = ast.FunctionDef(
        name='start',
        args=ast.arguments(posonlyargs=[], args=[ast.arg(arg='self')], vararg=None, kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=[log_info, add_all_nodes, update_profile, set_custom_params_doc, return_true],
        decorator_list=[],
        returns=None
    )

    return function_def


import ast

def astStopFunc():
    # Function body: LOGGER.info(f"Stopping {self.name}")
    log_stop = astLogger('info', 'Stopping ... ', False)
    return_true = astReturnBoolean(True)

    # Function definition: def stop(self):
    function_def = ast.FunctionDef(
        name='stop',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=[log_stop, return_true],
        decorator_list=[],
        returns=None
    )

    return function_def

