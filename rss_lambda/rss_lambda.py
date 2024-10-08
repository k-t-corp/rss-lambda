import feedparser
from typing import Callable, Optional, Dict
from lxml import etree


class RSSLambdaError(Exception):
     def __init__(self, message):
        self.message = message
        super().__init__(self.message)

supported_feed_versions = ["rss20", "atom10", "atom03"]
xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'

def rss_lambda(
        rss_text: str,
        rss_item_lambda: Callable[[etree.Element, Dict], Optional[etree.Element]]
) -> str: 
    # Determine if it's a valid and supported feed
    feed = feedparser.parse(rss_text)
    if feed.bozo != 0:
        raise RSSLambdaError(f"Failed to parse the feed")
    if feed.version not in supported_feed_versions:
        raise RSSLambdaError(f"Unsupported feed version: {feed.version}")

    # Parse the feed and find the parent element of the items or entries
    lxml_parser = etree.XMLParser(strip_cdata=False)
    root = etree.fromstring(rss_text.encode('utf-8'), parser=lxml_parser)
    if feed.version == 'rss20':
        parent = root.find('./channel')
        items = parent.findall('item')
    elif feed.version in ['atom10', 'atom03']:
        parent = root
        items = parent.findall('{http://www.w3.org/2005/Atom}entry')
    else:
        raise RSSLambdaError(f"Escaped unsupported feed version: {feed.version}")

    # Filter the items or entries
    transformed_items = list(map(lambda item: rss_item_lambda(item, root.nsmap), items))

    # Remove all original items and appended kept items
    for item in items:
        parent.remove(item)
    for item in transformed_items:
        if item is not None:
            parent.append(item)

    # Return the filtered feed
    if xml_declaration in rss_text:
        return xml_declaration + '\n' + etree.tostring(root, encoding='unicode')
    else:
        return etree.tostring(root, encoding='unicode')
