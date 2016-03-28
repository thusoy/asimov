from asimov.feeds.models import Feed, FeedItem
from mock import MagicMock
import datetime
import textwrap

def test_logged_in_frontpage(logged_in_user, testfeed):
    res = logged_in_user.get('/')
    assert res.status_code == 200
    for item in testfeed.items:
        assert item.title in res.data


def test_list_feeds(logged_in_user):
    res = logged_in_user.get('/feeds')
    assert res.status_code == 200

class ResponseMock(object):

    def __init__(self, content='', status_code=200, headers=None):
        if headers is None:
            headers = {}
        self.content = content
        self.status_code = status_code
        self.headers = headers


    @property
    def ok(self):
        return self.status_code < 400


def test_subscribe_to_feed(logged_in_user, monkeypatch):
    # Assume that example.com has a alternate tag for the feed
    def http_get(url):
        return ResponseMock(content='''\
        <head>
            <meta charset='utf-8'>
            <title>Sample page</title>
            <link rel="alternate" href="/feed.atom" title="Sample feed" type="application/atom+xml">
        </head>
        ''')
    monkeypatch.setattr('requests.get', http_get)
    res = logged_in_user.post('/feeds', data={
        'url': 'http://example.com',
    })
    assert res.status_code == 302
    feeds = Feed.query.all()
    assert len(feeds) == 1
    feed = feeds[0]
    assert feed.title == 'Sample feed'


def test_updating_simple_feeds(logged_in_user, monkeypatch):
    def http_get(url):
        return ResponseMock(content=textwrap.dedent('''\
            <?xml version="1.0" encoding="utf-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">

             <title>Example Feed</title>
             <link href="http://example.org/"/>
             <updated>2003-12-13T18:30:02Z</updated>
             <author>
               <name>John Doe</name>
             </author>
             <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>

             <entry>
               <title>Atom-Powered Robots Run Amok</title>
               <link href="http://example.org/2003/12/13/atom03"/>
               <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
               <updated>2003-12-13T18:30:02Z</updated>
               <summary>Some text.</summary>
             </entry>

            </feed>
            '''), headers={'content-type': 'application/atom+xml'})
    monkeypatch.setattr('requests.get', http_get)
    Feed.create(title='Sample feed', url='http://example.com/feed')
    res = logged_in_user.post('/feeds/update')
    assert res.status_code == 302
    feed_items = FeedItem.query.all()
    assert len(feed_items) == 1
    feed_item = feed_items[0]
    assert feed_item.title == 'Atom-Powered Robots Run Amok'
    # Should have normalized the update field into published_date
    expected_published_date = datetime.datetime(2003, 12, 13, 18, 30, 02)
    assert feed_item.updated_date == expected_published_date
    assert feed_item.author == 'John Doe'

