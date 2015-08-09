import types
from kaa import doc_re

def begin_tokenizer(doc, root, updated):
    updated = min(updated, doc.endpos()-1)
    if updated >= 1:
        token = root.get_token_at(doc, updated)
        parents, pos = token.get_resume_pos(doc, updated)
        for parent in parents:
            pos = yield from parent.run(doc, pos)
        return pos
    else:
        pos = yield from root.run(doc, 0)
        return pos


class Token:
    styles = ()
    def __init__(self, stylename):
        self._stylename = stylename
        self._style_ids = []


    def register_styles(self, *names):
        l = self.tokenizer.get_styleid_map()
        for name in names:
            styleid = len(l)
            l[styleid] = self
            self._style_ids.append(styleid)
            setattr(self, name, styleid)

    def get_tokenizers(self):
        ret = []
        tokenizer = self.tokenizer
        while tokenizer:
            yield tokenizer
            tokenizer = tokenizer.parent

    def get_stylename(self, styleid):
        return self._stylename

    def get_resume_pos(self, doc, pos):
        return (list(self.get_tokenizers()),
            self.get_token_begin(doc, pos))

    def get_token_begin(self, doc, pos):
        p = doc.styles.rfindint(self._style_ids, 0, pos,
                                comp_ne=True)
        if p == -1:
            return 0
        else:
            return p+1

    def set_tokenizer(self, tokenizer):
        self.tokenizer = tokenizer
        self.prepare()

class DefaultToken(Token):
    def prepare(self):
        self.register_styles("styleid_default")

class Tokenizer:
    re_starts = None
    def __init__(self, parent, terminates, tokens=()):
        self.parent = parent
        self._terminates = terminates
        self._token_list = []
        self.tokens = types.SimpleNamespace()

        self.tokens.default = DefaultToken('default')
        self.tokens.default.set_tokenizer(self)
        self.styleid_default = self.tokens.default.styleid_default

        for name, token in tokens:
            self.add_token(name, token)

        self.prepare()


    def add_token(self, name, token):
        self._token_list.append(token)
        setattr(self.tokens, name, token)
        token.set_tokenizer(self)

    def get_styleid_map(self):
        if self.parent:
            return self.parent.get_styleid_map()
        else:
            return self.styleid_map

    def prepare(self):
        self.groupnames = {}
        starts = []
        for i, token in enumerate(self._token_list):
            start = token.re_start()
            if start:
                name = 'G{}'.format(i)
                self.groupnames[name] = token
                starts.append(r'(?P<{}>{})'.format(name, start))

        if self._terminates:
            starts.insert(
                0, r'(?P<{}>{})'.format('TERMINATE', self.terminates))
            self.groupnames['TERMINATE'] = None

        if starts:
            self.re_starts = doc_re.compile(
                '|'.join(starts),
                doc_re.M + doc_re.X)

    def resume(self, doc, updated):
        pos = yield from self.run(doc, updated)
        if self.parent:
            pos = yield from self.parent.run(doc, pos)
        return pos

    def run(self, doc, pos):
        if not self.re_starts:
            return doc.endpos()

        while True:
            m = self.re_starts.search(doc, pos)
            if not m:
                break

            f, t = m.span()
            if f != pos:
                yield (pos, f, self.styleid_default)
                pos = f

            if m.lastgroup == 'TERMINATE':
                return f

            child = self.groupnames[m.lastgroup]
            pos = yield from child.on_start(doc, m)

        if pos != doc.endpos():
            yield (pos, doc.endpos(), self.styleid_default)
            pos = doc.endpos()

        return pos

    def get_token_at(self, doc, pos):
        styleid = doc.styles.getints(pos, pos+1)[0]
        return self.get_styleid_token(styleid)

    def get_styleid_token(self, styleid):
        return self.get_styleid_map()[styleid]


class Root(Tokenizer):
    def __init__(self, tokens=()):
        self.styleid_map = {}
        super().__init__(None, '', tokens)


class SingleToken(Token):
    def __init__(self, stylename, tokens):
        super().__init__(stylename)
        self._tokens = tokens

    def prepare(self):
        self.register_styles("styleid_token")

    def re_start(self):
        return r'({})'.format('|'.join(self._tokens))

    def on_start(self, doc, match):
        yield (match.start(), match.end(), self.styleid_token)
        return match.end()


class Keywords(SingleToken):
    def re_start(self):
        return (
            r'\b({})\b'.format('|'.join(doc_re.escape(k) 
                for k in self._tokens))
        )



class Span(Token):

    def __init__(self, stylename, start, end, escape=None,
                 capture_end=True, terminates=None):

        self._start = start
        self._escape = escape
        self._end = end
        self._capture_end = capture_end
        self._terminates = terminates

        super().__init__(stylename)


    def prepare(self):
        self.register_styles(
            "styleid_begin", "styleid_mid", "styleid_end")

        end = self._end
        if self._terminates:
            end = '(?P<TERMINATES>{})|({})'.format(
                self._terminates, end)

        if self._escape:
            end = '(?P<ESCAPE>{}.)|({})'.format(
                doc_re.escape(self._escape), end)

        self._re_end = doc_re.compile(end, doc_re.X + doc_re.M + doc_re.S)

    def re_start(self):
        return self._start

    def _is_end(self, doc, m):
        return True

    def on_start(self, doc, match):
        pos = match.end()
        yield (match.start(), pos, self.styleid_begin)

        for m in self._re_end.finditer(doc, pos):
            if self._escape and m.group('ESCAPE') is not None:
                continue

            if not self._is_end(doc, m):
                continue

            if pos != m.start():
                yield (pos, m.start(), self.styleid_mid)

            if self._terminates and m.group('TERMINATES') is not None:
                return m.start()

            if self._capture_end:
                yield (m.start(), m.end(), self.styleid_end)
                return m.end()
            else:
                return m.start()
        else:
            yield (pos, doc.endpos(), self.styleid_mid)
            return doc.endpos()


#class HTMLTag(Token):
#    def on_start(self, doc, m, endpos):
#        angle_f, angle_t = m.span(1)
#        yield (angle_f, angle_t, self.styles.angle)
#
#        name_f, name_t = m.span(2)
#        if angle_t != name_f:
#            yield (angle_t, name_f, self.styles.null)
#
#        yield name_f, name_t, self.styles.elementname
#        pos = yield from self.run(doc, name_t, endpos, ns)
#
#        elemname = m.group(2).lower()
#        if elemname == 'script':
#            type = ns.attrs.get('type', '').lower().strip()
#            if not type or 'text/javascript' == type:
#                pos = yield from self.javascript.run(doc, pos, endpos)
#
#        elif elemname == 'style':
#            type = ns.attrs.get('type', '').lower().strip()
#            if not type or 'text/javascript' == type:
#                pos = yield from self.css.run(doc, pos, endpos)
#
#        return pos
#        
#
