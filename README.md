#Managers for SQLAlchemy.

Manager for model, methods added in runtime to query.

## Installation

```
$ git clone https://github.com/d1ffuz0r/sqlalchemy-manager.git
$ cd sqlalchemy-manager
$ python setup.py install
```

## Documentation


### alchmanager.ManagedQuery
----------------------------

Manager for Query.

#### Example

```python
from sqlalchemy.orm import sessionmaker

from alchmanager import ManagedQuery, ManagedSession


engine = create_engine('sqlite:///:memory:')
session = sessionmaker(query_cls=ManagedQuery,
        	           bind=engine)()
Base = declarative_base()

class MainManager:

    @staticmethod
	def is_index(self):
    	return self.filter_by(is_index=True)

	@staticmethod
    def is_public(self):
        return self.filter_by(is_public=True)

class Test(Base):
	id = Column(Integer, primary_key=True)
    is_public = Column(Boolean, default=False)
    is_index = Column(Boolean)

    __manager__ = MainManager

session.query(Video).is_index().filter_by(id=1).is_public()
```

### alchmanager.ManagedSession
------------------------------

Manager for Session. Decorator `load_manager()` for register methods into session.

##### Example

```python
from sqlalchemy.orm import sessionmaker
from alchmanager import ManagedQuery, ManagedSession

engine = create_engine('sqlite:///:memory:')
session = sessionmaker(class_=ManagedSession,
                       bind=engine)()


@session.load_manager()
class MainSessionManager:

    @staticmethod
    def published(self):
    	return self.filter_by(is_public=True)

    @staticmethod
    def has_index(self):
        return self.filter_by(is_index=True)

session.query(TestModel).has_index().published().count()
```
