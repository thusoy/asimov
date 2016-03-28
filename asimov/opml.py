from xml.etree import ElementTree as ET
import StringIO

from .feeds.models import Feed

def import_opml_from_string(opml_string):
    feeds = []
    tree = ET.fromstring(opml_string)
    for node in tree.findall('.//outline'):
        url = node.attrib.get('xmlUrl')
        if url:
            title = node.attrib.get('title')
            feed = Feed(url=url, title=title)
            feeds.append(feed)
    return feeds


def export_feeds_to_opml(feeds):
    root = ET.Element('opml', version='1.0')
    head = ET.SubElement(root, 'head')
    title = ET.SubElement(head, 'title')
    title.text = 'Feeds'
    body = ET.SubElement(root, 'body')

    for feed in feeds:
        outline = ET.SubElement(body, 'outline',
            title=feed.title, text=feed.title, xmlUrl=feed.url)

    opml_output = StringIO.StringIO()

    ET.ElementTree(root).write(opml_output, xml_declaration=True, encoding='utf-8')

    return opml_output.getvalue()
