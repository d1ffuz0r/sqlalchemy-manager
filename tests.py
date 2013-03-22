#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import unittest
from alchmanager import ManagedQuery, ManagedSession


engine = create_engine('sqlite:///:memory:')
session = sessionmaker(query_cls=ManagedQuery,
                       class_=ManagedSession,
                       bind=engine)()
Base = declarative_base()


@session.load_manager()
class MainSessionManager:

    @staticmethod
    def published(query):
        return query.filter_by(is_public=True)

    @staticmethod
    def has_index(query):
        return query.filter_by(is_index=True)


class MainManager:

    @staticmethod
    def is_index(query):
        return query.filter_by(is_index=True)

    @staticmethod
    def is_public(query):
        return query.filter_by(is_public=True)


class Main(Base):
    __tablename__ = 'main'
    id = Column(Integer, primary_key=True)
    child = Column(Integer, index=True)
    preview = Column(String(50))
    typeMedia = Column(Integer)
    is_index = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    __manager__ = MainManager

    __mapper_args__ = {'polymorphic_on': typeMedia}


class Video(Main):
    __tablename__ = 'video'
    videoid = Column(Integer, ForeignKey(Main.child), primary_key=True)
    movie = Column(String(50))
    __mapper_args__ = {'polymorphic_identity': 1,
                       'inherit_condition': (Main.typeMedia == 1) &
                                            (Main.child == videoid)}


class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    child = Column(Integer, index=True)
    is_public = Column(Boolean, default=False)
    is_index = Column(Boolean)


Base.metadata.create_all(engine)
items = [Video(movie='test',
               preview='test'),
         Video(movie='test',
               preview='testmovie',
               is_index=True),
         Test(child=1,
              is_public=True,
              is_index=True),
         Test(child=2)]

session.add_all(items)
session.commit()


class TestsQueryManager(unittest.TestCase):

    def test_queires(self):
        standart_query = session.query(Video).filter_by(is_index=True).all()
        managed_query = session.query(Video).is_index().all()
        self.assertEquals(standart_query, managed_query)

    def test_subclass_query(self):
        self.assertTrue(hasattr(session.query(Video), 'is_index'))
        self.assertTrue(session.query(Video).is_index())
        self.assertTrue(
            session.query(Video).is_index().filter_by(child=1).is_public()
        )

    def test_without_manager(self):
        self.assertFalse(hasattr(session.query(Test), 'is_index'))


class TestsSessionManager(unittest.TestCase):

    def test_is_loaded(self):
        self.assertTrue(hasattr(session.query(Test), 'published'))

    def test_queries(self):
        self.assertEquals(session.query(Test).published().count(), 1)
        self.assertEquals(session.query(Test).count(), 2)

    def test_with_many_calls(self):
        query = session.query(Test).has_index().published().count()
        self.assertEquals(query, 1)


if __name__ == '__main__':
    unittest.main()
