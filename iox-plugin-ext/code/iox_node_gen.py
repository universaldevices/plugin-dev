
import ast
from nodedef import NodeDefDetails, NodeProperties
from commands import CommandDetails, CommandParam
from log import LOGGER
from validator import getValidName
from ast_util import astReturnBoolean, astIndexAssignment, astCommandParamAssignment, astTryExcept, astLogger, astCommandQueryParams, astComment
from uom import UOMs
from editor import Editors

class IoXNodeGen():
    def __init__(self, nodedef:NodeDefDetails, path:str):
        if nodedef == None or path == None:
            LOGGER.critical("need node def and the path to save the python file")
            raise Exception ("need node def and the path to save the python file")

        self.nodedef = nodedef
        self.path = path


    def create_imports(self):
        import_node = ast.Import(
            names=[
                ast.alias(name='udi_interface', asname=None),
                ast.alias(name='os', asname=None),
                ast.alias(name='sys', asname=None),
                ast.alias(name='json', asname=None),
                ast.alias(name='time', asname=None)
            ]
        )
        return import_node 

    
    def create_globals(self):
        # AST node for 'LOGGER = udi_interface.LOGGER'
        assign_LOGGER = ast.Assign(
        targets=[ast.Name(id='LOGGER', ctx=ast.Store())],
        value=ast.Attribute(
            value=ast.Name(id='udi_interface', ctx=ast.Load()),
            attr='LOGGER',
            ctx=ast.Load()
            )
        )

        # AST node for 'Custom = udi_interface.Custom'
        assign_Custom = ast.Assign(
        targets=[ast.Name(id='Custom', ctx=ast.Store())],
        value=ast.Attribute(
            value=ast.Name(id='udi_interface', ctx=ast.Load()),
            attr='Custom',
            ctx=ast.Load()
            )
        )

        return [assign_LOGGER, assign_Custom]

    def create_command_body(self, command:CommandDetails):
        if command == None:
            return None
        
        if not command.hasParams():
            return astReturnBoolean(True)
        
        out = []
        error = []

        added_jparams=False

        params = command.getParams()
        for p in params:
            param = params[p] 
            editor = Editors.getEditors().editors[param.editor.getEditorId()]
            if UOMs.isIndex(editor.uom):
                out.append(astIndexAssignment(param.name.replace(' ','_') if param.name else param.id, param.id, 'command'))
            else:
                if not added_jparams:
                    stmts = astCommandQueryParams('command')
                    for stmt in stmts:
                        out.append(stmt)
                    added_jparams=True
                
                out.append(astCommandParamAssignment(f'{param.id}.uom{editor.uom}', param.id))

        out.append(astReturnBoolean(True))

        error.append(astLogger("error", "failed parsing parameters ... "))
        error.append(astReturnBoolean(False))

        return astTryExcept(out, error)
        

    def create_node_class(self ):
        # Create the class for the node 
        class_def = ast.ClassDef(
            name=f'{self.nodedef.name}Node',
            bases=[ast.Attribute(value=ast.Name(id='udi_interface', ctx=ast.Load()), attr='Node', ctx=ast.Load())],
            keywords=[],
            body=[],
            decorator_list=[]
        )

        # Add class-level attributes
        class_def.body.append(ast.Assign(
            targets=[ast.Name(id='id', ctx=ast.Store())],
            value=ast.Str(s=f"{self.nodedef.id}")
        ))

        try:
            drivers = self.nodedef.properties.getPG3Drivers()
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

        class_def.body.append(astComment('This is a list of properties that were defined in the nodedef'))

        # Add the drivers list
        drivers_list = ast.Assign(
            targets=[ast.Name(id='drivers', ctx=ast.Store())],
            value=ast.List(elts=[
                    ast.Dict(
                        keys=[ast.Str(s='driver'), ast.Str(s='value'), ast.Str(s='uom'), ast.Str(s='name')],
                        values=[ast.Str(s=driver['driver']), ast.Str(s=driver['value']), ast.Num(n=driver['uom']), ast.Str(s=driver['name'])]
                    ) for driver in drivers
            ], ctx=ast.Load())
        )

        class_def.body.append(drivers_list)

        try:
            commands = self.nodedef.getPG3Commands()
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise
        
        class_def.body.append(astComment('This is a list of commands that were defined in the nodedef'))
        # Add the drivers list
        commands_list = ast.Assign(
            targets=[ast.Name(id='commands', ctx=ast.Store())],
            value=ast.List(elts=[
                    ast.Dict(
                        keys=[ast.Str(s=f"{command['id']}")],
                        values=[ast.Name(id=f"{getValidName(command['name'],False)}", ctx=ast.Load())]
                    ) for command in commands
            ], ctx=ast.Load())
        )

        class_def.body.append(commands_list)

        # Add __init__ method
        init_method = ast.FunctionDef(
            name='__init__',
            args=ast.arguments(
                args=[ast.arg(arg='self'), ast.arg(arg='poly'), ast.arg(arg='controller'), ast.arg(arg='address'), ast.arg(arg='name')],
                defaults=[
                     ast.Str(self.nodedef.parent if self.nodedef.parent else self.nodedef.id),  ast.Str(s=self.nodedef.id),  ast.Str(s=self.nodedef.name)],
                kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
            ),
            body=[ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='super', ctx=ast.Load()), attr='__init__', ctx=ast.Load()),
                                       args=[ast.Name(id='self'), ast.Name(id='poly'), ast.Name(id='controller'), ast.Name(id='address'), ast.Name(id='name')],
                                       keywords=[]))],
            decorator_list=[]
        )

        class_def.body.append(init_method)

        #create update and get methods

        for driver in drivers:
            set_driver_call=ast.Call(
                        func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),  # 'self' object
                        attr='setDriver',  # Method name 'setDriver'
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id=f"\"{driver['driver']}\"", ctx=ast.Load()),  # First, driver id
                        ast.Name(id='value', ctx=ast.Load()),        # Second, value
                        ast.Name(id=f"{driver['uom']}", ctx=ast.Load()) ,    # Third uom
                        ast.Name(id='force', ctx=ast.Load())          # Whether or not to force update/boolean
                    ],
                    keywords=[],
                    decorator_list=[]
                )
            return_stmt = ast.Return( value=set_driver_call)  # Return the result of update 
            method = ast.FunctionDef(
            name=f"update{getValidName(driver['name'])}",
            args=ast.arguments(
                args=[ast.arg(arg='self'), ast.arg(arg='value'), ast.arg(arg='force', annotation=ast.Name(id='bool', ctx=ast.Load()))],
                defaults=[],
                kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
            ),
            body=[
                return_stmt
            ],
            keywords=[],
            decorator_list=[]
            )
            class_def.body.append(astComment(f"Use this method to update {getValidName(driver['name'])} in IoX"))
            class_def.body.append(method)

            ## Now getDriver
            get_driver_call=ast.Call(
                        func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),  # 'self' object
                        attr='getDriver',  # Method name 'getDriver'
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id=f"\"{driver['driver']}\"", ctx=ast.Load())  # First, driver id
                    ],
                    keywords=[],
                    decorator_list=[]
                )
            return_stmt = ast.Return( value=get_driver_call)  # Return the result of update 
            method = ast.FunctionDef(
            name=f"get{getValidName(driver['name'])}",
            args=ast.arguments(
                args=[ast.arg(arg='self')],
                defaults=[],
                kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
            ),
            body=[
                return_stmt
            ],
            keywords=[],
            decorator_list=[]
            )
            class_def.body.append(method)

        #now make the commands
        for command in commands:
            '''
            set_driver_call=ast.Call(
                        func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),  # 'self' object
                        attr='setDriver',  # Method name 'setDriver'
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id=f"\"{driver['driver']}\"", ctx=ast.Load()),  # First, driver id
                        ast.Name(id='value', ctx=ast.Load()),        # Second, value
                        ast.Name(id=f"{driver['uom']}", ctx=ast.Load()) ,    # Third uom
                        ast.Name(id='force', ctx=ast.Load())          # Whether or not to force update/boolean
                    ],
                    keywords=[],
                    decorator_list=[]
                )
            return_stmt = ast.Return( value=set_driver_call)  # Return the result of update 
            '''
            cmd = self.nodedef.commands.acceptCommands[command['id']]
            pass_stmt = ast.Pass()
            method = ast.FunctionDef(
                name=getValidName(command['name'],False),
                args=ast.arguments(
                    args=[ast.arg(arg='self'), ast.arg(arg='command')],
                    defaults=[],
                    kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
                ),
                body=[
            #        pass_stmt
                     self.create_command_body(cmd)
                ],
                keywords=[],
                decorator_list=[]
            )
            class_def.body.append(method)

        # Print the AST dump to verify
        print(ast.dump(class_def, indent=4))

        return class_def

    