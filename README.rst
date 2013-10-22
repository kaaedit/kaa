============================
Kaa - console text editor
============================

Kaa is a small and easy CUI text editor for console/terminal emulator environments.

.. contents::


Overview
============

Kaa is a easy yet powerful text editor for console user interface, providing numerous features like 

- Macro recording.

- Undo/Redo.

- Multiple windows/frames.

- Syntax highlighting.

- Grep.

- Open source software(MIT).

- More to come!


Kaa is easy!
------------

Kaa is very easy to learn in spite of its rich functions. Only thing you need to remember is **"To display menu, hit F1 key or alt+'/' key"**. Most of basic feartures could be accessed from fancy menus by hitting underlined character in the menu items. You can use kaa as easy as you are with Notepad on MS-Windows.


Customizable
------------

Kaa is written in `Python <http://www.python.org/>`_. So, you can easily customize many aspects of kaa through simple Python scripts.


Supported environment
---------------------

Kaa is a CUI editor that runs on most of modern UN*X flavor operating systems like Linux or Mac OS X. Kaa requires Unicode friendly environment both platform running kaa and terminal emulator/console to interact with kaa.

Cygwin environment on Windows platform is not supported at this time, but will be tested after they provide Python 3.3 package.


Requirements
============

* Python 3.3 or later

* Headers and libraries for Python and ncurses with wide character support. Consult documentation of your platform for details. For Debian/Ubuntu, you can install ncurses library by ::

  $ sudo apt-get install python3-dev libncursesw5-dev 

* UTF-8 locales

* (optional) Cython


Installation
============

Use easy_install3 or pip3 to install kaa from PyPI ::

   $ easy_install3 kaaedit


Command line options
====================

To start kaa, type ::

   $ kaa [-h] [--version] [FILE [FILE ...]]

   optional arguments:
     -h, --help  show this help message and exit
     --version show version info and exit
      
Terminal setting
================

For Mac OS X
-------------

Kaa uses alt keys for keyboard shortcut like `alt+W` for copy to clipboard. On most of recent Windows or Linux terminal, alt key works just fine. But on Mac OS X, Terminal app should be configured:

1. Select Preferences menu.
2. Open the Settings tab.
3. Open the keyboard tab.
4.  Check `Use option as meta key`.

Or, if you use iTerm on Mac, you should configure:

1. Select Preferences menu.
2. Open the Profiles tab.
3. Open the Keys tab.
4. Check `Left option Key acts as: +Esc.` button.

For Gnome Terminal(Ubuntu, etc.,)
----------------------------------

If you use Gnome terminal and wishes to access menu by F1 key, you should configure:

1. Select Edit | Keyboard shortcuts menu.
2. Scroll to the Help/Contents shortcut and change key from F1 to some another key.


Usage
=====

Using kaa is intuitive. Typing alphabet keys will update file as you expected. Functional keys like arrow or delete keys also works.


Using menu
-----------

To display menu, type F1 key or alt+/ (type slash key with alt key). Each items in the menu has one underlined character. The menu item is execused by typing the underlined key.

Typing escape key hides menu.


File menu
++++++++++

New
   Create new file.

Open
   Open existing file.

File info
   Show file information. Also update per file editor settings of tab/indentation.

Save
   Save current file.

Save As
   Save current file as new file.

Close
   Close current frame.

Save All
   Save all current files.

Close All
   Close all frames.

Recently
    Show recently used files menu.

Quit
   Terminate kaa.


Recently used files memu
~~~~~~~~~~~~~~~~~~~~~~~~

Recently used files
    Show list of recently used files.

Recently used dirs.
    Show list of recently used directories.


Edit menu
+++++++++

Cut
   Cut selected text.

Copy
   Copy selected text.
   
Paste
   Paste from clipboard.

Undo
   Undo last modification.

Redo
   Redo last undo.

Search
    Search text.
    
Replace
    Replace text.

Convert
    Show text convert menu


Text convert menu
~~~~~~~~~~~~~~~~~~~~

Upper
    Convert selected text to upper case.

Lower
    Convert selected text to lower case.

Normalization
    Convert selected text to Unicode Normalization Forms(NFKC).

Full-width
    Convert alphabet and numbers in the selected text to full-width character.


Code memu
+++++++++

Comment
    Insert line comment character at top of lines in selected regin.
    
Uncomment
    Delete line comment character at top of lines in selected regin.


Macro menu
++++++++++

Start record
   Start macro recording.

End record
   End macro recording.

Run macro
   Run last macro.


Tools menu
++++++++++

Paste lines
   Insert lines of text without auto indentation.

Shell command
   Execute external shell command and insert the output.

Grep
   Search text from disk.


Window menu
+++++++++++

Frame list
   Show list of frame windows. Use left/right arrow key to change active frame.

Split vert
   Split current window vertically.

Split horz
   Split current window horizontally.

Move separator
   Move window separator. Use left/right arrow key to move separator.

Next window
   Activate next window.

Join window
   Join splitted window.

Switch file
   Switch content of active window.


Key bindings
------------

Input mode
+++++++++++

F1, alt+/
   Show menu.

Arrow keys(up, down, left, right)
   Move cursor.

Shift+arrow keys
   Select text.

Control+left/right arrow keys
   Move cursor to next/prev word boundary.

Control+b, Control+f, Control+p, Control+n
   Move cursor to left/right/up/down.

Alt+b, Alt+f
   Move cursor to next/prev word boundary.

Control+v, Alt+v
    Page down/up

Home, Shift+Home
   Move cursor to top of line. Shift+Home selects text to top of line.

End, Shift+End
   Move cursor to end of line. Shift+Home selects text to end of line.

Control+Home, Control+Shift+Home
   Move cursor to top of file. Control+Shift+Home selects text to top of file.

Control+End, Control+Shift+End
   Move cursor to end of file. Control+Shift+End selects text to end of file.

Control+g
   Go to line number.

Alt+a
   Select all text.

Ctrl+c
   Select current word for first press, current line for second time and entire text for third time.

Backspace, Control+h
   Delete the character to the left.

Delete, Control+d
   Delete the character at the cursor.

Control+backspace, Alt+h
   Delete the word to the left.

Control+Delete, Alt+d
   Delete the word to the right.

Control+k
   Delete the line to the right.

Alt+k
   Delete the current line.

Control+y
   Paste

Control+w
   Cut selection

Alt+w
   Copy selection

Control+u
   Undo last change.

Alt+u
   Redo last undo.

F6
   Toggle macro recording on/off.

F5
   Run macro.

Alt+.
   Run last execused edit command again.

Control+s
   Search text.

Alt+s
   Replace text.

F2
    Search prev

F3
    Search next

Tab, Shift+Tab
   Indent/dedent selection

Alt-M v
    Show text conversion menu.

Ctrl+u Alt+!
    Execute command and insert the output.


Replace dialog
--------------

When `regex` button is checked, `Replace` string is also regular expression string. In this case, special characters like `\\t` or `\\n` are converted to tab character and newline character. Also, backreference character will be replaced to substring matched group in the search string. For example, when search string is `'(a+)(b+)'` and replace string is `\2\1`,  matched string `aabb` will be replaced to `bbaa`.


Grep dialog
------------

Grep dialog has three input field. `Search` is a plain text or regular expression string to search. `Directory` is a directory to start searching. If `Tree` button was checked, files are searched recursively. `Filenames` is space separeted list of file spec in shell-style wildcards (e.g., `*.txt *.py *.doc`). Up arrow key displays history of each input field.

In the grep result window, use F9 and F10 key to traverse matches forward/backward. 

Customization
==================

Kaa executes a Python script file at `~/.kaa/__kaa__.py` on startup. You can write Python script to customize kaa as you like.


Sample - Show line numbers
----------------------------------

.. code:: python

   from kaa.filetype.default import defaultmode
   defaultmode.DefaultMode.SHOW_LINENO = True

`defaultmode.DefaultMode` is base class of all text file types. Line number is diplayed if `Defaultmode.SHOW_LINENO` is True. If you want to show line number of paticular file types, you can update SHOW_LINENO attribute of each file type classes.

.. code:: python

   # Show line number in HTML mode
   from kaa.filetype.html import htmlmode
   htmlmode.HTMLMode.SHOW_LINENO = True

Sample - Customize key binding
----------------------------------

Assign same keyboard shortcut of splitting windows command as Emacs.

.. code:: python

    from kaa.keyboard import *
    from kaa.filetype.default.defaultmode import DefaultMode
    
    DefaultMode.KEY_BINDS.append({
       ((ctrl, 'x'), '2'): 'editor.splithorz'    # Assign C-x 2 
    })
   
In this example, key sequence C-x 2 (control+x followed by 2) is assigned to 'editor.splithorz' command.


Links
==========

- `Github project page <http://kaaedit.github.io/>`_

- `Github repository <http://github.com/kaaedit/kaa>`_

- `Python Package Index(PyPI) <http://pypi.python.org/pypi/kaaedit/>`_


Version history
=================

0.2.0 - 2013.10.20
------------------

- Comment/Uncomment region.

- In replace dialog, replace-to text is now treated as regular expression text.

- A lot of bugs fixed.


0.1.0 - 2013.10.14
------------------

- Grep

- Various improvements.


0.0.4 - 2013.10.11
------------------

- New command: Close all.

- New command: Recently used file/directory.

- Search/Replace history.

- Line number display setting at menu|File|File Info.


0.0.3 - 2013.10.9
-----------------

- Incremental search.

- Accept directory name as command line argument.

- New command: Go to line(^g).

- New command: Select current word(^c).

- New command: Save all files(menu|file|Save All).

- Improve file open dialog.


0.0.2 - 2013.10.5
-----------------

- Misc commands.

- Highlight parenthesis at cursor.

- Support text encodnig other than utf-8.

- Other a lot of changes.


0.0.1 - 2013.6.16
-----------------

- Initial release.

        
Copyright 
=========================

Copyright (c) 2013 Atsuo Ishimoto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
