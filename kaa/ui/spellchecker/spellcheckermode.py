import re
import enchant
import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import filterlist
from kaa.command import command, norec, norerun
from kaa.keyboard import *
import gappedbuf.re
from kaa.ui.wordcomplete import wordcompletemode
from kaa.ui.selectlist import filterlist


class SpellCheckerWordInputMode(wordcompletemode.WordCompleteInputMode):
    MAX_INPUT_HEIGHT = 4
    INITIAL_MESSAGE = "Hit tab/shift+tab to complete."

    @classmethod
    def build(cls, target):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)
        mode.target = target

        with dialogmode.FormBuilder(doc) as f:
            f.append_text('caption', 'Select word:')
            f.append_text('default', ' ')
            f.append_text('default', '', mark_pair='query')
            f.append_text('default', ' ')

            f.append_text('right-button', '[&Register]',
                          shortcut_style='right-button.shortcut',
                          on_shortcut=mode.register)

            f.append_text('right-button', '[&Skip]',
                          shortcut_style='right-button.shortcut',
                          on_shortcut=mode.skip)

            f.append_text('right-button', '[&Quit]',
                          shortcut_style='right-button.shortcut',
                          on_shortcut=mode.quit)

        return doc

    def on_edited(self, wnd):
        filterlist.FilterListInputDlgMode.on_edited(self, wnd)

    def register(self, wnd):
        self.pwl.add(self.word)
        if self.callback:
            self.callback(self.wordpos[1])

        wnd.get_label('popup').destroy()

    def skip(self, wnd):
        if self.callback:
            self.callback(self.wordpos[1])

        wnd.get_label('popup').destroy()

    def quit(self, wnd):
        wnd.get_label('popup').destroy()

    def start(self, wnd, list, f, t, word, pwl):
        self.orgloc = self.target.get_cursor_loc()
        self.orgpos = self.target.cursor.pos
        self.wordpos = (f, t)
        self.word = word
        self.pwl = pwl

        list.document.mode.set_candidates(pwl.suggest(word))
#        list.document.mode.candidates.sort(key=lambda v: v.text.upper())
        list.document.mode.set_query(list, '')

        list.get_label('popup').on_console_resized()


def show_suggests(wnd, f, t, s, pwl, callback):
    # select current word
    wnd.activate()
    wnd.cursor.setpos(t, middle=True)
    wnd.screen.selection.set_range(f, t)
    wnd.update_window()

    # todo: refactor
    doc = SpellCheckerWordInputMode.build(wnd)
    doc.mode.orgloc = wnd.get_cursor_loc()
    doc.mode.callback = callback

    if doc.mode.orgloc[0] > (wnd.mainframe.height // 2):
        doc.mode.stack_upper = True
    else:
        doc.mode.stack_upper = False

    dlg = kaa.app.show_dialog(doc)

    filterlistdoc = wordcompletemode.WordCompleteList.build()
    filterlistdoc.mode.SEP = ' '
    list = dlg.add_doc('dlg_filterlist', 0, filterlistdoc)

    doc.mode.start(wnd, list, f, t, s, pwl)

    return dlg


RE_WORD = gappedbuf.re.compile(r"\b[a-zA-Z][a-z']{2,}\b", gappedbuf.re.A)


def iter_words(wnd):
    d = enchant.DictWithPWL("en_US", kaa.app.config.spellchecker_pwl)

    pos = 0
    while True:
        m = RE_WORD.search(wnd.document.buf, pos)
        if not m:
            return

        f, t = m.span()
        s = wnd.document.gettext(f, t)
        if d.check(s):
            pos = t
            continue

        pos = yield (f, t, s, d)


def run_spellchecker(wnd):
    words = iter_words(wnd)

    def callback(pos):
        if pos is None:
            return

        try:
            f, t, s, d = words.send(pos)
            show_suggests(wnd, f, t, s, d, callback)
        except StopIteration:
            pass

    rec = next(words, None)
    if rec:
        f, t, s, d = rec
        show_suggests(wnd, f, t, s, d, callback)
