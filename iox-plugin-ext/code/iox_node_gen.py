
import ast
from nodedef import NodeDefDetails, NodeProperties
from log import LOGGER

class IoXNodeGen():
    def __init__(self, nodedef:NodeDefDetails, path:str):
        if nodedef == None or path == None:
            LOGGER.critical("need node def and the path to save the python file")
            raise Exception ("need node def and the path to save the python file")

        self.nodedef = nodedef
        self.path = path

    def create_node_class(self ):
        # Create the class for the node 
        class_def = ast.ClassDef(
            name=f'{self.nodedef.name}',
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
        
        # Add the drivers list
        commands_list = ast.Assign(
            targets=[ast.Name(id='commands', ctx=ast.Store())],
            value=ast.List(elts=[
                    ast.Dict(
                        keys=[ast.Str(s='id'), ast.Str(s='name')],
                        values=[ast.Str(s=command['id']), ast.Str(s=command['name'])]
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

        # Add updateInfo method
        update_info_method = ast.FunctionDef(
            name='updateInfo',
            args=ast.arguments(
                args=[ast.arg(arg='self'), ast.arg(arg='payload'), ast.arg(arg='topic', annotation=ast.Name(id='str', ctx=ast.Load()))],
                defaults=[],
                kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
            ),
            body=[],
            decorator_list=[]
        )
        class_def.body.append(update_info_method)

        # Add other methods and command dictionary similar to updateInfo
        # For brevity, those parts are skipped. You can add them similarly.

        # Print the AST dump to verify
        print(ast.dump(class_def, indent=4))

        return class_def