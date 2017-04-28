from tornado import gen, web, httpclient


def get_http_client():
    return httpclient.AsyncHTTPClient()


@gen.coroutine
def coroutine_example():
    """
    Pretend this is a real api integration in existing code to some 3rd party service.
    """
    http_client = get_http_client()

    response = yield http_client.fetch('http://mcscope.com/responsecode?code=200')

    raise gen.Return(response)


def callback_example(callback):
    """
    Pretend this is a real api integration in existing code to some 3rd party service.
    This one uses an old gross callback
    """
    http_client = get_http_client()

    http_client.fetch('http://mcscope.com/responsecode?code=200', callback=callback)


class MainHandler(web.RequestHandler):
    def get(self):
        self.write('Hello, world')
