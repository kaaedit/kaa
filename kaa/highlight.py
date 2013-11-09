from gappedbuf import re as gre
import collections

class Token:
    def __init__(self, name, stylename):
        self.name = name
        self.stylename = stylename

    def prepare(self, tokenizer):
        """Called to setup tokenizer"""
        self.tokenids = {}

    def re_start(self):
        """Returns regular expression to find begging of token"""

    def on_start(self, tokenizer, doc, pos, match):
        """Called when token started. Yield (pos, posto, tokenid)
        until exhausted"""

    def get_tokenids(self, highlighter, tokenizer):
        return tuple(self.tokenids.keys())

    def resume_pos(self, highlighter, tokenizer, doc, pos):
        # Returns top of current keyword
        if 0 < pos < len(doc.styles):
            p = doc.styles.rfindint(
                self.get_tokenids(highlighter, tokenizer),
                0, pos, comp_ne=True)
            if p != -1:
                return p+1
        return 0

    def assign_tokenid(self, tokenizer, stylename):
        tokenid = tokenizer.register_tokenid(self)
        self.tokenids[tokenid] = stylename
        return tokenid

    def get_stylename(self, tokenid):
        return self.tokenids[tokenid]


class SingleToken(Token):
    def __init__(self, name, stylename, tokens):
        super().__init__(name, stylename)
        self.tokens = tokens

    def re_start(self):
        return r'({})'.format('|'.join(self.tokens))

    def prepare(self, tokenizer):
        super().prepare(tokenizer)

        self.tokenid = self.assign_tokenid(tokenizer, self.stylename)

    def on_start(self, tokenizer, doc, pos, match):
        yield (match.start(), match.end(), self.tokenid)
        return match.end(), None, False


class Keywords(SingleToken):
    """Keyword tokens:
        ex) KeyWords('keyword', 'kwdstyle', keywords=['def', 'class', 'return'])
    """

    def re_start(self):
        return r'\b({})\b'.format('|'.join(gre.escape(k) for k in self.tokens))


class Span(Token):
    def __init__(self, name, stylename, start, end, escape=None,
            capture_end=True):
                
        super().__init__(name, stylename)

        self.start = start
        self.escape = escape
        if escape:
            end = '({}.)|({})'.format(gre.escape(escape), end)
        self.end = gre.compile(end, gre.X+gre.M+gre.S)
        self._capture_end = capture_end
        
    def prepare(self, tokenizer):
        super().prepare(tokenizer)

        self.span_start = self.assign_tokenid(tokenizer, self.stylename)
        self.span_mid = self.assign_tokenid(tokenizer, self.stylename)
        self.span_end = self.assign_tokenid(tokenizer, self.stylename)

    def re_start(self):
        return self.start

    def _is_end(self, doc, m):
        return True
        
    def on_start(self, tokenizer, doc, pos, match):
        yield (match.start(), match.end(), self.span_start)

        for m in self.end.finditer(doc.buf, match.end()):
            if self.escape and m.group(1) is not None:
                continue

            if match.end() != m.start():
                if not self._is_end(doc, m):
                    continue
                yield (match.end(), m.start(), self.span_mid)
            
            if self._capture_end:
                yield (m.start(), m.end(), self.span_end)
                end = m.end()
            else:
                end = m.start()
                
            return end, None, False

        else:
            yield (match.end(), doc.endpos(), self.span_mid)
            return doc.endpos(), None, False

class SubTokenizer(Token):
    def __init__(self, name, start, tokenizer):
        super().__init__(name, '')
        self.start = start

        self.subtokenizer = tokenizer

    def prepare(self, tokenizer):
        super().prepare(tokenizer)

        self.sub_tokens = {}
        self.tokenizer = tokenizer
        self.subtokenizer.prepare(self)

    def register_tokenid(self, tokenizer, token):
        ret = self.tokenizer.highlighter.register_tokenid(self.tokenizer, self)
        self.sub_tokens[ret] = token
        return ret

    def re_start(self):
        return self.start

    def iter_subtokenizers(self, tokenizer, doc, pos, match):
        pos, tok = yield from self.subtokenizer.start(doc, pos)
        return pos, None, False

    def on_start(self, tokenizer, doc, pos, match):
        ret = yield from self.iter_subtokenizers(tokenizer, doc, pos, match)
        return ret

    def resume_pos(self, highlighter, tokenizer, doc, pos):
        # Returns top of current keyword
        if 0 < pos < len(doc.styles):
            p = doc.styles.rfindint(tuple(self.sub_tokens.keys()), 0, pos, comp_ne=True)
            if p > 0:
                return highlighter.get_resume_pos(doc, p)
        return 0

    def get_stylename(self, tokenid):
        token = self.sub_tokens[tokenid]
        if token:
            return token.get_stylename(tokenid)
        else:
            return 'default'


class SubSection(Token):
    def __init__(self, name, stylename, start, tokenizer):
        super().__init__(name, stylename)

        self.start = start
        self.tokenizer = tokenizer

    def prepare(self, tokenizer):
        super().prepare(tokenizer)
        self.section_start = self.assign_tokenid(tokenizer, self.stylename)

    def re_start(self):
        return self.start

    def on_start(self, tokenizer, doc, pos, match):
        yield (match.start(), match.end(), self.section_start)
        return match.end(), self.tokenizer, False


class EndSection(Token):
    def __init__(self, name, stylename, end):
        super().__init__(name, stylename)

        self.end = end

    def prepare(self, tokenizer):
        super().prepare(tokenizer)

        self.section_end = self.assign_tokenid(tokenizer, self.stylename)

    def re_start(self):
        return self.end

    def on_start(self, tokenizer, doc, pos, match):
        yield (match.start(), match.end(), self.section_end)
        return match.end(), None, True


class Tokenizer:
    re_starts = None
    def __init__(self, tokens, terminates=None):

        self.groupnames = {}
        self.tokens = tokens
        self.terminates = terminates

    def prepare(self, highlighter):
        self.highlighter = highlighter
        self.nulltoken = self.register_tokenid(None)

        starts = []
        for i, token in enumerate(self.tokens):
            if not token:
                continue
            token.prepare(self)
            start = token.re_start()
            if start:
                name = 'G{}'.format(i)
                self.groupnames[name] = token
                starts.append(r'(?P<{}>{})'.format(name, start))

        if self.terminates:
            starts.insert(0, r'(?P<{}>{})'.format('TERMINATE', self.terminates))
            self.groupnames['TERMINATE'] = None

        if starts:
            self.re_starts = gre.compile('|'.join(starts), gre.M+gre.X)

    def register_tokenid(self, obj):
        return self.highlighter.register_tokenid(self, obj)

    def start(self, doc, pos):
        if self.re_starts:
            while True:
                m = self.re_starts.search(doc.buf, pos)
                if not m:
                    break

                f, t = m.span()
                if f != pos:
                    yield (pos, f, self.nulltoken)
                    pos = f

                if m.lastgroup == 'TERMINATE':
                    return f, None

                token = self.groupnames[m.lastgroup]

                pos, childtokenizer, close = yield from token.on_start(
                                                self, doc, pos, m)
                if close:
                    return pos, None

                if childtokenizer:
                    return pos, childtokenizer

        if pos != doc.endpos():
            yield (pos, doc.endpos(), self.nulltoken)
            pos = doc.endpos()

        return pos, None


class Section:
    parent = None
    end = None
    def __init__(self, pos, tokenizer):
        self.start = pos
        self.children = []
        self.tokenizer = tokenizer

    def walk(self):
        # traverse tree with depth first order
        stack = collections.deque([self])
        while stack:
            v = stack.pop()
            yield v
            stack.extend(reversed(v.children))

    def add(self, child):
        self.children.append(child)
        child.parent = self

    def get_section(self, pos):
        secs = list(self.walk())
        for sec in reversed(secs):
            if sec.start <= pos:
                if sec.end is None or pos < sec.end:
                    return sec
        return secs[0]

    def delete_after(self, pos):
        for n, c in enumerate(self.children):
            if pos < c.start:
                del self.children[n:]
                break
        section = self.get_section(pos)

        while section.parent:
            idx = section.parent.children.index(section)
            del section.parent.children[idx+1:]
            section = section.parent

class Highlighter:
    def __init__(self, tokenizers):
        self.tokenizers = tokenizers
        self.max_tokenid = 1
        self.tokenids = {}

        for tokenizer in self.tokenizers:
            tokenizer.prepare(self)

        self.section = None
        self.updatepos = 0
        self._highlighter = None

    def close(self):
        self._highlighter = self.section = self.tokenizer = None

    def register_tokenid(self, tokenizer, token):
        tokenid = self.max_tokenid
        self.max_tokenid += 1

        self.tokenids[tokenid] = (tokenizer, token)
        return tokenid

    def get_token(self, tokenid):
        if tokenid in self.tokenids:
            return self.tokenids[tokenid][1]

    def update_style(self, doc, batch=None):
        #todo: store 'doc' as attribute
        if not self._highlighter:
            self._highlighter = self.highlight(doc, self.updatepos)

        updatefrom = doc.endpos()
        updateto = 0
        updated = False
        try:
            for n, (start, end, style) in enumerate(self._highlighter):
                updated = True
                updatefrom = min(start, updatefrom)
                updateto = max(end, updateto)
                doc.styles.setints(start, end, style)
                if batch and (n > batch):
                    return True
            else:
                return False
        finally:
            if doc.endpos() == 0 or updated and (updatefrom != updateto):
                doc.style_updated(updatefrom, updateto)
                self.updatepos = updateto
                
    def highlight(self, doc, pos):
        if not self.tokenizers:
            return

        if not self.section:
            pos = 0
            section = Section(0, self.tokenizers[0])
            self.section = section
        else:
            self.section.delete_after(pos)
            section = self.section.get_section(pos)

        section.end = None
        while section:
            pos, childtokenizer = yield from section.tokenizer.start(doc, pos)
            if childtokenizer:
                childsection = Section(pos, childtokenizer)
                section.add(childsection)
                section = childsection
            else:
                section.end = pos
                section = section.parent

    def get_resume_pos(self, doc, pos):
        if pos == 0:
            return pos

        # check a character proceeding to updated pos
        pos -= 1
        style = doc.styles.getints(pos, pos+1)[0]
        if style == 0:
            # not highlighted yet.
            p = doc.styles.rfindint([0], 0, pos, comp_ne=True)
            if p != -1:
                return p+1
            return 0

        pair = self.tokenids.get(style)
        if not pair:
            # Invalid. this style is not set by tokenizer.
            return 0

        tokenizer, token = self.tokenids.get(style)
        if not token:
            p = doc.styles.rfindint([style], 0, pos, comp_ne=True)
            if p != -1:
                return p+1
            return 0

        return token.resume_pos(self, tokenizer, doc, pos)

    def updated(self, doc, pos, inslen, dellen):
        if pos <= self.updatepos:
            self.updatepos = self.get_resume_pos(doc, pos)
            self._highlighter = None
