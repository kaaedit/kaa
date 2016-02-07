import os
import curses
import subprocess
import signal
import time
import kaa
from kaa import document
from kaa.command import Commands
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun


class ToolCommands(Commands):

    @commandid('python.console')
    @norerun
    def pythonconsole(self, wnd):
        from kaa.ui.pyconsole import pythonconsolemode
        pythonconsolemode.show_console()

    @commandid('python.debugger.run')
    @norerun
    def pythonchilddebugger(self, wnd):
        from kaa.ui.pythondebug import port
        port.run()

    @commandid('python.debugger.server')
    @norerun
    def pythondebuggerserver(self, wnd):
        from kaa.ui.pythondebug import port
        port.init_server()

    @commandid('command.rerun')
    @norerun
    def reruncommand(self, wnd):
        mode = wnd.document.mode
        if not kaa.app.lastcommands:
            return
        n_repeat, commandids = kaa.app.lastcommands
        wnd.set_command_repeat(n_repeat)
        try:
            for cmdid in commandids:
                is_available, command = mode.get_command(cmdid)
                if not command:
                    msg = 'command {!r} is not registered.'.format(cmdid)
                    kaa.app.messagebar.set_message(msg)
                    kaa.log.error(msg)
                    return
                command(wnd)
        finally:
            wnd.set_command_repeat(1)

    @commandid('edit.paste-lines')
    @norerun
    def edit_pastelines(self, wnd):
        from kaa.ui.pastelines import pastelinesmode
        doc = pastelinesmode.PasteLinesMode.build(wnd)

        kaa.app.show_dialog(doc)

    @commandid('tools.execute-shell-command')
    @norerun
    def execute_shell_command(self, wnd):
        def callback(w, s):
            s = s.strip()
            if s:
                kaa.app.config.hist('shellcommand').add(s)
                ret = subprocess.check_output(
                    s, stderr=subprocess.STDOUT,
                    shell=True,
                    universal_newlines=True)

                wnd.document.mode.put_string(wnd, ret)
                wnd.screen.selection.clear()

                kaa.app.messagebar.set_message(
                    "{} letters inserted".format(len(ret)))

        hist = [s for s, info in kaa.app.config.hist('shellcommand').get()]
        from kaa.ui.inputline import inputlinemode
        doc = inputlinemode.InputlineMode.build('Shell command:',
                                                callback, history=hist)
        kaa.app.messagebar.set_message('Execute shell command')

        kaa.app.show_dialog(doc)

    def _exec_cmd(self, cmd):
        # todo: move to util
        import select
        import errno
        # http://stackoverflow.com/a/12207447
        # This page sujests bare os pipes is never buffered.
        # Is it true? Looks works fine, though.
        master, slave = os.pipe()
        # todo: Make these handles not inherited in Python 3.3.
        with subprocess.Popen(cmd, shell=True, stdout=slave,
                              stderr=slave, bufsize=1,
                              universal_newlines=True) as process:

            os.close(slave)

            output = os.fdopen(master)
            try:
                lines = []
                while process.poll() is None:
                    rlist, _, _ = select.select([master], [], [])
                    for f in rlist:
                        l = output.readline()
                        lines.append(l)
                        print(l, end='')
            finally:
                output.close()

            retcode = process.poll()
            if retcode:
                code = errno.errorcode.get(retcode)
                if code:
                    code = '(%s):' % code
                else:
                    code = ''

                msg = os.strerror(retcode)
                kaa.app.messagebar.set_message(
                    '{code}{msg}'.format(
                        code=code, msg=msg, retcode=retcode))

            return ''.join(lines)

    @commandid('tools.make')
    @norerun
    def execute_make(self, wnd):
        def callback(w, s):
            s = s.strip()
            if s:
                kaa.app.config.hist('makecommand').add(s)
                # todo: move these lines to kaa.cui.*
                curses.def_prog_mode()
                curses.endwin()
                try:
                    ret = self._exec_cmd(s)
                finally:
                    curses.reset_prog_mode()
                    wnd.mainframe.refresh()

                from kaa.ui.makeoutput import makeoutputmode
                makeoutputmode.show(s, ret)

        from kaa.ui.inputline import inputlinemode
        hist = [s for s, info in kaa.app.config.hist('makecommand').get()]
        value = 'make' if not hist else hist[0]
        doc = inputlinemode.InputlineMode.build('Make command:', callback,
                                                history=hist, value=value)
        kaa.app.messagebar.set_message('Execute command')

        kaa.app.show_dialog(doc)

    @commandid('tools.spellchecker')
    @norec
    @norerun
    def spellchecker(self, wnd):
        try:
            pass
        except ImportError:
            kaa.app.messagebar.set_message(
                'PyEnchant module is not installed.')
            return

        from kaa.ui.spellchecker import spellcheckermode
        spellcheckermode.run_spellchecker(wnd)

    @commandid('tools.grep')
    @norec
    @norerun
    def showgrep(self, wnd):
        from kaa.ui.grep import grepdlgmode

        doc = document.Document()
        mode = grepdlgmode.GrepDlgMode(wnd)
        doc.setmode(mode)
        mode.build_document()

        kaa.app.show_dialog(doc)

    @commandid('tools.suspend')
    @norec
    @norerun
    def suspend(self, wnd):
        with kaa.app.restore_teminal():
            os.kill(os.getpid(), signal.SIGSTOP)
            time.sleep(0.01)  # sleep to ensure signal derivered
