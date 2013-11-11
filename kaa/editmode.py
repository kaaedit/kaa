import kaa
import string

class EditMode:
    MODENAME = 'Insert'

    pending_str = ''
    repeat = None
    repeat_str = ''

    def __init__(self):
        self.pending_keys = []
        self.last_command_keys = []

    def activated(self, wnd):
        pass

    def flush_pending_str(self, wnd):
        if self.pending_str:
            pending = self.pending_str
            self.pending_str = ''
            wnd.document.mode.on_str(wnd, pending)
            if not wnd.closed:
                wnd.update_window()
            return True

    def on_keyevent(self, wnd, event):
        if event.key == '\x1b' and event.no_trailing_char:
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
        self.pending_str += s

    def on_key_pressed(self, wnd, event):
        s, commands, candidate = self._get_command(wnd, event)
        s, commands, candidate = wnd.document.mode.on_keypressed(
                                    wnd, event, s, commands, candidate)

        try:
            if s:
                self._on_str(wnd, s)
                del self.last_command_keys[:]

            elif commands:
                self.flush_pending_str(wnd)

                self.last_command_keys.append(self.pending_keys)
                del self.last_command_keys[:-3]

                wnd.document.mode.on_commands(wnd, commands)
        finally:
            if s or commands or not candidate:
                self.pending_keys = []

    def on_esc_pressed(self, wnd, event):
        self.pending_keys = []
        self.clear_repeat()
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
        if kaa.app.macro.is_recording():
            kaa.app.macro.record_repeatcount(None)

    def add_repeat_char(self, wnd, c):
        self.repeat_str += c
        try:
            self.set_repeat(int(self.repeat_str))
            if kaa.app.macro.is_recording():
                kaa.app.macro.record_repeatcount(self.repeat)
        except ValueError:
            self.init_repeat()

    def has_repeat(self):
        return self.repeat is not None

    def get_repeat(self):
        return self.repeat

    def set_repeat(self, n):
        self.repeat = n

class CommandMode(EditMode):
    MODENAME = 'Command'

    def on_key_pressed(self, wnd, event):
        # check if key is repeat count
        if not self.pending_keys:
            if (isinstance(event.key, str) and (event.key > '0') and
                    (event.key in string.digits)):

                self.add_repeat_char(wnd, event.key)
                return

        super().on_key_pressed(wnd, event)

    def _get_keybinds(self, wnd):
        return [wnd.document.mode.keybind_vi_commandmode, wnd.document.mode.keybind]

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

