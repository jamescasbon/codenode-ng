import sys
import uuid
from twisted.web import xmlrpc
from mjson import json

import cyclone.web
from twisted.internet import defer
from twisted.runner import procmon

from mjson import json
from auth import BaseHandler
from engine import runtime


class EngineProcessManager(procmon.ProcessMonitor):

    engine_registry = {}

    @defer.inlineCallbacks        
    def start(self, eid):
        if eid in self.engine_registry: 
            result = 'already started'
        else: 
            port = runtime.find_port()
            self.engine_registry[eid] = xmlrpc.Proxy('http://localhost:%s' % port)
            result = yield self.addProcess(str(eid), [
                '/Users/james/Documents/virtualenvs/backplay/bin/python', '-c', runtime.boot, str(port)])
        defer.returnValue(result)
    
    @defer.inlineCallbacks
    def evaluate(self, eid, data):
        if eid not in self.engine_registry: 
            result =  'no engine'
        else: 
            proxy =  self.engine_registry[eid]
            result = yield proxy.callRemote('evaluate', data)
        defer.returnValue(result)
    
    def interrupt(self, eid):
        self.protocols[eid].transport.interrupt()

    def stop(self, eid):
        self.removeProcess(eid)

    def __del__(self):
        print 'stopping procmon'
        self.stopService()


manager = EngineProcessManager()
manager.startService()


class EngineHandler(BaseHandler):
    
    def get_engine_id(self, nbid):
        user =  json.loads(self.get_current_user())['user']
        return nbid + '/' + user
                
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def post(self, nbid):        
        eid = self.get_engine_id(nbid)
        data = json.loads(self.request.body)
        print eid, data
        if data['method'] == 'start':
            result = yield manager.start(eid)
        elif data['method'] == 'evaluate':
            result = yield manager.evaluate(eid, data['input'])
        elif data['method'] == 'interrupt':
            result = yield manager.interrupt(eid)
        elif data['method'] == 'stop':
            result = yield manager.stop(eid)
        self.write({'result': result})
        
        
class EngineBus(cyclone.web.WebSocketHandler):

    def evaluate(self, data):
        pass
        
    def connectionMade(self, *args, **kwargs):
        # engine_registry[self.request.remote_ip] = self
        print "connection made:", args, kwargs

    def messageReceived(self, message):
        # self.sendMessage("echo: %s" % message)
#        self.transport.loseConnection()
        print message
        
    def connectionLost(self, why):
        print "connection lost:", why
