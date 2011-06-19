#!/usr/bin/env python
# coding: utf-8
# Copyright 2009 Alexandre Fiori
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# requires cyclone:
#  http://github.com/fiorix/cyclone
# run:
#  twistd -ny cyclone_server.tac
import uuid
import txmongo
import cyclone.web
import cyclone.httpclient
from twisted.internet import defer
from twisted.application import service, internet

from mjson import json
from auth import BaseHandler, LoginHandler, LogoutHandler
from engine.interpreter import Interpreter
from engineserver import EngineHandler, EngineBus#, EvaluateHandler


class NotebooksHandler(BaseHandler):
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self):
        """ fetch list of notebooks """
        # TODO: restrict to user's permitted notebooks
        result = yield self.settings.notebook_db.find()
        
        if 'application/json' in self.request.headers.get('Accept', ''):        
            self.write(json.dumps(result))
            self.finish()
        
        else: 
            self.render('template/index.html', notebooks=result)
            
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def post(self):
        """ create a new notebook """
        cell = json.loads(self.request.body)
        cell['id'] = uuid.uuid1()
        result = yield self.settings.notebook_db.save(cell)
        self.write(json.dumps(result))


class NotebookHandler(BaseHandler):

    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self, nbid):
        """ fetch a notebook"""
        
        result = yield self.settings.notebook_db.find_one({'id': nbid})
        if not result:
            raise cyclone.web.HTTPError(404)    
        
        if 'application/json' in self.request.headers.get('Accept', ''):
            self.write(json.dumps(result))
            self.finish()
        else: 
            # TODO: order cells
            cells = yield self.settings.cell_db.find({'nbid': nbid})
            self.render('template/notebook.html', 
                title = result['title'],
                id = result['id'],
                cells = cells
            )
        
        
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def put(self, nbid):
        """ update a notebook """
        cell = json.loads(self.request.body)
        result = yield self.settings.notebook_db.save(cell)
        self.write("ok\n")


class CellsHandler(BaseHandler):
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self, nbid):
        """ fetch a list of cells """
        result = yield self.settings.cell_db.find({'nbid': nbid})
        self.write(json.dumps(result))
        self.finish()
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def post(self, nbid):
        """ create a cell """
        cell = json.loads(self.request.body)
        cell['id'] = str(uuid.uuid1())
        cell['nbid'] = nbid
        print 'new cell with id', cell['id']
        result = yield self.settings.cell_db.save(cell)
        self.write(json.dumps(result))


class CellHandler(BaseHandler):
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self, nbid, cid):
        """ fetch a cell """
        result = yield self.settings.cell_db.find_one({'nbid': nbid, 'id': cid})
        if not result:
            raise cyclone.web.HTTPError(404)
        self.write(json.dumps(result))
        self.finish()

    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def put(self, nbid, cid):
        """ update a cell """
        print self.request.body
        cell = json.loads(self.request.body)
        result = yield self.settings.cell_db.save(cell)
        self.write("ok\n")
        
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def delete(self, nbid, cid):
        """ update a cell """
        result = yield self.settings.cell_db.find_one({'nbid': nbid, 'id': cid})
        result = yield self.settings.cell_db.remove(result)
        self.write("ok\n")


class NewNotebookHandler(BaseHandler):
    # Temporary solution
    # TODO: replace with javascript POSTs to REST api
    
    @cyclone.web.authenticated
    @defer.inlineCallbacks
    def get(self):
        notebook = dict( 
            id = str(uuid.uuid1()),
            title = 'untitled'
        )
        cell = dict(
            id = str(uuid.uuid1()),
            nbid = notebook['id'],
            mode = 'code',
            input = '',
            output = '',
            position = 2^16
        )
        
        yield self.settings.notebook_db.save(notebook)
        yield self.settings.cell_db.save(cell)
         
        self.redirect('/static/index.html#notebook/%s' % notebook['id'])

class WebMongo(cyclone.web.Application):
    def __init__(self):
        handlers = [
            (r'/',                                      NotebooksHandler),
            (r"/auth/login",                            LoginHandler),
            (r"/auth/logout",                           LogoutHandler),
            (r"/notebooks/",                            NotebooksHandler),
            (r"/notebooks/new",                         NewNotebookHandler),
            (r"/notebooks/([\w-]+)",                     NotebookHandler),
            (r"/notebooks/([\w-]+)/cells",               CellsHandler),
            (r"/notebooks/([\w-]+)/cells/([\w-]+)",      CellHandler),
            (r"/engine/([\w-]+)",                        EngineHandler),
            # (r"/engine/(\w+)",                          EngineHandler),
            (r"/enginebus/(\w+)",                       EngineBus),
        ]

        mongo = txmongo.lazyMongoConnectionPool()
        settings = dict(
            cell_db= mongo.codenode_dev.cells,
            notebook_db= mongo.codenode_dev.notebooks,
            user_db= mongo.codenode_dev.users,
            static_path= "./static",
            login_url="/auth/login",
            cookie_secret="32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        )
        cyclone.web.Application.__init__(self, handlers, **settings)


application = service.Application("webmongo")
srv = internet.TCPServer(8888, WebMongo(), interface="127.0.0.1")
srv.setServiceParent(application)