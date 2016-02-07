import enchant
import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import filterlist
from kaa.keyboard import *
from kaa import doc_re
from kaa.ui.wordcomplete import wordcompletemode


class SpellCheckerWordInputMode(wordcompletemode.WordCompleteInputMode):
    MAX_INPUT_HEIGHT = 4
    INITIAL_MESSAGE = "Hit tab/shift+tab to complete."

    @classmethod
    def build(cls, target):
        doc = document.Document()
        mode = cls()
        doc.setmode(mode)
        mode.target = target

        with dialogmode.FormBuilder(doc) as f:
            f.append_text('caption', 'Select word:')
            f.append_text('default', ' ')
            f.append_text('default', '', mark_pair='query')
            f.append_text('default', ' ')

            f.append_text('right-button', '[&Replace]',
                          shortcut_style='right-button.shortcut',
                          on_shortcut=mode.selected)

            f.append_text('right-button', '[&Add word]',
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

    def start(self, wnd, list, f, t, word, pwl, sugest):
        self.orgloc = self.target.get_cursor_loc()
        self.orgpos = self.target.cursor.pos
        self.wordpos = (f, t)
        self.word = word
        self.pwl = pwl

        list.document.mode.set_candidates(sugest)
        list.document.mode.set_query(list, '')

        list.get_label('popup').on_console_resized()


def show_suggests(wnd, f, t, s, pwl, sugest, callback):
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

    doc.mode.start(wnd, list, f, t, s, pwl, sugest)

    return dlg


RE_WORD = doc_re.compile(r"\b[a-zA-Z][a-z']{2,}\b", doc_re.A)


def iter_words(wnd, pos):
    d = enchant.DictWithPWL("en_US", kaa.app.config.spellchecker_pwl)

    while True:
        posto = wnd.document.marks['spellchecker'][1]
        m = RE_WORD.search(wnd.document, pos, posto)
        if not m:
            return

        f, t = m.span()
        s = wnd.document.gettext(f, t)
        if d.check(s):
            pos = t
            continue

        suggest = d.pwl.suggest(s)
        if not suggest:
            pos = t
            continue

        pos = yield (f, t, s, d, suggest)


def run_spellchecker(wnd):
    sel = wnd.screen.selection.get_selrange()
    if sel:
        pos, posto = sel
    else:
        pos, posto = 0, wnd.document.endpos()

    wnd.document.marks['spellchecker'] = (pos, posto)

    wnd.screen.selection.clear()
    words = iter_words(wnd, pos)

    def callback(new_pos):
        if new_pos is None:
            # canceled
            del wnd.document.marks['spellchecker']
            return

        try:
            f, t, s, d, sugest = words.send(new_pos)
            show_suggests(wnd, f, t, s, d, sugest, callback)
        except StopIteration:
            del wnd.document.marks['spellchecker']

    rec = next(words, None)
    if rec:
        f, t, s, d, sugest = rec
        show_suggests(wnd, f, t, s, d, sugest, callback)
