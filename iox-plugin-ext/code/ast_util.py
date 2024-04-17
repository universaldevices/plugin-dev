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
    
    valid_config = ast.Assign(
                targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='valid_configuration', ctx=ast.Store())],
                value=ast.Constant(value=False)
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

    return [assignment, valid_config] + method_calls

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

    #dFunction definition: def stop(self):
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

def astPollFunc():
    # LOGGER.info("short poll")
    log_short_poll = astLogger('info', 'Short poll ... ', False)
    log_long_poll = astLogger('info', 'Long poll ... ', False)

    # Elif 'longPoll' in polltype
    elif_long_poll = ast.If(
        test=ast.Compare(
            left=ast.Constant(value='longPoll'),
            ops=[ast.In()],
            comparators=[ast.Name(id='polltype', ctx=ast.Load())]
        ),
        body=[log_long_poll],
        orelse=[]
    )

    # If 'shortPoll' in polltype
    if_short_poll = ast.If(
        test=ast.Compare(
            left=ast.Constant(value='shortPoll'),
            ops=[ast.In()],
            comparators=[ast.Name(id='polltype', ctx=ast.Load())]
        ),
        body=[log_short_poll],
        orelse=[elif_long_poll]  # Elif is represented by an If in the orelse of the first If
    )

    # Function definition: def poll(polltype):
    function_def = ast.FunctionDef(
        name='poll',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='polltype')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=[if_short_poll],
        decorator_list=[],
        returns=None
    )

    return function_def

def astAddAllNodesFunc():
    # Method call: config = self.poly.getConfig()
    config_assignment = ast.Assign(
        targets=[ast.Name(id='config', ctx=ast.Store())],
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='poly',
                    ctx=ast.Load()),
                attr='getConfig',
                ctx=ast.Load()),
            args=[],
            keywords=[]
        )
    )

    # Check if config is None or config['nodes'] is None
    if_config = ast.If(
        test=ast.BoolOp(
            op=ast.Or(),
            values=[
                ast.Compare(
                    left=ast.Name(id='config', ctx=ast.Load()),
                    ops=[ast.Is()],
                    comparators=[ast.Constant(value=None)]
                ),
                ast.Compare(
                    left=ast.Subscript(
                        value=ast.Name(id='config', ctx=ast.Load()),
                        slice=ast.Index(value=ast.Str(s='nodes')),
                        ctx=ast.Load()
                    ),
                    ops=[ast.Is()],
                    comparators=[ast.Constant(value=None)]
                )
            ]
        ),
        body=[
            ast.Assign(
                targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='valid_configuration', ctx=ast.Store())],
                value=ast.Constant(value=True)
            ),
            ast.Return(value=None)
        ],
        orelse=[]
    )

    # For loop over config['nodes']
    for_loop = ast.For(
        target=ast.Name(id='node', ctx=ast.Store()),
        iter=ast.Subscript(
            value=ast.Name(id='config', ctx=ast.Load()),
            slice=ast.Index(value=ast.Str(s='nodes')),
            ctx=ast.Load()
        ),
        body=[
            ast.Assign(
                targets=[ast.Name(id='nodeDef', ctx=ast.Store())],
                value=ast.Subscript(
                    value=ast.Name(id='node', ctx=ast.Load()),
                    slice=ast.Index(value=ast.Str(s='nodeDefId')),
                    ctx=ast.Load()
                )
            ),
            ast.Assign(
                targets=[ast.Name(id='address', ctx=ast.Store())],
                value=ast.Subscript(
                    value=ast.Name(id='node', ctx=ast.Load()),
                    slice=ast.Index(value=ast.Str(s='address')),
                    ctx=ast.Load()
                )
            ),
            ast.Assign(
                targets=[ast.Name(id='primary', ctx=ast.Store())],
                value=ast.Subscript(
                    value=ast.Name(id='node', ctx=ast.Load()),
                    slice=ast.Index(value=ast.Str(s='primaryNode')),
                    ctx=ast.Load()
                )
            ),
            ast.Assign(
                targets=[ast.Name(id='name', ctx=ast.Store())],
                value=ast.Subscript(
                    value=ast.Name(id='node', ctx=ast.Load()),
                    slice=ast.Index(value=ast.Str(s='name')),
                    ctx=ast.Load()
                )
            ),
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),
                        attr='__addNode',
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id='nodeDef', ctx=ast.Load()),
                        ast.Name(id='address', ctx=ast.Load()),
                        ast.Name(id='name', ctx=ast.Load())
                    ],
                    keywords=[]
                )
            )
        ],
        orelse=[]
    )
    logger_info = astLogger('info', 'Done adding nodes ...', False)

    # Set self.valid_configuration = True
    set_valid_config = ast.Assign(
        targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='valid_configuration', ctx=ast.Store())],
        value=ast.Constant(value=True)
    )

    # Function definition: def addAllNodes(self):
    function_def = ast.FunctionDef(
        name='addAllNodes',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=[config_assignment, if_config, for_loop, logger_info, set_valid_config],
        decorator_list=[],
        returns=None
    )

    return function_def


import ast

def astAddNodeFunc():
    # Create nodes for function parameters with type annotations
    args = ast.arguments(
        posonlyargs=[],
        args=[
            ast.arg(arg='self'),
            ast.arg(arg='nodeDef', annotation=ast.Name(id='str', ctx=ast.Load())),
            ast.arg(arg='endDeviceAddress', annotation=ast.Name(id='str', ctx=ast.Load())),
            ast.arg(arg='devName', annotation=ast.Name(id='str', ctx=ast.Load())),
        ],
        kwonlyargs=[],
        kw_defaults=[],
        defaults=[]
    )

    # Check if nodeDef is None
    if_node_def_none = ast.If(
        test=ast.Compare(
            left=ast.Name(id='nodeDef', ctx=ast.Load()),
            ops=[ast.Is()],
            comparators=[ast.Constant(value=None)]
        ),
        body=[ast.Return(value=None)],
        orelse=[]
    )

    # Initialize devNode to None
    init_dev_node = ast.Assign(
        targets=[ast.Name(id='devNode', ctx=ast.Store())],
        value=ast.Constant(value=None)
    )

    # Check if devNode is None and log error
    if_dev_node_none = ast.If(
        test=ast.Compare(
            left=ast.Name(id='devNode', ctx=ast.Load()),
            ops=[ast.Is()],
            comparators=[ast.Constant(value=None)]
        ),
        body=[
            astLogger('error', 'invalid noddef id ...', False),
            ast.Return(value=None)
        ],
        orelse=[]
    )

    # Add devNode to poly
    add_node_call = ast.Expr(value=ast.Call(
        func=ast.Attribute(
            value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()),
            attr='addNode',
            ctx=ast.Load()
        ),
        args=[ast.Name(id='devNode', ctx=ast.Load())],
        keywords=[]
    ))

    # Function definition
    function_def = ast.FunctionDef(
        name='__addNode',
        args=args,
        body=[
            if_node_def_none,
            init_dev_node,
            if_dev_node_none,
            add_node_call
        ],
        decorator_list=[],
        returns=None
    )

    return function_def

