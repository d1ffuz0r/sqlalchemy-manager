#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import unittest
from alchmanager import ManagedQuery


engine = create_engine('sqlite:///:memory:')
session = sessionmaker(query_cls=ManagedQuery,
                       bind=engine)()
Base = declarative_base()


class MainManager:
    """Manager with simple custom methods"""
    @staticmethod
    def is_index(self):
        return self.filter_by(is_index=True)


class Main(Base):
    __tablename__ = 'main'
    id = Column(Integer, primary_key=True)
    child = Column(Integer, index=True)
    preview = Column(String(50))
    typeMedia = Column(Integer)
    is_index = Column(Boolean, default=False)

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


Base.metadata.create_all(engine)
v = Video(movie='test',
          preview='test')
p = Video(movie='test',
          preview='testmovie',
          is_index=True)
session.add_all([v, p])
session.commit()


class TestsQueryManager(unittest.TestCase):

    def test_queires(self):
        standart_query = session.query(Video).filter_by(is_index=True).all()
        managed_query = session.query(Video).is_index().all()
        self.assertEquals(standart_query, managed_query)

    def test_subclass_query(self):
        self.assertTrue(hasattr(session.query(Video), 'is_index'))
        self.assertTrue(session.query(Video).is_index())

    def test_table_without_manager(self):
        self.assertFalse(hasattr(session.query(Test), 'is_index'))


if __name__ == '__main__':
    unittest.main()
