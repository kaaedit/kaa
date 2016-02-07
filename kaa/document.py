import contextlib
import weakref
import gappedbuf


def is_combine(c):
    if (('\u0300' <= c <= '\u036f') or  # Combining Diacritical Marks
            # Combining Diacritical Marks Supplement
            ('\u1dc0' <= c <= '\u1dff') or
            # Combining Diacritical Marks for Symbols
        ('\u20d0' <= c <= '\u20ff') or
            ('\ufe20' <= c <= '\ufe2f')):  # Combining Half Marks

        return True


class LineNo:

    def __init__(self):
        self.buf = gappedbuf.GappedBuffer()

    def linecount(self):
        return len(self.buf) + 1

    def lineno(self, pos):
        return self.bisect_left(pos) + 1

    def getpos(self, lineno):
        if lineno <= len(self.buf):
            return self.buf.getint(lineno - 1)

    def bisect_left(self, pos):
        lo = 0
        hi = len(self.buf)

        while lo < hi:
            mid = (lo + hi) // 2
            if self.buf.getint(mid) < pos:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def inserted(self, pos, s):
        idx = 0
        lfs = []
        while True:
            idx = s.find('\n', idx)
            if idx == -1:
                break
            else:
                lfs.append(pos + idx)
            idx += 1

        lno = self.bisect_left(pos)
        self.buf.insertints(lno, lfs)

        d = len(s)
        for p in range(lno + len(lfs), len(self.buf)):
            self.buf.setints(p, p + 1, self.buf.getint(p) + d)

    def deleted(self, delfrom, delto):
        lno = self.bisect_left(delfrom)
        for idx in range(lno, len(self.buf)):
            pos = self.buf.getint(idx)
            if pos >= delto:
                break
        else:
            idx = len(self.buf)

        if lno != idx:
            self.buf.delete(lno, idx)

        d = delto - delfrom
        for p in range(lno, len(self.buf)):
            pos = self.buf.getint(p)
            d = min(delto, pos) - delfrom
            self.buf.setints(p, p + 1, pos - d)


class Buffer(gappedbuf.GappedBuffer):

    def __init__(self):
        self.listeners = []
        self.lineno = LineNo()

    def close(self):
        del self.listeners
        del self.lineno

    def insert(self, index, s):
        super().insert(index, s)
        self.lineno.inserted(index, s)
        self._updated(index, len(s), 0)

    def delete(self, begin, end):
        super().delete(begin, end)
        self.lineno.deleted(begin, end)
        self._updated(begin, 0, end - begin)

    def replace(self, begin, end, s):
        super().replace(begin, end, s)
        self.lineno.deleted(begin, end)
        self.lineno.inserted(begin, s)
        self._updated(begin, len(s), end - begin)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def _updated(self, pos, inslen, dellen):
        for listener in self.listeners:
            listener(self, pos, inslen, dellen)


class Document:
    all = weakref.WeakSet()  # should not be used!
    temporary = False
    closed = False
    fileinfo = None

    @classmethod
    def find_filename(cls, filename):
        for doc in cls.all:
            if doc.get_filename() == filename:
                return doc

    def __init__(self, buf=None):
        self.wnds = []
        self.all.add(self)

        if buf is None:
            buf = Buffer()
        self.buf = buf
        self.buf.add_listener(self.updated)

        self.styles = gappedbuf.GappedBuffer()
        if len(self.buf):
            self.styles.insertints(0, [0] * len(self.buf))

        self.undo = Undo()
        self.marks = Marks()
        self.mode = None

        self.title = ''

    def add_window(self, wnd):
        self.wnds.append(wnd)
        self.mode.on_add_window(wnd)

    def del_window(self, wnd):
        self.mode.on_del_window(wnd)
        self.wnds.remove(wnd)
        if self.mode.CLOSE_ON_DEL_WINDOW:
            if not self.wnds:
                self.close()

    def close(self):
        """Close this document"""
        assert not self.wnds

        self.closed = True
        del self.wnds

        self.mode.close()
        self.buf.close()

        self.marks = self.buf = self.mode = None
        self.all.remove(self)

    def use_undo(self, is_useundo):
        if is_useundo:
            if not self.undo:
                self.undo = Undo()
        else:
            self.undo = None

    @contextlib.contextmanager
    def undo_group(self):
        if self.undo:
            self.undo.beginblock()
        yield None
        if self.undo:
            self.undo.endblock()

    def set_title(self, title):
        self.title = title

    def get_title(self):
        title = '<untitled>'

        if self.title:
            title = self.title
        elif self.fileinfo and self.fileinfo.filename:
            title = self.fileinfo.filename

        return title

    def get_filename(self):
        filename = ''
        fileinfo = self.fileinfo
        if fileinfo:
            filename = fileinfo.fullpathname
        return filename

    def setmode(self, mode):
        if self.mode:
            self.mode.close()

        self.mode = mode
        mode.on_set_document(self)

    def updated(self, buf, pos, inslen, dellen):
        """Called when document updated"""

        if inslen:
            style = 0
            if 0 < pos <= len(self.styles):
                style = self.styles.getints(pos - 1, pos)[0]
            self.styles.replaceints(pos, pos + dellen, [style] * inslen)
        else:
            self.styles.delete(pos, pos + dellen)

        self.marks.updated(pos, inslen, dellen)
        self.update_screen(pos, inslen, dellen)

    def update_screen(self, pos, inslen, dellen):
        for wnd in self.wnds:
            wnd.on_document_updated(pos, inslen, dellen)

        if self.mode:
            self.mode.on_document_updated(pos, inslen, dellen)

    def style_updated(self, posfrom=0, posto=None):
        if posto is None:
            posto = self.endpos()

        for wnd in self.wnds:
            wnd.style_updated(posfrom, posto)

    def endpos(self):
        """Returns end position of this document(=size of document)."""
        return len(self.buf)

    def findchr(self, pos, chars):
        return self.buf.findchr(chars, pos, len(self.buf))

    def gettol(self, pos):
        """Returns top of line at pos"""

        if pos == 0:
            return 0
        tol = self.buf.rfindchr('\n', 0, pos)
        return 0 if tol == -1 else tol + 1

    def get_line_to(self, pos):
        eol = self.buf.findchr('\n', pos, len(self.buf))
        if eol == -1:
            eol = len(self.buf)
        return eol

    def _findeol(self, pos):
        """Find next occurrence of newline"""

        eol = self.buf.findchr('\n', pos, len(self.buf))
        if eol != -1:
            eol += 1
        return eol

    def geteol(self, pos):
        """Returns top of next line or end of buffer"""

        eol = self._findeol(pos)
        if eol == -1:
            eol = len(self.buf)
        return eol

    def gettext(self, begin, end):
        return self.buf[begin:end]

    def getstyles(self, begin, end):
        return self.styles.getints(begin, end)

    def getline(self, pos):
        """Returns tuple of eol and string"""

        eol = self._findeol(pos)
        if eol == -1:
            return (len(self.buf), self.buf[pos:])
        else:
            return (eol, self.buf[pos:eol])

    def get_line_break(self, pos):
        eol = self.buf.findchr('\n', pos, len(self.buf))
        if eol == -1:
            return len(self.buf)
        return eol

    def iterlines(self, pos):
        end = self.endpos()
        while pos < end:
            eol = self.geteol(pos)
            yield self.buf[pos:eol]
            pos = eol

    def insert(self, pos, s, style=None):
        self.buf.insert(pos, s)
        if style is not None:
            self.styles.setints(pos, pos + len(s), style)

    def append(self, s, style=None):
        self.insert(self.endpos(), s, style)
        return self.endpos()

    def delete(self, begin, end):
        self.buf.delete(begin, end)

    def replace(self, begin, end, s, style=None):
        self.buf.replace(begin, end, s)
        if style is not None:
            self.styles.setints(begin, begin + len(s), style)

    def get_nextpos(self, pos):
        pos += 1
        while pos < self.endpos():
            if not is_combine(self.buf[pos]):  # skip combine char
                return pos
            pos += 1
        return self.endpos()

    def get_prevpos(self, pos):
        while pos:
            pos -= 1
            if not is_combine(self.buf[pos]):  # skip combine char
                break
        return pos

    def get_lineno_pos(self, lineno):
        # line number starts from one.

        if lineno >= self.buf.lineno.linecount():
            return self.endpos()
        else:
            return self.buf.lineno.getpos(lineno)

    def setstyles(self, start, end, style, update=True):
        self.styles.setints(start, end, style)
        if update:
            self.style_updated(start, end)


class Marks(dict):
    locked = False

    def updated(self, pos, inslen, dellen):

        # don't update mark if locked
        if self.locked:
            return

        size = inslen - dellen
        if size == 0:
            return
        elif size > 0:
            for name, markpos in self.items():
                if isinstance(markpos, int):
                    if pos < markpos:
                        self[name] = markpos + size
                elif markpos is not None:
                    f, t = markpos
                    if pos < f:
                        f = f + size
                    if pos <= t:
                        t = t + size
                    self[name] = (f, t)

#            updated = ((name, markpos+size) for name, markpos in self.items()
#                            if (markpos is not None) and (pos < markpos))
        elif size < 0:
            size = abs(size)
            for name, markpos in self.items():
                if isinstance(markpos, int):
                    if pos < markpos:
                        if pos + size > markpos:
                            self[name] = pos
                        else:
                            self[name] = markpos - size
                elif markpos is not None:
                    f, t = markpos
                    if pos < f:
                        if pos + size > f:
                            f = pos
                        else:
                            f = f - size
                    if pos < t:
                        if pos + size > t:
                            t = pos
                        else:
                            t = t - size
                    self[name] = (f, t)


#            updated = ((name, pos if (pos+size > markpos) else (markpos-size))
#                            for name, markpos in self.items()
#                                if (markpos is not None) and (pos < markpos))
#        for name, p in updated:
#            self[name] = p
class Undo:

    """Records edit history"""

    def __init__(self):
        self.clear()

    def _dump(self, lv=0):
        _trace('    ' * lv, '======================')
        for a in self._actions:
            _trace('    ' * lv, a)
            if isinstance(a[0], Undo):
                a[0]._dump(lv + 1)

    def clear(self):
        self._actions = []      # edit operations
        self._closed = False    # Closed group undo block
        self._saved = 0         # position when document saved
        self._next_undo = 0     # undo action to be executed at next

    def _getblock(self):
        if self._actions:
            action, args, kwargs = self._actions[-1]
            if isinstance(action, Undo) and not action._closed:
                return action._getblock()
        return self

    def beginblock(self):
        """Begin group undo block"""

        block = self._getblock()
        block._add(Undo())

    def endblock(self):
        """End current group undo block"""

        block = self._getblock()
        assert block is not self
        if not block.can_undo():
            # Nothing happend
            del self._actions[-1]
            self._next_undo = len(self._actions)
        else:
            block._closed = True

    def _add(self, action, *args, **kwargs):
        # Can not redo thereafter
        del self._actions[self._next_undo:]
        if self._saved > len(self._actions):
            self._saved = -1

        self._actions.append((action, args, kwargs))
        self._next_undo = len(self._actions)

    def add(self, action, *args, **kwargs):
        """Add edit action"""

        self._getblock()._add(action, *args, **kwargs)

    def saved(self):
        """Notifies document saved"""

        self._saved = self._next_undo

    def is_dirty(self):
        """Returns True if buffer modified"""

        return self._next_undo != self._saved

    def can_undo(self):
        """Returns True if undo action is not exhausted"""

        return self._next_undo != 0

    def can_redo(self):
        """Returns True if redo action is not exhausted"""

        return self._next_undo < len(self._actions)

    def undo(self):
        """Perform undo action"""

        action, args, kwargs = self._actions[self._next_undo - 1]
        self._next_undo -= 1

        if isinstance(action, Undo):
            yield from action.undo_all()
        else:
            yield action, args, kwargs

    def undo_all(self):
        while self.can_undo():
            yield from self.undo()

    def redo(self):
        """Perform redo action"""

        action, args, kwargs = self._actions[self._next_undo]
        self._next_undo += 1
        if isinstance(action, Undo):
            yield from action.redo_all()
        else:
            yield action, args, kwargs

    def redo_all(self):
        while self.can_redo():
            yield from self.redo()
