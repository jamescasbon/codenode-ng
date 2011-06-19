import os
import asyncore
from websocket import WebSocket


boot = """
import sys
from engine.server import EngineRPCServer
from engine.interpreter import Interpreter
from engine import runtime
namespace = runtime.build_namespace
port = int(sys.argv[1])
server = EngineRPCServer(('localhost', port), Interpreter, namespace)
runtime.ready_notification(port)
server.serve_forever()
"""

pi_boot = """
from engine.runtime import pi_boot_fn
pi_boot_fn()
"""

def pi_boot_fn():
    def my_msg_handler(msg):
        print 'Got "%s"!' % msg

    socket = WebSocket('ws://localhost:8888/enginebus/were', onmessage=my_msg_handler)
    socket.onopen = lambda: socket.send('Hello world!')

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        socket.close()


def build_namespace():
    # from codenode.engine.introspection import introspect
    # try:
    #     import matplotlib
    #     matplotlib.use('Agg')
    #     from codenode.external.mmaplotlib import codenode_plot
    #     # from pylab import *
    #     USERNAMESPACE = locals()
    #     USERNAMESPACE.update({"show":codenode_plot.show, "introspect":introspect})
    # except ImportError:
    #     USERNAMESPACE={"introspect":introspect}
    return {}

def find_port():
    import socket
    s = socket.socket()
    s.bind(('',0))
    port = s.getsockname()[1]
    s.close()
    del s
    return port

def ready_notification(port):
    """The backend process manager expects to receive a port number on
    stdout when the process and rpc server within the process are ready.
    """
    import sys
    sys.stdout.write('port:%s' % str(port))

import os
import sys
import uuid
import base64
from StringIO import StringIO

try: 
    import pylab
    import matplotlib
    
    # 10 inches * 72 dpi gives 720px wide
    matplotlib.rcParams['figure.figsize'] = (10, 7)
    # cache pylab's original show function
    _original_show = pylab.show

    import matplotlib.backends.backend_svg
    matplotlib.backends.backend_svg.svgProlog = """<svg width="%ipx" height="%ipx" viewBox="0 0 %i %i"
       xmlns="http://www.w3.org/2000/svg"
       xmlns:xlink="http://www.w3.org/1999/xlink"
       version="1.1"
       id="svg1">
    """

    def show(fn=None, *args, **kwargs):
        s = StringIO()
        pylab.savefig(s, dpi=200, format='svg', **kwargs)
        # coded = base64.b64encode(s.getvalue())
        # data = "__imgstart__data:image/png;base64," + coded + "__imgend__"
        sys.stdout.write(s.getvalue(), escape=False)
        pylab.close()
    pylab.show = show
except ImportError: 
    raise
    pass