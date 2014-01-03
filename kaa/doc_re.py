from gappedbuf.re import *
from gappedbuf import re as gre


def match(pattern, doc, flags=0):
    """Try to apply the pattern at the start of the string, returning
    a match object, or None if no match was found."""
    return _compile(pattern, flags).match(doc)


def search(pattern, doc, flags=0):
    """Scan through string looking for a match to the pattern, returning
    a match object, or None if no match was found."""
    return _compile(pattern, flags).search(string)


def compile(pattern, flags=0):
    "Compile a regular expression pattern, returning a pattern object."
    return _compile(pattern, flags)


class _compile:

    def __init__(self, pattern, flags):
        self.reobj = gre._compile(pattern, flags)

    def findall(self, doc, *args, **kwargs):
        return self.reobj.findall(doc.buf, *args, **kwargs)

    def finditer(self, doc, *args, **kwargs):
        return self.reobj.finditer(doc.buf, *args, **kwargs)

    def match(self, doc, *args, **kwargs):
        return self.reobj.match(doc.buf, *args, **kwargs)

    def search(self, doc, *args, **kwargs):
        return self.reobj.search(doc.buf, *args, **kwargs)
