# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class InlistPage(PageObject):
    add_box     = PageElement(name='text')
    add_button  = PageElement(xpath="//form//input[@id='submit-id-submit']")
    thelist     = MultiPageElement(css='#list .full-height')
    listrows    = MultiPageElement(css='#list .mui-row')
    error_lists = MultiPageElement(css='.errorlist')
    delete_item = PageElement(link_text='DELETE', context=True)


class InlistDeletePage(PageObject):
    confirm = PageElement(xpath="//input[@type='submit']")
