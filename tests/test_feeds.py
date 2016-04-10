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
    assert feed_item.summary == 'Some text.'


def test_doesnt_add_duplicates_atom(logged_in_user, monkeypatch):
    # TODO: should update if content is changed but not add new items
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
    feed = Feed.create(title='Sample feed', url='http://example.com/feed')
    feed.update()
    items = FeedItem.query.all()
    assert len(items) == 1
    feed.update()
    items = FeedItem.query.all()
    assert len(items) == 1


def test_doesnt_add_duplicates_rss_0_91(logged_in_user, monkeypatch):
    # TODO: should update if content is changed but not add new items
    def http_get(url):
        return ResponseMock(content=textwrap.dedent('''\
<?xml version="1.0" encoding="ISO-8859-1"?>
<rss version="0.91">
    <channel>
        <title>WriteTheWeb</title>
        <link>http://writetheweb.com</link>
        <description>News for web users that write back</description>
        <language>en-us</language>
        <copyright>Copyright 2000, WriteTheWeb team.</copyright>
        <managingEditor>editor@writetheweb.com</managingEditor>
        <webMaster>webmaster@writetheweb.com</webMaster>
        <image>
            <title>WriteTheWeb</title>
            <url>http://writetheweb.com/images/mynetscape88.gif</url>
            <link>http://writetheweb.com</link>
            <width>88</width>
            <height>31</height>
            <description>News for web users that write back</description>
        </image>
        <item>
            <title>Giving the world a pluggable Gnutella</title>
            <link>http://writetheweb.com/read.php?item=24</link>
            <description>WorldOS is a framework on which to build programs that work like Freenet or Gnutella -allowing distributed applications using peer-to-peer routing.</description>
        </item>
        <item>
            <title>Syndication discussions hot up</title>
            <link>http://writetheweb.com/read.php?item=23</link>
            <description>After a period of dormancy, the Syndication mailing list has become active again, with contributions from leaders in traditional media and Web syndication.</description>
        </item>
        </channel>
    </rss>'''), headers={'content-type': 'application/xml'})
    monkeypatch.setattr('requests.get', http_get)
    feed = Feed.create(title='Sample feed', url='http://example.com/feed')
    feed.update()
    items = FeedItem.query.all()
    assert len(items) == 2
    feed.update()
    items = FeedItem.query.all()
    assert len(items) == 2


def test_doesnt_add_duplicates_rss_2_0(logged_in_user, monkeypatch):
    # TODO: should update if content is changed but not add new items
    def http_get(url):
        return ResponseMock(content=textwrap.dedent('''\
<?xml version="1.0"?>
<rss version="2.0">
   <channel>
      <title>Liftoff News</title>
      <link>http://liftoff.msfc.nasa.gov/</link>
      <description>Liftoff to Space Exploration.</description>
      <language>en-us</language>
      <pubDate>Tue, 10 Jun 2003 04:00:00 GMT</pubDate>
      <lastBuildDate>Tue, 10 Jun 2003 09:41:01 GMT</lastBuildDate>
      <docs>http://blogs.law.harvard.edu/tech/rss</docs>
      <generator>Weblog Editor 2.0</generator>
      <managingEditor>editor@example.com</managingEditor>
      <webMaster>webmaster@example.com</webMaster>
      <item>
         <title>Star City</title>
         <link>http://liftoff.msfc.nasa.gov/news/2003/news-starcity.asp</link>
         <description>How do Americans get ready to work with Russians aboard the International Space Station? They take a crash course in culture, language and protocol at Russia's &lt;a href="http://howe.iki.rssi.ru/GCTC/gctc_e.htm"&gt;Star City&lt;/a&gt;.</description>
         <pubDate>Tue, 03 Jun 2003 09:39:21 GMT</pubDate>
         <guid>http://liftoff.msfc.nasa.gov/2003/06/03.html#item573</guid>
      </item>
      <item>
         <description>Sky watchers in Europe, Asia, and parts of Alaska and Canada will experience a &lt;a href="http://science.nasa.gov/headlines/y2003/30may_solareclipse.htm"&gt;partial eclipse of the Sun&lt;/a&gt; on Saturday, May 31st.</description>
         <pubDate>Fri, 30 May 2003 11:06:42 GMT</pubDate>
         <guid>http://liftoff.msfc.nasa.gov/2003/05/30.html#item572</guid>
      </item>
   </channel>
</rss>'''), headers={'content-type': 'application/xml'})
    monkeypatch.setattr('requests.get', http_get)
    feed = Feed.create(title='Sample feed', url='http://example.com/feed')
    feed.update()
    items = FeedItem.query.all()
    assert len(items) == 2
    feed.update()
    items = FeedItem.query.all()
    assert len(items) == 2


def test_doesnt_add_duplicates_rss_troy_hunt(logged_in_user, monkeypatch):
    def http_get(url):
        return ResponseMock(content=textwrap.dedent('''\
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" media="screen" href="/~d/styles/atom10full.xsl"?>
<?xml-stylesheet type="text/css" media="screen" href="http://feeds.feedburner.com/~d/styles/itemcontent.css"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:openSearch="http://a9.com/-/spec/opensearchrss/1.0/" xmlns:blogger="http://schemas.google.com/blogger/2008" xmlns:georss="http://www.georss.org/georss" xmlns:gd="http://schemas.google.com/g/2005" xmlns:thr="http://purl.org/syndication/thread/1.0" xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#" xmlns:feedburner="http://rssnamespace.org/feedburner/ext/1.0">
<id>tag:blogger.com,1999:blog-3977663544337573923</id>
<updated>2016-04-08T19:25:48.794+10:00</updated>
<category term="Security" />
<title type="text">Troy Hunt's Blog</title>
<subtitle type="html">Observations, musings and conjecture about the world of software and technology</subtitle>
<link rel="alternate" type="text/html" href="http://www.troyhunt.com/" />
<link rel="next" type="application/atom+xml" href="http://www.blogger.com/feeds/3977663544337573923/posts/default?start-index=11&amp;max-results=10&amp;redirect=false" />
<author>
    <name>Troy Hunt</name>
    <uri>https://plus.google.com/111846329802076778489</uri>
    <email>noreply@blogger.com</email>
    <gd:image rel="http://schemas.google.com/g/2005#thumbnail" width="32" height="32" src="//lh3.googleusercontent.com/-r4_CjHr7f7Q/AAAAAAAAAAI/AAAAAAAAHGM/ATfTwh1qXkc/s512-c/photo.jpg" />
</author>
<generator version="7.00" uri="http://www.blogger.com">Blogger</generator>
<openSearch:totalResults>432</openSearch:totalResults>
<openSearch:startIndex>1</openSearch:startIndex>
<openSearch:itemsPerPage>10</openSearch:itemsPerPage>
<atom10:link xmlns:atom10="http://www.w3.org/2005/Atom" rel="self" type="application/atom+xml" href="http://feeds.feedburner.com/TroyHunt" />
<feedburner:info uri="troyhunt" />
<atom10:link xmlns:atom10="http://www.w3.org/2005/Atom" rel="hub" href="http://pubsubhubbub.appspot.com/" />
<geo:lat>-33.824008</geo:lat>
<geo:long>151.251244</geo:long>
<link rel="license" type="text/html" href="http://creativecommons.org/licenses/by/3.0/" />
<feedburner:emailServiceId>TroyHunt</feedburner:emailServiceId>
<feedburner:feedburnerHostname>https://feedburner.google.com</feedburner:feedburnerHostname>
<entry>
    <id>tag:blogger.com,1999:blog-3977663544337573923.post-6930448265510538112</id>
    <published>2016-04-08T19:04:00.001+10:00</published>
    <updated>2016-04-08T19:25:48.804+10:00</updated>
    <category scheme="http://www.blogger.com/atom/ns#" term="Have I been pwned?" />
    <title type="text">Have I been pwned, opting out, VTech and general privacy things</title>
    <content type="html">foo</content>
    <link rel="edit" type="application/atom+xml" href="http://www.blogger.com/feeds/3977663544337573923/posts/default/6930448265510538112" />
    <link rel="self" type="application/atom+xml" href="http://www.blogger.com/feeds/3977663544337573923/posts/default/6930448265510538112" />
    <link rel="alternate" type="text/html" href="http://feedproxy.google.com/~r/TroyHunt/~3/bBQm5vqE7Kc/have-i-been-pwned-opting-out-vtech-and.html" title="Have I been pwned, opting out, VTech and general privacy things" />
    <author>
        <name>Troy Hunt</name>
        <uri>https://plus.google.com/111846329802076778489</uri>
        <email>noreply@blogger.com</email>
        <gd:image rel="http://schemas.google.com/g/2005#thumbnail" width="32" height="32" src="//lh3.googleusercontent.com/-r4_CjHr7f7Q/AAAAAAAAAAI/AAAAAAAAHGM/ATfTwh1qXkc/s512-c/photo.jpg" />
    </author>
    <media:thumbnail xmlns:media="http://search.yahoo.com/mrss/" url="https://lh3.googleusercontent.com/-64zGAtOv19A/Vwd0AAkPM_I/AAAAAAAAI9A/xnUrKkwOT4c/s72-c/image2.png?imgmax=800" height="72" width="72" />
    <feedburner:origLink>http://www.troyhunt.com/2016/04/have-i-been-pwned-opting-out-vtech-and.html</feedburner:origLink>
</entry>
<entry>
    <id>tag:blogger.com,1999:blog-3977663544337573923.post-1954271889073374940</id>
    <published>2016-04-07T07:10:00.001+10:00</published>
    <updated>2016-04-07T07:10:23.605+10:00</updated>
    <category scheme="http://www.blogger.com/atom/ns#" term="MVP" />
    <title type="text">MVP, round 6!</title>
    <content type="html">bar</content>
    <link rel="edit" type="application/atom+xml" href="http://www.blogger.com/feeds/3977663544337573923/posts/default/1954271889073374940" />
    <link rel="self" type="application/atom+xml" href="http://www.blogger.com/feeds/3977663544337573923/posts/default/1954271889073374940" />
    <link rel="alternate" type="text/html" href="http://feedproxy.google.com/~r/TroyHunt/~3/YMC_D_hpicg/mvp-round-6.html" title="MVP, round 6!" />
    <author>
        <name>Troy Hunt</name>
        <uri>https://plus.google.com/111846329802076778489</uri>
        <email>noreply@blogger.com</email>
        <gd:image rel="http://schemas.google.com/g/2005#thumbnail" width="32" height="32" src="//lh3.googleusercontent.com/-r4_CjHr7f7Q/AAAAAAAAAAI/AAAAAAAAHGM/ATfTwh1qXkc/s512-c/photo.jpg" />
    </author>
    <media:thumbnail xmlns:media="http://search.yahoo.com/mrss/" url="https://lh3.googleusercontent.com/-z5qeoT-epcE/VwV7PM9v5LI/AAAAAAAAI8w/AljCJCcVv3E/s72-c/image%25255B6%25255D.png?imgmax=800" height="72" width="72" />
    <feedburner:origLink>http://www.troyhunt.com/2016/04/mvp-round-6.html</feedburner:origLink>
</entry>
</feed>'''), headers={'content-type': 'application/xml'})
    monkeypatch.setattr('requests.get', http_get)
    feed = Feed.create(title='Troy Hunt', url='http://example.com/feed')
    feed.update()
    items = FeedItem.query.all()
    assert len(items) == 2
    feed.update()
    items = FeedItem.query.all()
    assert len(items) == 2


def test_sanitizes_feeds(logged_in_user, monkeypatch):
    # Test sanitization
    pass

# def test_get_single_feed(logged_in_user, testfeed):
#     response = logged_in_user.get('/feeds/%d' % testfeed.id)
#     assert response.status_code == 200


def test_unsubscribe_feed(logged_in_user, testfeed):
    response = logged_in_user.delete('/feeds/%d' % testfeed.id)
    assert response.status_code < 400
    assert Feed.query.count() == 0
