# -*- coding: utf-8 -*-
from django.test import TestCase, RequestFactory

class ViewTestCase(TestCase):
    factory = RequestFactory()

    def get_request(self, user, url=None, **kwargs):
        if url == None:
            url = self.url
        request = self.factory.get(self.url)
        request.user = user
        return self.view(request, url, **kwargs)

    def post_request(self, user, data={}, url=None, **kwargs):
        if url == None:
            url = self.url
        request = self.factory.post(self.url, data)
        request.user = user
        return self.view(request, url, **kwargs)

