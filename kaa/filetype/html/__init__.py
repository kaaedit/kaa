from kaa import encodingdef
from kaa.filetype import filetypedef
import re

def iter_attr(b):
    pos = 0
    prop = re.compile(br'(\w+)\s*=\s*', re.DOTALL)
    value = re.compile(b'\s*(("[^"]+")|(\'[^\']+\'))', re.DOTALL)

    while True:
        m = prop.search(b, pos)
        if not m:
            return
        name = m.group(1)
        m = value.match(b, m.end())
        if not m:
            return
        yield name, m.group()[1:-1]
        pos = m.end()

def get_encoding(b):
    # http://www.w3.org/International/questions/qa-html-encoding-declarations

    # HTML5: <meta charset="UTF-8">
    m = re.search(br'<meta ', b, re.DOTALL)
    if m:
        for name, value in iter_attr(b[m.end():]):
            if name == b'charset':
                return str(value.strip(), 'utf-8')

    # HTML4, XHTML: 
    #    <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
    m = re.search(br'<meta ', b, re.DOTALL)
    if m:
        for name, value in iter_attr(b[m.end():]):
            if name == b'content':
                m = re.search(br'charset=(.*)', value, re.DOTALL)
                if m:
                    return str(m.group(1).strip(), 'utf-8')
                break

    # XHTML: <?xml version="1.0" encoding="UTF-8"?>
    m = re.search(br'<\?xml ', b, re.DOTALL)
    if m:
        for name, value in iter_attr(b[m.end():]):
            if name == b'encoding':
                return str(value.strip().strip(), 'utf-8')

class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.htm', '.html'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.html.htmlmode import HTMLMode
        return HTMLMode

    @classmethod
    def update_fileinfo(cls, fileinfo):
        try:
            buffer = open(fileinfo.fullpathname, 'rb').read(1024)
            enc = get_encoding(buffer)
            if enc:
                enc = encodingdef.normalize_encname(enc)
                fileinfo.encoding = enc
        except IOError:
            pass

