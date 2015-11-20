# -*- coding:utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class ActionlistPage(PageObject):
    add_box     = PageElement(name='text')
    add_button  = PageElement(xpath="//form//input[@id='submit-id-submit']")
    thelist     = MultiPageElement(css='#list .full-height')
    error_lists = MultiPageElement(css='.errorlist')
