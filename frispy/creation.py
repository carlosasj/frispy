import requests
from .response import Response


class Creation:
    def __init__(self, title):
        self.title = title

    def get(self, url, params=None, **kwargs):
        res = requests.get(url, params, **kwargs)
        return Response(self.title, res)

    def options(self, url, **kwargs):
        res = requests.options(url, **kwargs)
        return Response(self.title, res)

    def head(self, url, **kwargs):
        res = requests.head(url, **kwargs)
        return Response(self.title, res)

    def post(self, url, data=None, json=None, **kwargs):
        res = requests.post(url, data, json, **kwargs)
        return Response(self.title, res)

    def put(self, url, data=None, **kwargs):
        res = requests.put(url, data, **kwargs)
        return Response(self.title, res)

    def patch(self, url, data=None, **kwargs):
        res = requests.patch(url, data, **kwargs)
        return Response(self.title, res)

    def delete(self, url, **kwargs):
        res = requests.delete(url, **kwargs)
        return Response(self.title, res)
