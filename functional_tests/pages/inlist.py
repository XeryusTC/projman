# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class InlistPage(PageObject):
    add_box = PageElement(name='text')
    thelist = MultiPageElement(xpath="//div[@id='content']//li")
