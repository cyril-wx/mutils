# server.py
# -*- coding:utf-8 -*-

# -*- coding:utf-8 -*-

from tornado.web import Application, RequestHandler, url
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
import tornado.options
import json
import redis

#定义全局变量
tornado.options.define('port',default=8000,type=int,help="The port for application")


class IndexHandler(RequestHandler):
    def get(self):
        self.write("<a href='"+self.reverse_url("login")+"'>用户登录</a>")


class RegistHandler(RequestHandler):
    def initialize(self, title):
        self.title = title

    def get(self):
        self.write("注册业务处理:" + str(self.title))


class LoginHandler(RequestHandler):
    def get(self):
        json_str = {"username": "admin", "password": "123123"}
        self.write(json.dumps(json_str))

    def post(self):
        self.write("用户登录功能处理")

class HomeHandler(RequestHandler):
    def get(self):
        # 获取get方式传递的参数
        username = self.get_query_argument("username")

        self.write("首页展示 username:{}".format(username))

    def post(self):
        # 获取post方式传递的参数
        username = self.get_body_argument("username")

        self.write("首页功能处理 username:{}".format(username))


class ErrorHandler(RequestHandler):
    # override
    def get(self):
        self.write("Welcome to chinared.com")
        self.send_error(404, msg="页面丢失", info="家里服务器搞对象去了")

    # override
    def write_error(self, status_code, **kwargs):
        self.write("<h1>出错啦，工程师GG/MM正在赶来的途中...</h1>")
        self.write("<p>错误信息:%s</p>" % kwargs["msg"])
        self.write("<p>错误描述:%s</p>" % kwargs["info"])


class FactorialService(object):

    def __init__(self):
        self.cache = redis.StrictRedis("localhost", 6379)  # 缓存换成redis了
        self.key = "factorials"

    def calc(self, n):
        s = self.cache.hget(self.key, str(n))  # 用hash结构保存计算结果
        if s:
            return int(s), True
        s = 1
        for i in range(1, n):
            s *= i
        self.cache.hset(self.key, str(n), str(s))  # 保存结果
        return s, False

class FactorialHandler(RequestHandler):

    service = FactorialService()
    def get(self):
        n = int(self.get_argument("n") or 1)  # 参数默认值
        fact, cached = self.service.calc(n)
        result = {
            "n": n,
            "fact": fact,
            "cached": cached
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))


if __name__ == "__main__":
    app = Application(
        [
            (r"/", IndexHandler),
            (r"/regist", RegistHandler, {"title": "会员注册"}),
            (r"/home", HomeHandler),
            (r"/factorial", FactorialHandler),
            (r"/error", ErrorHandler),
            url(r"/login", LoginHandler, name="login"),
        ], debug=True
    )

    http_server = HTTPServer(app)
    #http_server.listen(port=tornado.options.options.port)

    # 实现多线程
    http_server.bind(port=tornado.options.options.port )
    http_server.start(1)

    # 启动Ioloop轮循监听
    IOLoop.current().start()
