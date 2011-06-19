######################################################################### 
# Copyright (C) 2007, 2008, 2009 
# Alex Clemesha <alex@clemesha.org> & Dorian Raymer <deldotdr@gmail.com>
# 
# This module is part of codenode, and is distributed under the terms 
# of the BSD License:  http://www.opensource.org/licenses/bsd-license.php
#########################################################################

"""
Trap for stdout and stderr of the python interpreter.
"""

import sys
import cgi 
from cStringIO import StringIO

class EscapingIO():

    def __init__(self, stream, klass='stdout'):
        self.stream = stream
        self.klass = klass
        
    def write(self, data, escape=True):
        if escape: 
            # self.stream.write('<pre class="%s">' % self.klass)
            self.stream.write(cgi.escape(data))
            # self.stream.write('</pre>')
        else: 
            self.stream.write(data)
        

class OutputTrap(object):

    def __init__(self):
        self.reset()

    def set(self):
        """Turn on trapping"""

        if sys.stdout is not self.out:
            sys.stdout = self.out

        if sys.stderr is not self.err:
            sys.stderr = self.err

    def unset(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def reset(self):
        """return the out and err.
        close the out and err buffers and open new ones.
        """
        self.out = EscapingIO(StringIO())
        self.err = EscapingIO(StringIO())
        self.unset()

    def get_value(self):
        """get the strings from the out and err buffers"""
        return self.out.stream.getvalue(), self.err.stream.getvalue()

