import tornado.httpclient

def handle_request(response):
    if response.error:
        print ("Error:", response.error)
    else:
        print (response.body)

# 不能请求成功
def asys_request():
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_client.fetch("http://127.0.0.1:8888/", handle_request)
    pass

def sys_request():
    http_client = tornado.httpclient.HTTPClient()
    try:
        response = http_client.fetch("http://127.0.0.1:8888/")
        # print(response.body)
    except tornado.httpclient.HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        print("Error: " + str(e))
    except Exception as e:
        # Other errors are possible, such as IOError.
        print("Error: " + str(e))
    http_client.close()
    pass


def body_request():
    _request = tornado.httpclient.HTTPRequest(url="http://127.0.0.1:8888/",method="POST",body="我是谁")
    http_client = tornado.httpclient.HTTPClient()
    http_response = http_client.fetch(_request)
    print("结果",http_response.body)

    pass

if __name__ == '__main__':
    # sys_request()
    # asys_request()
    body_request()
    pass