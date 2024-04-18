class Michel:
    def __init__(self, name, address, parent):
        self.name=name
        self.address=address
        self.parent=parent

    def print(self):
        print(f'{self.name} - {self.address} - {self.parent}')


class_name = "Michel"
cls = globals()[class_name]  # Get the class from globals
instance = cls('michel', '18332 lake encino', 'papa')
instance.print()


    def __init__(self, polyglot, controller='hello_worldCtrl', address=
        'hello_worldCtrl', name='hello_world'):
        super().__init__(polyglot, controller, address, name)
        self.Parameters = Custom(polyglot, 'customparams')
        self.valid_configuration = False
        self.poly.subscribe(polyglot.START, self.start)
        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameter_handler)
        self.poly.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(polyglot.CONFIG, self.config)
        self.poly.ready()
        self.addAllNodes()