import pymongo, hashlib

con = pymongo.Connection("localhost", 27017)

c1 = r"""Text Cells
==========

This is the input box of a text cell.  This text is is written in markdown.
When this cell is evaluated, the text with be processed and HTML output will
appear beneath it. To evaluate this cell, focus this input box and press CTRL-e or CMD-e 
or you just double click the cell.

Some nice equations
-------------------

We also have mathjax available to format latex style equations.
A dollar will give you inline equations, such as $e^i\pi +  1 = 0$.
Two dollars gives an equation block with the full power of mathjax!

$$
z 
\left( 
    1 + \sqrt{\omega_{i+1} + \zeta -\frac{x+1}{\Theta +1} y + 1} 
\right)
\ \ \ =\ \ \  1
$$"""

c2 = r"""# This is a python code block.  Execute it the same way as the text cell above
print "Hello, world!"
print 
import random
print "This is a random number and will change every time the cell is evaluated:"
print random.random()"""

c3 = """# This cell should be a code cell, but it has the wrong mode. You can see 
# which mode a cell is by the blue tab to the left of the notebook.
#
# You can change the mode by clicking CMD-m or CTRL-m.  Try it.

print "*" * 80""" 

c4 = """# Adding new cells
To add a new cell, you should focus the horizontal grey bar between the 
cells surrounding the position you want.  You can do this by clicking on it or by
using the cursor keys to move up and down the notebook.  When it is focused, 
you can press enter to insert a cell.
"""
c5 =r"""# Pylab demo.  Evaluate this cell to test pylab rendering.
from pylab import * 
x = arange(0, 2*pi, 0.01)
plot(x, sin(x))
plot(x, sin(2*x))
show()"""

# c1o = "<h1>Example codenode</h1>\n\n<p>Did you know that $e^i\\pi +  1 = 0$?</p>\n\n<p>The power of mathjax!</p>\n\n<p>$$<br />z <br />\\left( <br />    1 + \\sqrt{\\omega_{i+1} + \\zeta -\\frac{x+1}{\\Theta +1} y + 1} <br />\\right)<br />\\ \\ \\ =\\ \\ \\  1<br />$$</p>", "nbid" : "demo1", "mode" : "text", "input" : "# Example codenode\n\nDid you know that $e^i\\pi +  1 = 0$?\n\nThe power of mathjax!\n\n$$\nz \n\\left( \n    1 + \\sqrt{\\omega_{i+1} + \\zeta -\\frac{x+1}{\\Theta +1} y + 1} \n\\right)\n\\ \\ \\ =\\ \\ \\  1\n$$"

notebooks = {
    1: {'title': 'Tutorial', 'id': 'demo1'}
}

cells = [
    {'id': 'cell%s' % i, 'position': i*(2^16), 'nbid': 'demo1', 'mode': mode,
        'input': inp, 'output':'Please edit this notebook to use this tutorial'}
    for i, (inp, mode) in enumerate(zip([c1,c2,c3,c4,c5], 
        ['text', 'code', 'text', 'text', 'code']))
]
users = [
    {'user': "test", "password": hashlib.md5("test").hexdigest()}
]

db = con.codenode_dev.cells
db.drop()
for c in cells:
    db.save(c) 
    
db = con.codenode_dev.notebooks
db.drop()
for n in notebooks.values():
    db.save(n)
    
db = con.codenode_dev.users    
db.drop()
for u in users: 
    db.save(u)
