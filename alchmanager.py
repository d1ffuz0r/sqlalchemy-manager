"""
alchmanager
"""
__version__ = '0.0.1'
__author__ = 'Roman Gladkov'

from sqlalchemy.orm.query import Query
from sqlalchemy.ext.declarative.api import DeclarativeMeta

__all__ = ['ManagedQuery', 'ManagedSession']


not_doubleunder = lambda f: not f.startswith('__')


class ManagedQuery(Query):
    """Managed Query object"""
    def __init__(self, entities, *args, **kwargs):
        for entity in entities:
            if isinstance(entity, DeclarativeMeta):
                if hasattr(entity, 'Filters'):
                    manager_cls = entity.Filters
                    for fname in filter(not_doubleunder, dir(manager_cls)):
                        method = getattr(manager_cls, fname, None)
                        setattr(self, fname, lambda: method(self))
        super(ManagedQuery, self).__init__(entities, *args, **kwargs)


class ManagedSession(object):
    pass
