# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement

class BaseProjectPage(PageObject):
    logout = PageElement(link_text='LOG OUT')
