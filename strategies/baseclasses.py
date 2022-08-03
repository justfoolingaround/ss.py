class StrategiserMeta(type):
    def __new__(
        cls,
        name,
        bases,
        attrs,
        setter,
        accessor=(lambda _: _),
        combinable=False,
        strategy=None,
    ):

        return_class = super().__new__(cls, name, bases, attrs)

        return_class.accessor = staticmethod(accessor)
        return_class.combinable = combinable
        return_class.setter = staticmethod(setter)
        return_class.strategy = staticmethod(strategy)

        return return_class


class Strategiser:
    def __init__(self, session):
        self.session = session

    def execute(self):

        retval = self.strategy(self.accessor(self.session))

        if retval is not None:
            self.setter(self.session, retval)


class StrategyException(Exception):
    pass
