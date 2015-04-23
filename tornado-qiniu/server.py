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

define("port", default=8888, help="run on the given port", type=int)

'''
qiniu_setting = {
    'ACCESS_KEY': '3rer6DB4jKt2CqSVzBjNmAC3NQe4s_LkK5PuOB4s',
    'SECRET_KEY': 'vmwWsF8_EEoiB9mJPYuKDKvoVvkGn0AwdfFBWXlM',
    'BUCKET_NAME': 'fbttest',
    'UPTOKEN_URL': '/uptoken',
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

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/uptoken", TokenHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)



class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html',domain=qiniu_setting["DOMAIN"], uptoken_url=qiniu_setting["UPTOKEN_URL"])


class TokenHandler(tornado.web.RequestHandler):
    def get(self):
        auth = Auth(qiniu_setting['ACCESS_KEY'], qiniu_setting['SECRET_KEY'])
        token = auth.upload_token(qiniu_setting['BUCKET_NAME'])
        self.write(json.dumps({'uptoken': token}))

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
