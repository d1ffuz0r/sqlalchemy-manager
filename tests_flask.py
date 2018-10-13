#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ~ Author: Pavel Ivanov

import flask
import unittest
import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy

from alchmanager import ManagedQuery


class Config:
    DEBUG = False
    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app = flask.Flask(__name__)
db = SQLAlchemy(query_class=ManagedQuery)


class MainManager:

    @staticmethod
    def is_index(query):
        return query.filter_by(is_index=True)

    @staticmethod
    def is_public(query):
        return query.filter_by(is_public=True)


class Main(db.Model):
    __tablename__ = 'main'
    id = sa.Column(sa.Integer, primary_key=True)
    child = sa.Column(sa.Integer, index=True)
    preview = sa.Column(sa.String(50))
    typeMedia = sa.Column(sa.Integer)
    is_index = sa.Column(sa.Boolean, default=False)
    is_public = sa.Column(sa.Boolean, default=False)

    __manager__ = MainManager

    __mapper_args__ = {'polymorphic_on': typeMedia}


class Video(Main):
    __tablename__ = 'video'
    videoid = sa.Column(sa.Integer, sa.ForeignKey(Main.child), primary_key=True)
    movie = sa.Column(sa.String(50))
    __mapper_args__ = {'polymorphic_identity': 1,
                       'inherit_condition': (Main.typeMedia == 1) &
                                            (Main.child == videoid)}


@app.route('/testing-queries-v1', methods=['POST'])
def run_testing_queires_v1():
    standart_query = db.session.query(Video).filter_by(is_index=True).all()
    managed_query = db.session.query(Video).is_index().all()

    try:
        assert standart_query == managed_query
    except AssertionError:
        flask.abort(500)

    return ''


@app.route('/testing-subclass-query-v1', methods=['POST'])
def run_testing_subclass_query_v1():
    try:
        assert hasattr(db.session.query(Video), 'is_index')
        assert callable(db.session.query(Video).is_index)
        assert callable(
            db.session.query(Video).is_index().filter_by(child=1).is_public
        )
    except AssertionError:
        flask.abort(500)

    return ''


@app.route('/testing-queries-v2', methods=['POST'])
def run_testing_queires_v2():
    standart_query = Video.query.filter_by(is_index=True).all()
    managed_query = Video.query.is_index().all()

    try:
        assert standart_query == managed_query
    except AssertionError:
        flask.abort(500)

    return ''


@app.route('/testing-subclass-query-v2', methods=['POST'])
def run_testing_subclass_query_v2():
    try:
        assert hasattr(Video.query, 'is_index')
        assert callable(Video.query.is_index)
        assert callable(Video.query.is_index().filter_by(child=1).is_public)
    except AssertionError:
        flask.abort(500)

    return ''


class TestsQueryManager(unittest.TestCase):

    def setUp(self):
        self.app = None

        app.config.from_object(Config())

        with app.app_context():
            db.init_app(app)
            db.create_all()

        self.app = app.test_client()

    def test_post_v1(self):
        response = self.app.post('/testing-queries-v1')
        self.assertEqual(response.status_code, 200)

    def test_post_v2(self):
        response = self.app.post('/testing-queries-v2')
        self.assertEqual(response.status_code, 200)

    def test_post_v3(self):
        response = self.app.post('/testing-subclass-query-v1')
        self.assertEqual(response.status_code, 200)

    def test_post_v4(self):
        response = self.app.post('/testing-subclass-query-v2')
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
