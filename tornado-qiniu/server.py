#!/usr/bin/env python
from qiniu import Auth
from tornado.options import define, options

import os.path
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json

define("port", default=8666, help="run on the given port", type=int)

qiniu_setting = {
    'ACCESS_KEY': '3rer6DB4jKt2CqSVzBjNmAC3NQe4s_LkK5PuOB4s',
    'SECRET_KEY': 'vmwWsF8_EEoiB9mJPYuKDKvoVvkGn0AwdfFBWXlM',
    'BUCKET_NAME': 'fbttest',
    'UPTOKEN_URL': '/uptoken',
    'CALLBACK_URL': 'http://www.friendsbt.com:8666/res/education/upload',
    'DOMAIN': 'http://7xipy9.com1.z0.glb.clouddn.com/'
}

'''
qiniu_setting = {
    'ACCESS_KEY': 'TODO MODIFY',
    'SECRET_KEY': 'TODO MODIFY',
    'BUCKET_NAME': 'TODO MODIFY',
    'UPTOKEN_URL': '/uptoken',
    'DOMAIN': 'TODO MODIFY'
}
'''

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/uptoken", TokenHandler),
            (r"/res/education/upload", EduResourceUploadHandler),
            (r"/res/education/list", EduResourceListHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False, # HTTP 403: Forbidden ('_xsrf' argument missing from POST)
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = {} # just a mock of database

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class HomeHandler(BaseHandler):
    def get(self):
        self.render('index.html',domain=qiniu_setting["DOMAIN"], uptoken_url=qiniu_setting["UPTOKEN_URL"])

class TokenHandler(BaseHandler):
    def get(self):
        auth = Auth(qiniu_setting['ACCESS_KEY'], qiniu_setting['SECRET_KEY'])
        # if policy is None, you will add a callback in browser js client. else you will add processing logic in callback url server.
        # policy = None
        policy = {  "callbackUrl": qiniu_setting["CALLBACK_URL"],
                    "callbackBody" : "file_name=$(fname)&file_hash=$(etag)&file_size=$(fsize)&uid=123"
                 }
        token = auth.upload_token(qiniu_setting['BUCKET_NAME'],policy=policy)
        self.write(json.dumps({'uptoken': token}))

class EduResourceUploadHandler(BaseHandler):
    def post(self):
        # token = self.get_argument("token")
        # user = self.get_argument("user")
        file_name = self.get_argument("file_name", None)
        file_size = self.get_argument("file_size", None)
        file_hash = self.get_argument("file_hash", None)

        """
        Sometimes your application will be behind a proxy, for example if you use nginx and UWSGI and
        you will always get something like 127.0.0.1 for the remote IP. In this case you need to
        check the headers too, like:
        """
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = self.request.remote_ip if not x_real_ip else x_real_ip
        uid = self.get_argument("uid", remote_ip)
        try:
            assert len(file_name) > 0
            file_size = long(file_size)
            assert file_size > 0
            assert len(file_hash) > 0
            self.db[file_name]={"size": file_size, "hash": file_hash, "name": file_name, "uid": uid, "link": qiniu_setting["DOMAIN"]+file_name}
            self.write(json.dumps({"error": 0, "key":file_name, "hash":file_hash}))
        except Exception as e:
            self.write(json.dumps({"error": 1, "content": e.message}))

class EduResourceListHandler(BaseHandler):
    def get(self):
        #self.write(json.dumps(self.db))
        self.render('resource_list.html',db=self.db)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
