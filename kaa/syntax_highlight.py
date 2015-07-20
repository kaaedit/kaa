from types import SimpleNamespace


def run(doc, root, pos, endpos):
    f, t, token = root.get_prev_token(pos)
    if token:
        root, *rest = token.get_path()
        yield from root.resume(rest, doc, f, endpos)
        return

    yield from root.run(doc, f, endpos)


class Token:
    def token_from_style(self, style):
        if style in self.styles:
            return self
        
        for c in self.children:
            token = c.get_token(style)
            if token:
                return

    def get_token_at(self, doc, pos):
        style = doc.styles.getints(pos, pos+1)[0]
        return self.token_from_style(style)

    def get_token_range(self, pos):
        pass

    def resume(self, path, doc, pos, endpos):
        f = self.get_token_start(doc, pos)
        return f
        yield None  # make this method a generator

    def run(self, doc, pos, endpos):
        if self.re_starts:
            while True:
                m = self.re_starts.search(doc, pos, endpos)
                if not m:
                    break

                f, t = m.span()
                if f != pos:
                    yield (pos, f, self.styles.null)
                    pos = f

                child = self.groupnames[m.lastgroup]
                pos = yield from child.on_start(doc, m, endpos)

        if pos != endpos:
            yield (pos, endpos, self.styles.null)
            pos = endpos

        return pos, None


class SingleToken(Tonen):

    def on_start(self, doc, m, endpos):
        yield (match.start(), match.end(), self.styles.token)
        return match.end()


class Tokenizer(Token):
    def resume(self, path, doc, pos, endpos):
        if path:
            root, *rest = path
            pos = yield from root.resume(rest, doc, pos, endpos)
        else:
            pos = self.get_token_start(doc, pos)

        pos = yield from self.run(doc, pos, endpos)
        return pos


class HTMLTag(Token):
    def on_start(self, doc, m, endpos):
        angle_f, angle_t = m.span(1)
        yield (angle_f, angle_t, self.styles.angle)

        name_f, name_t = m.span(2)
        if angle_t != name_f:
            yield (angle_t, name_f, self.styles.null)

        yield name_f, name_t, self.styles.elementname
        pos = yield from self.run(doc, name_t, endpos, ns)

        elemname = m.group(2).lower()
        if elemname == 'script':
            type = ns.attrs.get('type', '').lower().strip()
            if not type or 'text/javascript' == type:
                pos = yield from self.javascript.run(doc, pos, endpos)

        elif elemname == 'style':
            type = ns.attrs.get('type', '').lower().strip()
            if not type or 'text/javascript' == type:
                pos = yield from self.css.run(doc, pos, endpos)

        return pos
        

