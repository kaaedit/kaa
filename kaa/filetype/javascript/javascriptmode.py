from collections import namedtuple
from kaa.filetype.default import defaultmode
from kaa.highlight import Tokenizer, Span, Keywords, EndSection, SingleToken
from kaa.theme import Theme, Style

JavaScriptThemes = {
    'basic': [],
}

class JSRegex(Span):
    def on_start(self, tokenizer, doc, pos, match):
        valid_tokens = (tokenizer.tokens.keywords, tokenizer.tokens.punctuation1)
        ignore_tokens = (tokenizer.tokens.comment1, tokenizer.tokens.comment2)

        p = pos-1
        while p >= 0:
            style = doc.styles.getints(p, p + 1)[0]
            token = tokenizer.get_token(style)
            # if token is subtokenizer, get actual token inside subtokenizer.
            if token:
                token = token.get_token(style)
            
            if not token or token in ignore_tokens:
                # ignore comment tokens
                oldp=p
                p = doc.styles.rfindint([style], 0, p, comp_ne=True)
                if p == -1:
                    break
                continue

            if token in valid_tokens:
                # regex can be put here.
                break

            if token not in tokenizer.tokens:
                # Token is not JS token. May be embedded in HTML.
                break

            ret = yield from tokenizer.tokens.punctuation1.on_start(
                                tokenizer, doc, pos, match)
            return ret

        ret = yield from super().on_start(tokenizer, doc, pos, match)
        return ret

    def resume_pos(self, highlighter, tokenizer, doc, pos):
        t, token, p = self.get_prev_token(tokenizer, doc, pos)
        if token:
            return token.resume_pos(highlighter, t, doc, p)
        else:
            return self.find_token_top(doc, pos)

def build_tokenizer(stop=None, terminates=None):
    JSTOKENS = namedtuple(
        'jstokens', ['stop', 'keywords', 'number', 'comment1', 'comment2',
                     'string1', 'string2', 'regex', 'punctuation1', 'punctuation2'])

    keywords = Keywords(
                'javascript-keyword', 'keyword',
                ["break", "case", "catch", "continue", "debugger", "default",
                 "delete", "do", "else", "finally", "for", "function", "if", "in",
                 "instanceof", "new", "return", "switch", "this", "throw", "try",
                 "typeof", "var", "void", "while", "with", "class", "enum", "export",
                 "extends", "import", "super", "implements", "interface", "let",
                 "package", "private", "protected", "public", "static", "yield", ])

    number = SingleToken('javascript-numeric', 'number',
                         [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b'])
    comment1 = Span('javascript-comment1', 'comment',
                    r'/\*', r'\*/', escape='\\')
    comment2 = Span('javascript-comment2', 'comment', r'//', r'$', escape='\\')
    string1 = Span('javascript-string1', 'string', '"', '"', escape='\\')
    string2 = Span('javascript-string2', 'string', "'", "'", escape='\\')

    regex = JSRegex('javascript-regex', 'string',
                    r'/', r'/\w*', escape='\\')

    punctuation1 = SingleToken('javascript-punctuation1', 'default',
                         [r'[+\-*/~&?:|=%;<>^({[,:]'])

    punctuation2 = SingleToken('javascript-punctuation2', 'default',
                         [r'\S'])

    tokens = JSTOKENS(stop, keywords, number, comment1, comment2, string1, string2,
                      regex, punctuation1, punctuation2)

    return Tokenizer(tokens, terminates=terminates)


class JavaScriptMode(defaultmode.DefaultMode):
    MODENAME = 'JavaScript'

    def init_themes(self):
        super().init_themes()
        self.themes.append(JavaScriptThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]
