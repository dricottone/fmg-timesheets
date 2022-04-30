#!/usr/bin/env python3

# Crash Course on html.parser
#
# A SAX-style parser. Hook into tags and data like...
#
# ```
# from html.parser import HTMLParser
# class MyHTMLParser(HTMLParser):
#    def handle_starttag(self, tag, attrs):
#        #do something...
#    def handle_endtag(self, tag):
#        #do something...
#    def handle_data(self, data):
#        #do something...
# ```
#
# Valid HTML is fed into the parser like...
#
# ```
# parser = MyHTMLParser()
# parser.feed(html)
# ```

from html.parser import HTMLParser

def parse_attrs_string(attrs):
    """Parse a string structures like `key1:value1;key2:value2;`.

    Embedded CSS (as in `style` attributes) can look like this.
    """
    attrs_dict = {}
    for pair in attrs.split(";"):
        if len(pair.strip()) == 0:
            continue
        key, value = pair.split(":")

        key, value = key.strip(), value.strip()
        attrs_dict[key] = value
    return attrs_dict

def parse_attrs_doubles(attrs):
    """Parse a dictionary of HTML/CSS attributes from a series of doubles.

    The built-in Python HTML parser (`html.parser.HTMLParser`) hands attributes
    to the `handle_starttag` hook like this.
    """
    attrs_dict = {}
    for pair in attrs:
        key, value = pair
        if key == "style":
            value = parse_attrs_string(value)
        attrs_dict[key] = value
    return attrs_dict

def has_style_left(attrs):
    return "style" in attrs.keys() and "left" in attrs["style"].keys()

class TimesheetHTMLParser(HTMLParser):
    """A specialization of the `html.parser.HTMLParser` class to handle my
    timesheets.

    Data is stored internally and can be dumped with the `dump` method.

    Don't forget to close the parser instance!
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self._left = 0
        self._in_div = False
        self._in_span = False
        self._data = []

    def handle_starttag(self, tag, _attrs):
        attrs = parse_attrs_doubles(_attrs)
        if self._in_div:
            if tag == "span":
                self._in_span = True
            else:
                self._in_div = False
        elif tag == "div" and has_style_left(attrs):
            self._left = int(attrs["style"]["left"].removesuffix("px"))
            self._in_div = True
        else:
            self._in_span = False
            self._in_div = False

    def handle_endtag(self, tag):
        self._in_span = False
        self._in_div = False

    def handle_data(self, data):
        if self._in_span:
            self._data.append((data.splitlines()[0], self._left, ))
        self._in_span = False
        self._in_div = False

    def dump(self):
        return self._data

def parse(html):
    """Read an HTML-encoded string into semi-structured data."""
    parser = TimesheetHTMLParser()
    try:
        parser.feed(html)
        data = parser.dump()
    finally:
        parser.close()
    return data

