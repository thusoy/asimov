# -*- coding: utf-8 -*-

from asimov.opml import import_opml_from_string, export_feeds_to_opml
from asimov.feeds.models import Feed

OPML_FEED = '''\
<?xml version='1.0' encoding='utf-8' ?>
<opml version="1.0">
    <head>
        <title>Feeds</title>
    </head>
    <body>
        <outline text="All items" title="All items"/>
        <outline text="Uncategorized" title="Uncategorized">
            <outline text="Ars Technica" title="Ars Technica" xmlUrl="http://feeds.arstechnica.com/arstechnica/index/"/>
            <outline text="Boing Boing » Science" title="Boing Boing » Science" xmlUrl="https://boingboing.net/tag/science/feed"/>
            <outline text="CGP Grey" title="CGP Grey" xmlUrl="https://feeds.feedburner.com/cgpgrey/PJyo"/>
        </outline>
    </body>
</opml>
'''

def test_opml_import_from_string():
    feeds = import_opml_from_string(OPML_FEED)
    assert len(feeds) == 3

    feed_tuples = [(feed.title, feed.url) for feed in feeds]
    assert ('Ars Technica', 'http://feeds.arstechnica.com/arstechnica/index/') in feed_tuples
    assert ('CGP Grey', 'https://feeds.feedburner.com/cgpgrey/PJyo') in feed_tuples


def test_opml_export_to_string():
    feeds = [
        Feed(url='https://example.com/feed1', title='Example 1'),
    ]
    opml = export_feeds_to_opml(feeds)
    assert opml == '''\
<?xml version='1.0' encoding='utf-8'?>
<opml version="1.0"><head><title>Feeds</title></head><body><outline text="Example 1" title="Example 1" xmlUrl="https://example.com/feed1" /></body></opml>'''
