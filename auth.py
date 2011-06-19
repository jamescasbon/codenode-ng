#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
import hashlib
import txmongo
import cyclone.web
from twisted.python import log
from twisted.internet import defer, reactor

class BaseHandler(cyclone.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class LoginHandler(BaseHandler):
    def get(self):
        err = self.get_argument("e", None)
        self.finish("""
            <html><body><form action="/auth/login" method="post">
            username: <input type="text" name="u"><br>
            password: <input type="password" name="p"><br>
            <input type="submit" value="sign in"><br>
            %s
            </body></html>
        """ % (err == "invalid" and "invalid username or password" or ""))

    @defer.inlineCallbacks
    def post(self):
        u, p = self.get_argument("u"), self.get_argument("p")
        password = hashlib.md5(p).hexdigest()
        try:
            user = yield self.settings.user_db.find_one({"user":u, "password":password}, fields=["user"])
        except Exception, e:
            log.err("mongo can't find_one({u:%s, p:%s}): %s" % (u, password, e))
            raise cyclone.web.HTTPError(503)

        if user:
            user["_id"] = str(user["_id"])
            print 'setting user', user
            self.set_secure_cookie("user", cyclone.escape.json_encode(user))
            self.redirect("/")
        else:
            self.redirect("/auth/login?e=invalid")

class LogoutHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")

