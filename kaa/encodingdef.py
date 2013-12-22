import kaa
import codecs

encodings = [
    'ascii',
    'big5',
    'big5hkscs',
    'cp037',
    'cp424',
    'cp437',
    'cp500',
    'cp720',
    'cp737',
    'cp775',
    'cp850',
    'cp852',
    'cp855',
    'cp856',
    'cp857',
    'cp858',
    'cp860',
    'cp861',
    'cp862',
    'cp863',
    'cp864',
    'cp865',
    'cp866',
    'cp869',
    'cp874',
    'cp875',
    'cp932',
    'cp949',
    'cp950',
    'cp1006',
    'cp1026',
    'cp1140',
    'cp1250',
    'cp1251',
    'cp1252',
    'cp1253',
    'cp1254',
    'cp1255',
    'cp1256',
    'cp1257',
    'cp1258',
    'euc-jp',
    'euc-jis-2004',
    'euc-jisx0213',
    'euc-kr',
    'gb2312',
    'gbk',
    'gb18030',
    'hz',
    'iso-2022-jp',
    'iso-2022-jp-1',
    'iso-2022-jp-2',
    'iso-2022-jp-2004',
    'iso-2022-jp-3',
    'iso-2022-jp-ext',
    'iso-2022-kr',
    'latin-1',
    'iso-8859-2',
    'iso-8859-3',
    'iso-8859-4',
    'iso-8859-5',
    'iso-8859-6',
    'iso-8859-7',
    'iso-8859-8',
    'iso-8859-9',
    'iso-8859-10',
    'iso-8859-13',
    'iso-8859-14',
    'iso-8859-15',
    'iso-8859-16',
    'johab',
    'koi8-r',
    'koi8-u',
    'mac-cyrillic',
    'mac-greek',
    'mac-iceland',
    'mac-latin2',
    'mac-roman',
    'mac-turkish',
    'ptcp154',
    'shift_jis',
    'shift_jis-2004',
    'shift_jisx0213',
    'utf-32',
    'utf-32be',
    'utf-32le',
    'utf-16',
    'utf-16be',
    'utf-16le',
    'utf-7',
    'utf-8',
    'utf-8-sig',
]

canonical_names = {codecs.lookup(name).name: name for name in encodings}


# from tokenize.py
def _get_normal_name(orig_enc):
    """Imitates get_normal_name in tokenizer.c."""
    # Only care about the first 12 characters.
    enc = orig_enc[:12].lower().replace("_", "-")
    if enc == "utf-8" or enc.startswith("utf-8-"):
        return "utf-8"
    if enc in ("latin-1", "iso-8859-1", "iso-latin-1") or \
       enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
        return "iso-8859-1"
    return orig_enc


def normalize_encname(name, default='utf-8'):
    name = _get_normal_name(name)
    try:
        name = codecs.lookup(name).name
    except LookupError:
        kaa.log.error('Unknown encoding', exc_info=True)
        name = default   # error fallback
    return canonical_names[name]
