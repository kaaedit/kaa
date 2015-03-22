from collections import namedtuple
import kaa
from kaa.filetype.default import defaultmode
from kaa.highlight import Tokenizer, Span, Keywords, EndSection, SingleToken
from kaa.theme import Theme, Style

JavaScriptThemes = {
    'basic': [],
}


class JSRegex(Span):
    OPERATORS = set('+\-*/~&?:|=%;<>^({[,:]')

    def _is_regex(self, tokenizer, doc, pos):
        # check if current token is valid regex expr or not
        ignore_tokens = {tokenizer.tokens.comment1, tokenizer.tokens.comment2}
        p = pos - 1
        while p >= 0:
            _tokenizer, token, prev = tokenizer.highlighter.get_prev_token(doc, p)

            if token is None:
                return True
            else:
                end_prev_token = token.find_token_end(doc, prev)

            if end_prev_token <= p:
                s = doc.gettext(end_prev_token, p+1).strip()
                if s:
                    if s[-1] in self.OPERATORS:
                        # current token begin just after operator.
                        return True
                    else:
                        return False


            if tokenizer is not _tokenizer:
                return True

            if not token:
                return True

            if token not in ignore_tokens:
                return False

            p = prev-1

        return True

    def on_start(self, tokenizer, doc, pos, match):
        if not self._is_regex(tokenizer, doc, pos):
            # This '/' is not regex, but divide operator
            ret = yield from tokenizer.tokens.punctuation.on_start(
                tokenizer, doc, pos, match)
            return ret
        else:
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
                     'string1', 'string2', 'regex', 'punctuation'])

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

    punctuation = SingleToken('javascript-punctuation', 'default',
                               [r'[+\-*/~&?:|=%;<>^(){}[],:'])


    tokens = JSTOKENS(
        stop, keywords, number, comment1, comment2, string1, string2,
        regex, punctuation)

    return Tokenizer(tokens, terminates=terminates)


class JavaScriptMode(defaultmode.DefaultMode):
    MODENAME = 'JavaScript'

    def init_themes(self):
        super().init_themes()
        self.themes.append(JavaScriptThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]
