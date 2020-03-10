# -*- coding: utf-8 -*-

import threading
import mysql.connector
from mysql.connector import errorcode
import json
from datetime import date, datetime, timedelta




class db_connect_singleton(object):
    _instance_lock = threading.Lock()

    _db_connect_config = {
        'user': 'root',
        'password': '19920105',
        'host': '127.0.0.1',
        'database': 'content',
        'raise_on_warnings': True
    }

    _cnx = None

    def is_register(self, str_open_id):
        return self.__is_register(str_open_id)

    def __is_register(self,str_open_id):

        if not self.connect_open():
            print("数据库链接错误")
            return None

        cursor = self._cnx.cursor()
        # 插入替换 时间需要判读 不能进行每次的插如
        i_sql = ("replace into user_info(c_open_id,t_creation_time) VALUES (%s,%s);")
        now_datetime = datetime.now()
        i_values = (str_open_id,now_datetime)
        cursor.execute(i_sql,i_values)

        self._cnx.commit()

        query_sql = "select i_is_register from user_info where c_open_id = \'%s\';" % str_open_id
        cursor.execute(query_sql)

        # 查询联系人列表

        b_is_register = False
        for (i_is_register) in cursor:
            if i_is_register == 0:
                b_is_register = False
            else:
                b_is_register = True

        cursor.close()
        self._cnx.close()
        return b_is_register


    def register(self, str_userinfo):
        print("解析发过来的数据", str_userinfo)
        json_obj = json.loads(str_userinfo)
        str_open_id = json_obj["openid"]
        str_nike_name = json_obj["nickName"]
        num_gender = json_obj["gender"]
        str_language = json_obj["language"]
        str_city = json_obj["city"]
        str_province = json_obj["province"]
        str_country = json_obj["country"]
        str_avatar_url = json_obj["avatarUrl"]
        self.__register(str_open_id, str_nike_name, num_gender, str_language, str_city, str_province, str_country, str_avatar_url, '')
        pass

   # 注册接口需要后续进行调整
    def __register(self, str_open_id, str_nike_name, num_gender, str_language, str_city, str_province, str_country,
                   str_avatar_url, str_union_id):

        if not self.connect_open():
            print("数据库链接错误")
            return None

        cursor = self._cnx.cursor()
        now_datetime = datetime.now()
        add_user_info = (
            "replace into user_info"
            "(c_open_id, c_nike_name, i_gender, c_language, c_city, c_province, c_country, c_avatar_url, c_union_id, t_creation_time) "
            "VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        )

        data_user_info = (
            str_open_id, str_nike_name, num_gender, str_language, str_city, str_province, str_country, str_avatar_url,
            str_union_id, now_datetime)
        cursor.execute(add_user_info, data_user_info)
        last_id = cursor.lastrowid
        self._cnx.commit()
        cursor.close()
        self._cnx.close()
        return last_id

    def get_content_index_list(self, str_json):
        json_obj = json.loads(str_json)
        str_open_id = json_obj["open_id"]
        return self.__get_content_index_list(str_open_id)

    def __get_content_index_list(self, str_open_id):
        # 查询所有列表
        if not self.connect_open():
            print("数据库链接错误")
            return None

        cursor = self._cnx.cursor()
        query_sql = "select id, c_open_id, c_nike_name, c_avatar_url, c_phone_number from content_index where c_open_id = \'%s\' order by c_nike_name;" % str_open_id

        cursor.execute(query_sql)
        json_obj = []
        for (id, c_open_id, c_nike_name, c_avatar_url, c_phone_number) in cursor:
            print(id, c_open_id, c_nike_name, c_avatar_url, c_phone_number)
            item_obj = {"open_id": c_open_id, "content_id": id, "nike_name": c_nike_name, "avatar_url": c_avatar_url,
                        "phone_number": c_phone_number}
            json_obj.append(item_obj)

        cursor.close()
        self._cnx.close()
        str_json = json.dumps(json_obj)
        print("查询数据输出结果", str_json.encode('utf-8'))
        return str_json

    def get_content_info(self, str_json):
        json_obj = json.loads(str_json)
        content_id = json_obj["content_id"]

        num_content_id = int(content_id)
        return self.__get_content_info(num_content_id)

    def __get_content_info(self, num_content_id):
        # 查询所有列表
        if not self.connect_open():
            print("数据库链接错误")
            return None

        cursor = self._cnx.cursor()

        info_query_sql = "select c_nike_name, c_avatar_url,c_remark from content_index where id = %d;" % num_content_id
        cursor.execute(info_query_sql)
        json_obj = {}
        for (c_nike_name, c_avatar_url, c_remark) in cursor:
            json_obj = {"content_id": num_content_id,"nike_name": c_nike_name, "avatar_url": c_avatar_url, "remark": c_remark}

        number_query_sql = "select id,c_phone_type,c_phone_number from content_info where i_content_id = %d;" % num_content_id
        cursor.execute(number_query_sql)
        array = []
        for (id, c_phone_type, c_phone_number) in cursor:
            item_obj = {"info_id": id, "phone_type": c_phone_type, "phone_number": c_phone_number}
            array.append(item_obj)
        json_obj["array"] = array

        cursor.close()
        self._cnx.close()

        str_json = json.dumps(json_obj)
        return str_json

    # 添加联系人
    def add_content(self, str_content_info):
        try:
            json_obj = json.loads(str_content_info)
            str_open_id = json_obj["open_id"]
            str_nike_name = json_obj["nike_name"]
            str_avatar_url = json_obj["avatar_url"]
            str_remark = json_obj["remark"]
            str_phone_number = json_obj["array"][0]["phone_number"]
            array_content_info = json_obj["array"]
            content_id = self.__add_content(str_open_id, str_nike_name, str_avatar_url, str_remark, str_phone_number,
                                            array_content_info)
            return content_id
        except Exception as e:
            print("json 格式错误 或者数据字段缺少 错误", e)
            return None

    def __add_content(self, str_open_id, str_nike_name, str_avatar_url, str_remark, str_phone_number,
                      array_content_info):
        if not self.connect_open():
            print("数据库链接错误")
            return None
        cursor = self._cnx.cursor()

        now_datetime = datetime.now()

        add_content_index = (
            "INSERT INTO content_index"
            "(c_open_id, c_nike_name, c_avatar_url, c_remark, c_phone_number,t_modify_time,t_creation_time) "
            "VALUES( %s, %s, %s, %s, %s, %s,%s);")

        data_content_index = (
            str_open_id, str_nike_name, str_avatar_url, str_remark, str_phone_number, now_datetime, now_datetime)

        cursor.execute(add_content_index, data_content_index)

        content_id = cursor.lastrowid

        add_content_info = 'INSERT INTO content_info (c_open_id,i_content_id,c_phone_type,c_phone_number,t_modify_time,t_creation_time) VALUES(%s,%s,%s,%s,%s,%s);'

        data_content_info_list = []
        for item in array_content_info:
            data = (str_open_id, content_id, item["phone_type"], item["phone_number"], now_datetime, now_datetime)
            data_content_info_list += [data]

        cursor.executemany(add_content_info, data_content_info_list)

        self._cnx.commit()
        cursor.close()
        self._cnx.close()
        return content_id

    # 删除联系人
    def delete_content(self, str_json):
        print("删除联系人", str_json)
        json_obj = json.loads(str_json)
        try:
            content_id = json_obj["content_id"]
            # print(type(content_id))
            num_content_id = int(content_id)
            # print("删除号码的联系人id", type(num_content_id),num_content_id)
            return self.__delete_content(num_content_id)
        except Exception as e:
            print("json 格式错误 或者数据字段缺少 错误", e)
            return False
        pass

    def __delete_content(self, num_content_index_id):

        if not self.connect_open():
            return False

        cursor = self._cnx.cursor()

        d_content_index_sql = "delete from content_index where id = %d" % (num_content_index_id)
        d_content_info_sql = "delete from content_info where i_content_id = %d" % (num_content_index_id)

        cursor.execute(d_content_index_sql)
        cursor.execute(d_content_info_sql)

        self._cnx.commit()
        cursor.close()
        self._cnx.close()

        return True
    # 重新完成修改部分 都完成新增
    def modify_content_info(self, str_content_info):

        try:
            json_obj = json.loads(str_content_info)
            print("解析修改电话本信息", type(json_obj), json_obj)
            content_id = json_obj["content_id"]
            open_id = json_obj['open_id']
            return self.__modify_content_info(content_id, open_id, json_obj)
        except Exception as e:
            print("出现错误", e)
            return False
        pass

    def __modify_content_info(self, num_content_id, str_open_id, dic_content_info):

        if not self.connect_open():
            return False

        cursor = self._cnx.cursor()
        update_sql = "update content_index set"

        for key, value in dic_content_info.items():
            if key == 'nike_name':
                update_sql += ' c_nike_name = \'%s\',' % value
            if key == 'avatar_url':
                update_sql += ' c_avatar_url = \'%s\',' % value
            if key == 'remark':
                update_sql += ' c_remark = \'%s\',' % value

        len_str = len(update_sql) - 1
        update_sql = update_sql[:len_str]
        # 更新基础信息
        update_sql += " where id = %d;" % num_content_id
        cursor.execute(update_sql)

        phone_numbers = dic_content_info.get("array")

        now_datetime = datetime.now()
        if phone_numbers is not None:
            for item in phone_numbers:
                ot = item['ot']
                if ot == 0:
                    # 增加
                    str_phone_type = item["phone_type"]
                    str_phone_number = item["phone_number"]
                    i_sql = (
                        "insert into content_info(c_open_id, i_content_id, c_phone_type, c_phone_number, t_modify_time, t_creation_time) VALUES(%s, %s, %s, %s, %s, %s);")
                    i_values = (
                        str_open_id, num_content_id, str_phone_type, str_phone_number, now_datetime, now_datetime)
                    cursor.execute(i_sql, i_values)
                    pass
                elif ot == 1:
                    # 修改
                    u_sql = ("update content_info set  c_phone_type = %s , c_phone_number = %s where id = %s;")
                    num_info_id = item["info_id"]
                    str_phone_type = item["phone_type"]
                    str_phone_number = item["phone_number"]
                    u_values = (str_phone_type, str_phone_number, num_info_id)
                    cursor.execute(u_sql, u_values)
                    pass
                elif ot == 2:
                    # 删除
                    num_info_id = item["info_id"]
                    d_sql = "delete from content_info where id = %d;" % num_info_id
                    cursor.execute(d_sql)
                    pass
                else:
                    # 不存在表示 没有 进行修改
                    pass

        cursor.execute(update_sql)

        self._cnx.commit()
        cursor.close()
        self._cnx.close()

        return True



    def content_info_modify(self,str_content_info):
        try:
            json_obj = json.loads(str_content_info)

            num_content_index_id = json_obj["content_id"]

            str_open_id = json_obj["open_id"]
            str_nike_name = json_obj["nike_name"]
            str_avatar_url = json_obj["avatar_url"]
            str_remark = json_obj["remark"]
            str_phone_number = json_obj["array"][0]["phone_number"]
            array_content_info = json_obj["array"]

            content_id = self.__content_info_modify__(str_open_id, str_nike_name, str_avatar_url, str_remark, str_phone_number,
                                            array_content_info,num_content_index_id)
            return content_id
        except Exception as e:
            print("json 格式错误 或者数据字段缺少 错误", e)
            return None
        pass

    def __content_info_modify__(self, str_open_id, str_nike_name, str_avatar_url, str_remark, str_phone_number,
                      array_content_info, num_content_index_id):
        # 删除之前的数据

        if not self.connect_open():
            return False

        cursor = self._cnx.cursor()

        d_content_index_sql = "delete from content_index where id = %d" % (num_content_index_id)
        d_content_info_sql = "delete from content_info where i_content_id = %d" % (num_content_index_id)

        cursor.execute(d_content_index_sql)
        cursor.execute(d_content_info_sql)


        # 新增现在的数据
        now_datetime = datetime.now()

        add_content_index = (
            "INSERT INTO content_index"
            "(c_open_id, c_nike_name, c_avatar_url, c_remark, c_phone_number,t_modify_time,t_creation_time) "
            "VALUES( %s, %s, %s, %s, %s, %s,%s);")

        data_content_index = (
            str_open_id, str_nike_name, str_avatar_url, str_remark, str_phone_number, now_datetime, now_datetime)

        cursor.execute(add_content_index, data_content_index)

        content_id = cursor.lastrowid

        add_content_info = 'INSERT INTO content_info (c_open_id,i_content_id,c_phone_type,c_phone_number,t_modify_time,t_creation_time) VALUES(%s,%s,%s,%s,%s,%s);'

        data_content_info_list = []
        for item in array_content_info:
            data = (str_open_id, content_id, item["phone_type"], item["phone_number"], now_datetime, now_datetime)
            data_content_info_list += [data]

        cursor.executemany(add_content_info, data_content_info_list)

        self._cnx.commit()
        cursor.close()
        self._cnx.close()
        return content_id


        pass

    def connect_open(self):
        try:
            self._cnx = mysql.connector.connect(**self._db_connect_config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print("数据库打开错误",err.msg)
                pass
            return False
        else:
            return True

    def __init__(self):
        print("__init__")

    def __new__(cls, *args, **kwargs):
        print("__new__")
        if not hasattr(db_connect_singleton, "_instance"):
            with db_connect_singleton._instance_lock:
                if not hasattr(db_connect_singleton, "_instance"):
                    db_connect_singleton._instance = object.__new__(cls)
        return db_connect_singleton._instance


if __name__ == '__main__':
    add_content_json = '''
    {
    "open_id": "jkxznjkshdkas",
    "nike_name": "hao帅",
    "avatar_url": "http:daskjhdka",
    "remark":"天下第帅",
    "array": [
        {"phone_type":"住宅","phone_number":"18682435851"},
        {"phone_type":"住宅","phone_number":"18682435851"}
    ]
}
    '''

    m_content_json = '''
    {
    "open_id": "jkxznjkshdkas",
    "content_id": 15,
    "nike_name":"修正",
    "avatar_url": "http:daskjhdka",
    "remark":"天下第帅",
    "array": [
        {"ot":1, "info_id": 1,  "type":"住宅","phone_number":"修改18682435851🙏"},
        {"ot":0, "phone_type":"住宅","phone_number":"添加18682435851"}
    ]
}
    '''

    d_content_json = '''
    {
    "content_id": "23"
    }
'''

    s_content_json = '''
    {
    "open_id": "jkxznjkshdkas"
    }
    '''

    s_content_info_json = '''
    {
    "content_id": 15
    }
    '''

    db_do = db_connect_singleton()
    # 添加号码
    # db_do.add_content(add_content_json)
    # 删除测试
    db_do.delete_content(d_content_json)
    # 测试修改
    # db_do.modify_content_info(m_content_json)
    # 测试获取联系人列表
    # db_do.get_content_index_list(s_content_json)

    # 测试获取联系人信息
    # db_do.get_content_info(s_content_info_json)
    # print("测试完成")


    pass
