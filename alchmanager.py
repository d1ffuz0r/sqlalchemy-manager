"""
alchmanager
"""
__version__ = '0.0.1'
__author__ = 'Roman Gladkov'

from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative.api import DeclarativeMeta

__all__ = ['ManagedQuery', 'ManagedSession']

not_doubleunder = lambda name: not name.startswith('__')


class ManagedQuery(Query):
    """Managed Query object"""

    def __init__(self, entities, *args, **kwargs):
        for entity in entities:
            if isinstance(entity, DeclarativeMeta):
                if hasattr(entity, '__manager__'):
                    manager_cls = entity.__manager__
                    for fname in filter(not_doubleunder, dir(manager_cls)):
                        fn = getattr(manager_cls, fname)
                        setattr(self.__class__, fname, fn)
        super(ManagedQuery, self).__init__(entities, *args, **kwargs)


class ManagedSession(Session):

    methods = {}

    def load_manager(self):
        def loader(manager_cls):
            for fname in filter(not_doubleunder, dir(manager_cls)):
                method = getattr(manager_cls, fname, None)
                self.methods[fname] = method
        return loader

    def query(self, *entities, **kwargs):
        """Return a new ``Query`` object corresponding to this ``Session``."""
        query = self._query_cls(entities, self, **kwargs)
        for fname, fn in self.methods.items():
            if not hasattr(query, fname):
                setattr(query.__class__, fname, fn)
        return query
