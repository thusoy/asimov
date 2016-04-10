# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from flask.ext.login import login_user
from flask import session
from webtest import TestApp

from asimov.app import create_app
from asimov.user.models import User
from asimov.feeds.models import Feed, FeedItem
from asimov.database import db as _db
from asimov.settings import TestConfig

from .factories import UserFactory


@pytest.yield_fixture(scope='function')
def app():
    """An application for the tests."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """A user for the tests."""
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user


@pytest.fixture
def logged_in_user(db):
    app = create_app(TestConfig)
    user = User(username='testuser', email='test@example.com')
    with app.test_request_context():
        db.session.add(user)
        db.session.commit()

        # Login the user and save the session
        login_user(user)
        session_copy = session.copy()

    # Re-create the session with a new test client
    with app.test_client() as c:
        with c.session_transaction() as sess:
            for k, v in session_copy.items():
                sess[k] = v
        return c


@pytest.fixture
def testfeed(db):
    feed = Feed(title='Sample Feed', url='http://example.com/feed')
    db.session.add(feed)
    for item in range(3):
        feed_item = FeedItem(title='Item %d' % item, feed=feed,
            source_url='http://example.com/item%d' % item)
        db.session.add(feed_item)
    db.session.commit()
    return feed


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr('requests.sessions.Session.request')
