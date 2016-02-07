import re
from kaa.filetype.default import defaultmode
from kaa.syntax_highlight import *

JavaScriptThemes = {
    'basic': [],
}


KEYWORDS = ["break", "case", "catch", "continue", "debugger", "default",
            "delete", "do", "else", "finally", "for", "function", "if", "in",
            "instanceof", "new", "return", "switch", "this", "throw", "try",
            "typeof", "var", "void", "while", "with", "class", "enum", "export",
            "extends", "import", "super", "implements", "interface", "let",
            "package", "private", "protected", "public", "static", "yield", ]


class Regex(Span):
    RE_ENDOFTERM = re.compile(r'[a-zA-Z0-9.)]')

    def _is_regex(self, doc, pos):
        comments = (self.tokenizer.tokens.comment1,
                    self.tokenizer.tokens.comment2)
        not_terms = (self.tokenizer.tokens.keyword,)

        while pos > 0:
            pos -= 1
            token = self.tokenizer.get_token_at(doc, pos)

            if token.tokenizer is not self.tokenizer:
                break

            top = token.get_token_begin(doc, pos)

            # skip comment token
            if token in comments:
                pos = top
                continue

            # check if prev token is keywords
            if token in not_terms:
                break

            s = doc.gettext(top, pos + 1).strip()

            # skip white-space
            if not s:
                pos = top
                continue

            # check if last token is term or closing parenthesis
            m = self.RE_ENDOFTERM.match(s[-1])
            if not m:
                break

            # last token is term(literal, variable, expr, ...)
            return False

        return True

    def on_start(self, doc, match):
        pos = match.start()
        if self._is_regex(doc, pos):
            ret = yield from super().on_start(doc, match)
            return ret
        else:
            # This / is divide operator
            yield (pos, pos + 1, self.tokenizer.styleid_default)
            return pos + 1, False
        return ret


def javascript_tokens():
    return (
        ("comment1", Span('comment', r'/\*', '\*/', escape='\\')),
        ("comment2", Span('comment', r'//', '$', escape='\\')),

        ("keyword", Keywords('keyword', KEYWORDS)),
        ("number", SingleToken('number',
                               [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b'])),
        ("regex", Regex('string', r'/', r'/\w*', escape='\\')),


        ("string1", Span('string', '"', '"', escape='\\')),
        ("string2", Span('string', "'", "'", escape='\\')),
    )


def make_tokenizer():
    return Tokenizer(tokens=javascript_tokens())


class JavaScriptMode(defaultmode.DefaultMode):
    MODENAME = 'JavaScript'
    tokenizer = make_tokenizer()

    def init_themes(self):
        super().init_themes()
        self.themes.append(JavaScriptThemes)
