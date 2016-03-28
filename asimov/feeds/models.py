# -*- coding: utf-8 -*-

import datetime
from time import mktime

from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL
import feedparser
import requests

from asimov.database import Column, Model, SurrogatePK, db, relationship


class Feed(SurrogatePK, Model):
    __tablename__ = 'feeds'

    title = Column(db.String(128), nullable=False)
    url = Column(db.String(512), nullable=False)
    # rss_url = Column(db.String(512), nullable=False)
    image = Column(db.String(512), nullable=True)
    last_updated = Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Feed({title})>'.format(title=self.title)


    def update(self):
        import pprint
        # Use requests to fetch the url to make it easier to mock
        raw_feed = requests.get(self.url)
        feed = feedparser.parse(raw_feed.content)
        feed_author = feed.feed.get('author')
        # self.title = feed.title
        print 'feed', pprint.pprint(feed.feed)
        # print 'items', feed['items']
        for item in feed['items']:
            # print 'item', item
            author = item.get('author') or feed_author
            updated_ts = mktime(item.updated_parsed)
            updated_date = datetime.datetime.fromtimestamp(updated_ts)
            # published_date = item.get('published') or item.updated
            FeedItem.create(title=item.title, source_url=item.link,
                updated_date=updated_date, author=author)


class FeedItem(SurrogatePK, Model):
    __tablename__ = 'feed_items'

    title = Column(db.String(128), nullable=False)
    summary = Column(db.Text, nullable=True)
    source_url = Column(db.String(512), nullable=False)
    has_been_read = Column(db.Boolean, nullable=False, default=False)
    author = Column(db.String(128))
    #: Content as given directly in the feed
    feed_content = Column(db.Text, nullable=True)
    #: Content as extracted from the source_url
    raw_source_content = Column(db.Text, nullable=True)
    #: Content as parsed from either feed or source_url. Can be re-computed
    #: later if parsing improves
    content = Column(db.Text, nullable=True)
    published_date = Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_date = Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    feed_id = db.Column(db.Integer, db.ForeignKey('feeds.id'))
    feed = relationship('Feed', backref=db.backref('items', lazy='dynamic', cascade='all,delete'))


class FeedForm(Form):
    """Register form."""

    url = StringField('Subscribe to new feed',
        validators=[DataRequired(), URL(), Length(min=4, max=512)])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(FeedForm, self).__init__(*args, **kwargs)
        self.user = None


    # def validate(self):
    #     """Validate the form."""
    #     initial_validation = super(FeedForm, self).validate()
    #     if not initial_validation:
    #         return False
    #     user = User.query.filter_by(username=self.username.data).first()
    #     if user:
    #         self.username.errors.append('Username already registered')
    #         return False
    #     user = User.query.filter_by(email=self.email.data).first()
    #     if user:
    #         self.email.errors.append('Email already registered')
    #         return False
    #     return True
