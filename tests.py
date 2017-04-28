import unittest
from mock import patch, Mock
from tornado import gen, testing, web, httpclient, httpserver
from code_under_test import MainHandler, callback_example, coroutine_example


class TestTornadoWeb(testing.AsyncHTTPTestCase):
    def get_app(self):
        return web.Application([(r'/', MainHandler)])

    def handle_request(self, response):
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "Hello, world")
        self.stop()

    @testing.gen_test
    def test_with_http_client(self):
        response = yield self.http_client.fetch(self.get_url('/'), self.handle_request)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "Hello, world")

    def test_with_testcase_fetch(self):
        """
        Tornado AsyncHTTPTestCase has it's own .fetch that hits your own server
        and handles the IOloop nonsense for you. Easier than using your own httpclient
        """
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Hello, world')

    @testing.gen_test
    def test_with_existing_callbacky_code(self):
        """
        Sometimes there is existing code that has callbacks and you don't get to
        fix it right now.

        When unittesting, we often test individual functions or smaller bits of code,
        instead of the api endpoints.  Isolating and testing individual components
        helps us figure out exactly where a bug is occuring.
        """
        response = yield gen.Task(callback_example)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '200 OK')

    @testing.gen_test
    def test_with_existing_coroutine(self):
        """
        Sometimes your test has to test an existing coroutine instead of making
        the requests itself.
        """
        response = yield coroutine_example()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '200 OK')

    # Where to patch can be difficult sometimes. This case is straightforward,
    # but it can be tricky. Here's a guide: http://www.voidspace.org.uk/python/mock/patch.html#id1
    @patch("code_under_test.get_http_client")
    @testing.gen_test
    def test_with_existing_coroutine_MOCKED(self, mock_http_client):
        """
        In real code, we don't actually want our tests to hit third party apis
        when we run them.
        - the other people running those websites don't like it, and it could be
         a lot of traffic if we run our tests often.
        - external apis often change or have downtime for reasons other than
        our own code breaking.  You want your tests to have a low false-positive rate,

        So we replace the third party services with our own version that returns
        the same thing every time. That way, we can test that our integration
        does what we want it to do.
        If the third party service breaks, then our that uses it probably will
        break too, but no amount of unit tests that we do will fix that.

        The mock library is genius.
        https://docs.python.org/dev/library/unittest.mock.html
        You can replace any python code in your project with an impostor, that will
        act in a way you define. The mock remembers how it was called, and
        you can write asserts that it was called a certain way. I didn't do that
        here but can make an example if you are interested.
        """

        # This is how we plug our fake fetch function into the one the code under test will
        # use.
        #
        fake_response = gen.Future()
        fake_response.set_result(Mock(code=200, body="200 OK"))
        mock_http_client().fetch.return_value = fake_response

        response = yield coroutine_example()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '200 OK')


if __name__ == '__main__':
    unittest.main()
