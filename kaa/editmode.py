import kaa
import string


class EditMode:
    MODENAME = 'Insert'

    pending_str = ''
    repeat = None
    repeat_str = ''

    _replace_str = False
    _key_hook = None
    _post_key_hook = None

    def __init__(self):
        self.pending_keys = []
        self.last_command_keys = []

    def install_keyhook(self, hook):
        self._key_hook = hook

    def install_post_key_hook(self, hook):
        self._post_key_hook = hook

    def activated(self, wnd):
        pass

    def flush_pending_str(self, wnd):
        if self.pending_str:
            pending = self.pending_str
            self.pending_str = ''
            wnd.document.mode.on_str(wnd, pending, self._replace_str)
            return True

    def on_keyevent(self, wnd, event):
        if self._key_hook:
            f = self._key_hook
            self._key_hook = None
            event = f(wnd, event)

        if not event:
            return

        if event.key == '\x1b' and not event.has_trailing_char:
            return self.on_esc_pressed(wnd, event)
        else:
            return self.on_key_pressed(wnd, event)

    def _get_keybinds(self, wnd):
        return [wnd.document.mode.keybind]

    def _get_command(self, wnd, event):
        self.pending_keys.append(event.key)
        candidates = [(keys, command)
                      for keybind in self._get_keybinds(wnd)
                      for keys, command
                      in keybind.get_candidates(self.pending_keys)]

        if not candidates:
            if len(self.pending_keys) == 1:
                if isinstance(event.key, str):
                    s = event.key
                    return s, None, candidates

        elif len(candidates[0][0]) == len(self.pending_keys):
            return None, candidates[0][1], candidates

        return None, None, candidates

    def _on_str(self, wnd, s):
        if not wnd.document.mode.DELAY_STR:
            self.flush_pending_str(wnd)

        for c in s:
            if c in '\t\r\n' or c >= ' ':
                self.pending_str += c

                if not wnd.document.mode.DELAY_STR:
                    self.flush_pending_str(wnd)

    def _keys_to_str(self, keys):
        ret = []
        alt = False
        for k in keys:
            if k == '\x1b':
                alt = True
            else:
                s = kaa.app.get_keyname(k)
                if alt:
                    s = 'alt-' + s
                    alt = False
                ret.append(s)
        return ret

    def _show_pending_keys(self, wnd, s, commands, candidates):
        if s or commands or not candidates or not self.pending_keys:
            msg = wnd.document.mode.DEFAULT_MENU_MESSAGE or kaa.app.DEFAULT_MENU_MESSAGE
            kaa.app.messagebar.set_message(msg)
        else:
            cur = self._keys_to_str(self.pending_keys)
            curlen = len(cur)

            nextkeys = set()
            for k, commands in candidates:
                keys = self._keys_to_str(k)
                if len(keys) > curlen:
                    nextkeys.add(keys[curlen:curlen + 1][0])

            msg = ' '.join(cur) + ' [%s]' % (', '.join(sorted(nextkeys)))
            kaa.app.messagebar.set_message(msg)

    def on_non_command_str(self, wnd, event, s):
        self._on_str(wnd, s)
        del self.last_command_keys[:]

    def on_key_pressed(self, wnd, event):
        s, commands, candidate = self._get_command(wnd, event)
        s, commands, candidate = wnd.document.mode.on_keypressed(
            wnd, event, s, commands, candidate)

        self._show_pending_keys(wnd, s, commands, candidate)
        try:
            if s:
                self.on_non_command_str(wnd, event, s)

            elif commands:
                self.flush_pending_str(wnd)

                self.last_command_keys.append(self.pending_keys)
                del self.last_command_keys[:-3]

                wnd.document.mode.on_commands(wnd, commands, self.get_repeat())
                self.clear_repeat()

        finally:
            if self._post_key_hook and (s or commands):
                f = self._post_key_hook
                self._post_key_hook = None

                # flush pending str before hook runs.
                self.flush_pending_str(wnd)
                event = f(wnd, s, commands)

            if s or commands or not candidate:
                self.pending_keys = []

    def on_esc_pressed(self, wnd, event):
        kaa.app.messagebar.set_message('')
        self.pending_keys = []
        self.clear_repeat()

        self._key_hook = None
        self._post_key_hook = None

        del self.last_command_keys[:]

        if not wnd.closed:
            self.flush_pending_str(wnd)

        if not wnd.closed:
            # cancel mark
            wnd.screen.selection.set_mark(None)

            wnd.document.mode.on_esc_pressed(wnd, event)

    def clear_repeat(self):
        self.repeat = None
        self.repeat_str = ''

    def add_repeat_char(self, wnd, c):
        self.repeat_str += c
        try:
            self.set_repeat(int(self.repeat_str))
        except ValueError:
            self.init_repeat()

    def has_repeat(self):
        return self.repeat is not None

    def get_repeat(self):
        return self.repeat or 1

    def set_repeat(self, n):
        self.repeat = n


class ReplaceMode(EditMode):
    MODENAME = 'Replace'
    _replace_str = True


class CommandMode(EditMode):
    MODENAME = 'Command'

    def on_non_command_str(self, wnd, event, s):
        is_available, command = wnd.document.mode.get_command(
            'editmode.insert')
        if command:
            self.flush_pending_str(wnd)
            command(wnd)
            wnd.document.mode.on_str(wnd, s, False)
        else:
            super().on_non_command_str(wnd, event, s)

    def on_key_pressed(self, wnd, event):
        # check if key is repeat count
        if not self.pending_keys:
            if (isinstance(event.key, str) and (event.key > '0') and
                    (event.key in string.digits)):
                self.add_repeat_char(wnd, event.key)
                return

            if (event.key == '0') and self.repeat_str:
                self.add_repeat_char(wnd, event.key)
                return

        super().on_key_pressed(wnd, event)

    def _get_keybinds(self, wnd):
        return [wnd.document.mode.keybind_vi_commandmode,
                wnd.document.mode.keybind]

    def flush_pending_str(self, wnd):
        self.pending_str = ''


class VisualMode(CommandMode):
    MODENAME = 'Visual'

    def _get_keybinds(self, wnd):
        return [wnd.document.mode.keybind_vi_visualmode]


class VisualLinewiseMode(CommandMode):
    MODENAME = 'Visual(Line)'

    def _get_keybinds(self, wnd):
        return [wnd.document.mode.keybind_vi_visuallinewisemode]
