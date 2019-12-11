from abc import ABC

import tornado.web
import mysql_db
import tornado.httpclient
import json


class get_wechat_open_id_handler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def post(self):
        body = self.request.body.decode("utf-8")
        json_obj = json.loads(body)
        str_appid = json_obj["appid"]
        str_secret = json_obj["secret"]
        str_code = json_obj["code"]
        url = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&grant_type=authorization_code&js_code=%s" % (
        str_appid, str_secret, str_code)

        # 必须要用异步的请求 同步请求应该会阻塞当前的客服端的请求
        http = tornado.httpclient.AsyncHTTPClient()

        try:
            result = yield http.fetch(url)
        except tornado.httpclient.HTTPError as e:
            print(e)
        else:
            print(result.body)
            open_id = json.loads(result.body)["openid"]
            self._response(open_id)

    def _response(self, str_open_id):
        result = mysql_db.db_connect_singleton().is_register(str_open_id)
        result_obj = {"openid":str_open_id,"is_register": result}
        str_json = json.dumps(result_obj)
        print("获取openid接口返回", str_json)
        self.write(str_json)
        self.finish()


# 注册 - 登录
# 已经注册过就下发联系人列表 没有注册 就进行注册 下发空列表

class register_handler(tornado.web.RequestHandler):
    def post(self):
        body = self.request.body.decode('utf-8')
        mysql_db.db_connect_singleton().register(body)
        self.write("注册成功")


# 获取联系人列表
class get_content_list_handler(tornado.web.RequestHandler):
    def post(self):
        body = self.request.body.decode('utf-8')
        print("获取联系人列表请求参数", body)
        result_json_str = mysql_db.db_connect_singleton().get_content_index_list(body)
        self.write(result_json_str)
        self.finish()
        pass


# 添加联系人
class add_content_handler(tornado.web.RequestHandler):
    def post(self):
        body = self.request.body.decode('utf-8')
        print("添加联系人请求参数", body)
        result = mysql_db.db_connect_singleton().add_content(body)
        if result is None:
            self.write("{\'error_code\': 80000,\'error_msg\':\'db error or data error\'}")
            pass
        else:
            self.write("{\"content_id\":%d}" % result)
            pass

        pass

    pass


# 获取联系人信息
class get_content_info_handler(tornado.web.RequestHandler):
    def post(self):
        body = self.request.body.decode('utf-8')
        result_json_str = mysql_db.db_connect_singleton().get_content_info(body)
        self.write(result_json_str)
        pass

    pass


# 删除联系人
class delete_content_handler(tornado.web.RequestHandler):
    def post(self):
        body = self.request.body.decode('utf-8')
        result = mysql_db.db_connect_singleton().delete_content(body)
        if result is True:
            self.write("{\'error_code\': 0,\'error_msg\':\'删除成功\'}")
            pass
        else:
            self.write("{\'error_code\': -1,\'error_msg\':\'删除失败\'}")
            pass
        print("删除联系人请求参数", body)

        pass

    pass


# 修改联系人
class modify_content_handler(tornado.web.RequestHandler):
    def post(self):
        body = self.request.body.decode('utf-8')
        result = mysql_db.db_connect_singleton().modify_content_info(body)
        if result is True:
            self.write("{\'error_code\': 0,\'error_msg\':\'删除成功\'}")
            pass
        else:
            self.write("{\'error_code\': -1,\'error_msg\':\'删除失败\'}")
            pass
        pass

    pass
