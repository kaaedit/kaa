============================
Kaa - console text editor
============================

Kaa is a small and easy text editor for console environment.

.. DANGER::
   Kaa is still in the very early stage of the development. Don't use kaa for other purpose than evaluation.

.. contents::

Requirements
============

* Python 3.3 or later

* Headers and libraries for ncurses. Consult documentation of your platform for details. For Debian/Ubuntu, you can install ncurses library by ::

  $ sudo apt-get install libncurses-dev

* (optional) Cython

Installation
============

1. Get source from github ::

   $ git clone git@github.com:atsuoishimoto/kaa.git

2. Install kaa ::
   
   $ cd kaa
   $ python setup.py install

Command line options
====================

To start kaa, type ::

   $ kaa [FILE]...

Usage
=====

Using kaa is intuitive. Typing alphabet keys will update file as you expected. Functional keys like arrow or delete keys also works.

Using menu
-----------

To display menu, type F1 key or alt+/ (type slash key with alt key). Each items in the menu has one underlined character. The menu item is execused by typing the underlined key.

Typing escape key hides menu.

File menu
++++++++++

Open
   Open existing file.

Save
   Save current file.

Save As
   Save current file as new file.

Close
   Close current frame.

Quit
   Terminate kaa.


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


Macro menu
++++++++++

Start record
   Start macro recording.

End record
   End macro recording.

Run macro
   Run last macro.


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

F1, alt+/
   Show menu

Arrow keys
   Move cursor.

Shift+arrow keys
   Select text.

Control+left/right arrow keys
   Move cursor to next/prev word boundary.

Backspace
   Delete the character to the left.

Delete
   Delete the character at the cursor.

Control+z
   Undo last change.

Control+r
   Redo last undo.

F6
   Toggle macro recording on/off.

F5
   Run macro.

Control+S
   Search text.

Alt+S
   Replace text.

Control+b|Control+f|Control+p|Control+n
   Move cursor to left|right|up|down.

Alt+b|Alt+f
   Move cursor to next/prev word boundary.

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
