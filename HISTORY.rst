Past versions
--------------


0.44.0 - 2015.6.7
++++++++++++++++++++++

- New file mode: INI file. [`PR #125 Contributed by hirokiky <https://github.com/kaaedit/kaa/pull/125>`_]

- New file mode: JSON file. [`PR #126 Contributed by hirokiky <https://github.com/kaaedit/kaa/pull/126>`_]


0.43.0 - 2015.5.10
++++++++++++++++++++++

- [HTML mode] Handle Javascript line (//) comments in HTML attributes/elements correctly.

- [Markdown mode] Highlight pre style(both indented block/Github style \`\`\` markup)

0.42.0 - 2015.4.5
++++++++++++++++++++++

- HTML highlighter respects type attribute of script element.

0.41.0 - 2015.3.25
++++++++++++++++++++++

- History of grep directory was not saved correctly.

0.40.0 - 2015.3.23
++++++++++++++++++++++

- [JavaScript mode] Fix highlighting of regex token.

- [JavaScript mode] Highlight parenthesis under cursor.

- Use xclip instead of xsel for clilpboard on Unix.

0.39.0 - 2014.3.18
++++++++++++++++++++++

- [Python console] Display time consumed to execute script.

- [Python console] Optimize text output.

0.38.0 - 2014.3.9
++++++++++++++++++++++

- [Python console] Multiline scripts could be edited in-place. Edit window is no longer displayed. To execute script, cursor must be located at end of script.

- [Python console] local namespace is shared among consoles.

0.37.0 - 2014.3.8
+++++++++++++++++++++

- Home directory was not expanded to open file in Grep window.

- Undo command in the macro was not worked properly.

- Command 'selection.curword` doesn't select Japanese word.

0.36.0 - 2014.1.29
+++++++++++++++++++++

- An Error raised when file open dialog displayed at startup was canceled. 
  `Reported by hirokiky <https://github.com/kaaedit/kaa/issues/115>`_

0.35.0 - 2014.1.24
+++++++++++++++++++++

- Impove highlighting of reStructuredText mode.

- Don't update mode class on saving file if ext part of filename is not changed.


0.34.0 - 2014.1.13
+++++++++++++++++++++

- Highlight regex literal in Javascipt mode.

- Impove auto indentation of Python mode.


0.33.0 - 2014.1.8
+++++++++++++++++++++

- new `kaa.addon` module to customize kaa.


0.32.0 - 2014.1.5
+++++++++++++++++++++

- Impove auto indentation of Python mode.

- Support vi-style repeat count in macro record and in repeating last change.


0.31.0 - 2014.1.3
+++++++++++++++++++++

- Cursor position was wrong at start up.

- Add some vi-like commands.


0.30.0 - 2014.1.1
+++++++++++++++++++++

- Fix error on reloading modified file.

- Highlight decorator in Python mode.

- Version check was failed.


0.29.0 - 2013.12.31
+++++++++++++++++++++

- Check for new release of kaa.


0.28.0 - 2013.12.31
+++++++++++++++++++++

- Improve file-save-as dialog.

- Interuppt Python script with ^C key while running script in Python console.

- Display empty lines like vim.


0.27.0 - 2013.12.29
+++++++++++++++++++++

- New command line option: --command, -x spefify kaa command id to execute on start up.

- Alt+m key now assigned as new preferred menu key instead of alt+/ because key sequence of alt+/ could be `misinterpreted by other applications <https://twitter.com/kefir_/status/416613392879611904>`_.

- Alt+^ moves cursor to first non-blank character of the line.


0.26.1 - 2013.12.28
+++++++++++++++++++++

- Fixed an error on file-save-as.


0.26.0 - 2013.12.27
+++++++++++++++++++++

- New command: Alt+m moves cursor to first non-blank character of the line.


0.25.0 - 2013.12.25
+++++++++++++++++++++

- Syntax highlight in Python console.


0.24.0 - 2013.12.24
+++++++++++++++++++++

- Spell checker


0.23.0 - 2013.12.21
+++++++++++++++++++++

- Improve Python console a lot.

- Breakpoints in Python debugger now works better.


0.22.0 - 2013.12.19
+++++++++++++++++++++

- Respect encoding declaration on loading/saving file in CSS mode.

- Button to send SIGINT to the debug target process.


0.21.0 - 2013.12.15
+++++++++++++++++++++

- Respect encoding declaration on loading/saving file in HTML/Python mode.

- Paste from OS clipboard didn't work on Mac.


0.20.0 - 2013.12.13
+++++++++++++++++++++

- Save clipboard history to disk.

- Python debugger: Display status of target process.


0.19.0 - 2013.12.11
+++++++++++++++++++++

- Support system clipboard.


0.18.0 - 2013.12.10
+++++++++++++++++++++

- Optimizations. Kaa responds quicker than previous version.

- Error highlighting JavaScript attribute in html mode was fixed.

- White space characters inserted by auto-indent are automatically removed if cursor moved to another position without entering a character.

- reStructuredText Mode: Non-ASCII punctuation marks were not recognized as separator of inline mark ups.


0.17.0 - 2013.12.06
+++++++++++++++++++++

- reStructuredText Mode: Recognize non-ASCII punctuation as separator of inline mark ups.

- Indent command: Don't indent blank line. (Contributed by `allanderek <https://github.com/kaaedit/kaa/pull/94>`_)

- Separate `kaadbg <https://pypi.python.org/pypi/kaadbg>`_ as new package.


0.16.0 - 2013.12.03
+++++++++++++++++++++

- Defer to save history information. Kaa now works much smoother than ever on PC with slow hard disk. 


0.15.1 - 2013.11.30
+++++++++++++++++++++

- Removed debugging code.


0.15 - 2013.11.29
+++++++++++++++++++++

- Python debugger now runs 20+ times faster than in 0.14.

- Highlight Python constant.


0.14 - 2013.11.27
+++++++++++++++++++++

- Experimental Python debugger.


0.13 - 2013.11.18
+++++++++++++++++++++

- New file mode: C language.

- New command: *[Tools] | Make*. Invoke ``make`` command to build and view output without leaving kaa.

- Move initial selection of Table Of Contents to current cursor position.


0.12 - 2013.11.16
+++++++++++++++++++++

- Show table of contents in Markdown mode. Hit Ctrl+t to display TOC.

- Show table of contents reStructuredText mode. Hit Ctrl+t to display TOC.

- Improve highlighting in Markdown mode.

- Bugs fixed.


0.11 - 2013.11.14
+++++++++++++++++++++

- Show table of contents in Python mode. Hit Ctrl+t to display TOC.

- Improve highlighting in reStructured mode.


0.10 - 2013.11.11
+++++++++++++++++++++

- Add 'japanese' encoding that detects text encoding from file.

- Specify text encoding to grep file.

- New commandline option: --no-init, --init-script, --palette, --term.

- New color palette: dark, light.


0.9 - 2013.11.9
+++++++++++++++++++++

- Markdown mode.

- reStructuredText mode.


0.8 - 2013.11.7
+++++++++++++++++++++

- View diff between original file and current buffer.

- Grep dialog now has 'Dir' button to select directory.
 
- Handle SIGTERM to restore terminal state before exit.

- Prompt to reload file when file modified by other process.


0.7 - 2013.11.5
+++++++++++++++++++++

- Paste from clipboard history.

- Word completion list now contains text from clipboard history.

- New command: New file here.

- New command: Open file here.

- New command: Open recently used file here.

- New command: Open recently used directory here.


0.6 - 2013.11.1
+++++++++++++++++++++

- Basic word completion with ctrl+o.

- Display blank line if the line is selected.

- Various minor changes.


0.5 - 2013.10.30
+++++++++++++++++++++

- Locate position of opened file where the file located last time.

- Changed history database scheme. By this change, old history will be deleted.

- Changed default color setting.

- Kaa didn't run if $TERM is 'xterm-color'.


0.4 - 2013.10.27
+++++++++++++++++++++

- Rectangular selection can be started by Alt+'#' key.

- `Window|Join` menu caused error.

- `File|Save all` caused error.


0.3.1 - 2013.10.25
+++++++++++++++++++++

- Python console window now works with Gnome terminal.

- `Window|Switch file` menu caused error.

- ^G (Goto line number) dialog shouldn't accept '0' if field is empty.


0.3.0 - 2013.10.24
+++++++++++++++++++++

- Python console window.

- Emacs style region selection. Now you can select region by ctrl+SPACE or ctrl+'@'key.

- Changed some default keyboard binding.

- A lot of bugs fixed.


0.2.0 - 2013.10.20
+++++++++++++++++++++

- Comment/Uncomment region.

- In replace dialog, replace-to text is now treated as regular expression text.

- A lot of bugs fixed.


0.1.0 - 2013.10.14
+++++++++++++++++++++

- Grep

- Various improvements.


0.0.4 - 2013.10.11
+++++++++++++++++++++

- New command: Close all.

- New command: Recently used file/directory.

- Search/Replace history.

- Line number display setting at menu | File | File Info.


0.0.3 - 2013.10.9
+++++++++++++++++++++

- Incremental search.

- Accept directory name as command line argument.

- New command: Go to line(^g).

- New command: Select current word(^c).

- New command: Save all files(menu | file | Save All).

- Improve file open dialog.


0.0.2 - 2013.10.5
+++++++++++++++++++++

- Misc commands.

- Highlight parenthesis at cursor.

- Support text encoding other than utf-8.

- Other a lot of changes.


0.0.1 - 2013.6.16
+++++++++++++++++++++

- Initial release.
