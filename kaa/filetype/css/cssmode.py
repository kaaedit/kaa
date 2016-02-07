import re
from kaa.filetype.default import defaultmode
from kaa.theme import Style
from kaa import encodingdef
from kaa.syntax_highlight import *

# todo: highlighter should be written.

CSSThemes = {
    'basic': [
        Style('media-selector', 'yellow', 'default'),
        Style('css-selector', 'magenta', 'default'),
        Style('css-propname', 'cyan', 'default', bold=True),
        Style('css-propvalue', 'green', 'default', bold=True),
    ],
}


class MediaToken(SingleToken):

    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        pos = yield from self.tokenizer.MediaCSSTokenizer.run(doc, pos)

        return pos, False


class RuleSetToken(SingleToken):

    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        if match.group(0) == '{':
            pos = yield from self.tokenizer.PropTokenizer.run(doc, pos)

        return pos, False


class PropNameToken(SingleToken):

    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        pos = yield from self.tokenizer.PropValueTokenizer.run(doc, pos)

        return pos, self.terminates


def make_prop_tokenizer(root, terminates=None):
    ret = Tokenizer(parent=root, terminates=terminates,
                    tokens=(
                        ('comment1', Span('comment', r'/\*', '\*/', escape='\\')),
                        ('propname', PropNameToken(
                            'css-propname', [r'[^:\s]+:'])),
                        ('terminate_name', SingleToken(
                            'css-selector', [r'}'], terminates=True)),
                    ))

    ret.PropValueTokenizer = Tokenizer(parent=ret, terminates=terminates,
                                       tokens=(
                                           ('close', Terminator(
                                               'css-selector', [r'\}'])),
                                           ('terminate_value', SingleToken(
                                               'css-propvalue', [r';'], terminates=True)),
                                           ('comment1', Span('comment',
                                                             r'/\*', '\*/', escape='\\')),
                                           ('string', SingleToken(
                                               'string', [r'[a-zA-Z_]\w*'])),
                                           ('string1', Span(
                                               'string', '"', '"', escape='\\')),
                                           ('string2', Span(
                                               'string', "'", "'", escape='\\')),
                                           ("color", SingleToken(
                                               'keyword', [r'\#[0-9a-zA-Z]+'])),
                                           ("number",
                                              SingleToken('number',
                                                          [r'[+-]?[0-9]+(\.[0-9]*)*([a-z]*)', r'[+-]?\.[0-9]([a-z]*)'])),
                                       ))

    return ret


def get_css_tokens():
    return [
        ('comment1', Span('comment', r'/\*', '\*/', escape='\\')),
        ('string1', Span('string', '"', '"', escape='\\')),
        ('string2', Span('string', "'", "'", escape='\\')),
        ('ruleset', RuleSetToken('css-selector', [r'\{'])),
    ]


def make_tokenizer(parent, terminates=None):
    ret = Tokenizer(parent=parent, default_style='css-selector',
                    terminates=terminates,
                    tokens=[
                        ('media', MediaToken(
                            'media-selector', [r'@media[^{]*\{?'])),
                        ('decl', SingleToken('directive', [r'@\w*'])),
                    ]
                    + get_css_tokens())

    ret.PropTokenizer = make_prop_tokenizer(ret, terminates=terminates)
    ret.MediaCSSTokenizer = Tokenizer(
        parent=ret, default_style='css-selector',
        tokens=get_css_tokens() +
        [('terminate_media', SingleToken('media-selector', [r'}'], terminates=True))])

    ret.MediaCSSTokenizer.PropTokenizer = make_prop_tokenizer(ret.MediaCSSTokenizer,
                                                              terminates=terminates)
    return ret


class CSSMode(defaultmode.DefaultMode):
    MODENAME = 'CSS'
    tokenizer = make_tokenizer(None, None)

    @classmethod
    def update_fileinfo(cls, fileinfo, document=None):
        if not document:
            try:
                with open(fileinfo.fullpathname, 'rb') as buffer:
                    s = buffer.read(1024)
            except IOError:
                return
        else:
            s = document.gettext(0, 1024).encode('utf-8', errors='ignore')

        m = re.search(
            rb'@charset\s+(' + rb'"([^"]+)"|' + rb"('[^']+'))", s)
        if m:
            enc = str(m.group(2) or m.group(3), 'utf-8', 'replace').strip()
            enc = encodingdef.normalize_encname(enc, fileinfo.encoding)
            fileinfo.encoding = enc

    def init_themes(self):
        super().init_themes()
        self.themes.append(CSSThemes)
