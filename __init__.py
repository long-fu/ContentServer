import tornado.web
import tornado.ioloop
import request_handler


class MainHandler(tornado.web.RequestHandler):
    def get(self):

        print("请求参数", self.request.body.decode('utf-8'))
        self.write("hello my name is hao shuai")

    pass


def make_app():
    print("start success, register handler")
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/get_open_id', request_handler.get_wechat_open_id_handler),
        (r'/register', request_handler.register_handler),
        (r'/add_content', request_handler.add_content_handler),
        (r'/delete_content', request_handler.delete_content_handler),
        (r'/modify_content', request_handler.modify_content_handler),
        (r'/get_content_index_list', request_handler.get_content_list_handler),
        (r'/get_content_info', request_handler.get_content_info_handler),
    ])
    pass


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    pass
