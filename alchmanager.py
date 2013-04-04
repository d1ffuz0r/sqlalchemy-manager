"""
alchmanager
"""
__version__ = '0.0.2'
__author__ = 'Roman Gladkov'
import types
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative.api import DeclarativeMeta

__all__ = ['ManagedQuery', 'ManagedSession']

not_doubleunder = lambda name: not name.startswith('__')


class ManagedQuery(Query):
    """Managed Query object"""

    def __init__(self, entities, *args, **kwargs):
        entity = entities[0]
        if isinstance(entity, DeclarativeMeta):
            if hasattr(entity, '__manager__'):
                manager_cls = entity.__manager__
                for fname in filter(not_doubleunder, dir(manager_cls)):
                    fn = getattr(manager_cls, fname)
                    setattr(self, fname, types.MethodType(fn, self))
        super(ManagedQuery, self).__init__(entities, *args, **kwargs)


class ManagedSession(Session):

    def load_manager(self):
        def loader(manager_cls):
            for fname in filter(not_doubleunder, dir(manager_cls)):
                fn = getattr(manager_cls, fname)
                if not hasattr(self._query_cls, fname):
                    setattr(self._query_cls, fname, fn)
        return loader
