# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class InlistPage(PageObject):
    add_box     = PageElement(name='text')
    add_button  = PageElement(xpath="//form//button[@type='submit']")
    thelist     = MultiPageElement(xpath="//div[@id='content']//li")
    error_lists = MultiPageElement(css='.errorlist')
