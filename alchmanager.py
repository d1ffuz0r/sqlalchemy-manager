"""
alchmanager
"""
__version__ = '0.0.2'
__author__ = 'Roman Gladkov'

import types
import inspect
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative.api import DeclarativeMeta

__all__ = ['ManagedQuery', 'ManagedSession']

not_doubleunder = lambda name: not name.startswith('__')
not_under = lambda name: not name.startswith('_')


class ManagedQuery(Query):
    """Managed Query object"""

    def __init__(self, entities, *args, **kwargs):
        self.binds = {}
        entity = None

        if isinstance(entities, Mapper):
            entity = entities.entity
            if isinstance(entity, DeclarativeMeta):
                if hasattr(entity, '__manager__'):
                    manager_cls = entity.__manager__
                    for fname in filter(not_doubleunder, dir(manager_cls)):
                        fn = getattr(manager_cls, fname)
                        setattr(self, fname, types.MethodType(fn, self))

        if isinstance(entities, tuple) and len(entities):
            entity = entities[0]

        if entity and isinstance(entity, DeclarativeMeta):
            if hasattr(entity, '__manager__'):
                manager_cls = entity.__manager__
                for fname in filter(not_doubleunder, dir(manager_cls)):
                    fn = getattr(manager_cls, fname)

                    self.binds.update({fname: fn})
                    self.__rebind()

        super(ManagedQuery, self).__init__(entities, *args, **kwargs)

    def __getattribute__(self, name):
        """ Rebind function each function call

        :param name: str
        :return: any
        """
        returned = object.__getattribute__(self, name)

        if name != '_ManagedQuery__rebind' and \
                (inspect.isfunction(returned) or inspect.ismethod(returned)):
            # print('called ', returned.__name__)
            self.__rebind()
        return returned

    def __rebind(self):
        if len(self.binds):
            for fname, fn in self.binds.items():
                setattr(self, fname, types.MethodType(fn, self))


class ManagedSession(Session):

    def load_manager(self):
        def loader(manager_cls):
            for fname in filter(not_doubleunder, dir(manager_cls)):
                fn = getattr(manager_cls, fname)
                if not hasattr(self._query_cls, fname):
                    setattr(self._query_cls, fname, fn)
        return loader
