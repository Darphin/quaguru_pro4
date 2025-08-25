import logging

import curlify
from requests import Session


class BaseSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.base_url = kwargs.get('base_url', None)

    def get(self, url, **kwargs):
        url = self.base_url + url
        response = super().get( url, **kwargs)
        return response

    def post(self, url, **kwargs):
        url = self.base_url + url
        response = super().post( url, **kwargs)
        return response

    def patch(self, url, **kwargs):
        url = self.base_url + url
        response = super().patch( url, **kwargs)
        return response

    def delete(self, url, **kwargs):
        url = self.base_url + url
        response = super().delete( url, **kwargs)
        return response